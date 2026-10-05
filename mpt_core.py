#!/usr/bin/env python3
"""
mpt_core.py — Shared engine for the Indian ETF MPT project.

All data download, cleaning, optimization, and metric computation
lives here. Both mpt_indian_etf_analysis.py and mpt_detailed_report.py
import from this module to eliminate code duplication (DRY principle).
"""

import pathlib
import warnings
import datetime

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from scipy.stats import skew, kurtosis

# ── Suppress only known, benign yfinance / pandas FutureWarnings ──────────────
warnings.filterwarnings('ignore', category=FutureWarning, module='yfinance')
warnings.filterwarnings('ignore', category=FutureWarning, module='pandas')
warnings.filterwarnings('ignore', message='.*auto_adjust.*')

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — single source of truth for both scripts
# ─────────────────────────────────────────────────────────────────────────────

# Portable output directory: <project_root>/output/
PROJECT_ROOT = pathlib.Path(__file__).parent
OUTPUT_DIR   = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ✅ India 10-Year G-Sec yield as of 15-Jul-2026 (~6.80%)
# Source: worldgovernmentbonds.com / tradingeconomics.com
RISK_FREE_RATE = 0.068       # 6.80% per annum

TICKERS = [
    'NIFTYBEES.NS',
    'JUNIORBEES.NS',
    'BANKBEES.NS',
    'MID150BEES.NS',
    'MON100.NS',
    'GOLDBEES.NS',
    'SILVERBEES.NS',
    'GSEC10IETF.NS',
    'LIQUIDBEES.NS',
]

BASKET_CLASSIC_5 = [
    'NIFTYBEES.NS', 'JUNIORBEES.NS', 'BANKBEES.NS', 'GOLDBEES.NS', 'LIQUIDBEES.NS'
]
BASKET_ALL_WEATHER_8 = [
    'NIFTYBEES.NS', 'MID150BEES.NS', 'MON100.NS', 'GOLDBEES.NS', 
    'SILVERBEES.NS', 'GSEC10IETF.NS', 'LIQUIDBEES.NS', 'JUNIORBEES.NS'
]
BASKET_EQUITY_ALPHA = [
    'NIFTYBEES.NS', 'JUNIORBEES.NS', 'MID150BEES.NS', 'MON100.NS'
]

BENCHMARK_TICKER = '^NSEI'   # Nifty 50 Total Return proxy

TICKER_NAMES = {
    'NIFTYBEES.NS' : 'Nifty 50 BeES',
    'JUNIORBEES.NS': 'Junior BeES (Next 50)',
    'BANKBEES.NS'  : 'Bank BeES',
    'MID150BEES.NS': 'Midcap 150 BeES',
    'MON100.NS'    : 'Motilal Nasdaq 100',
    'GOLDBEES.NS'  : 'Gold BeES',
    'SILVERBEES.NS': 'Silver BeES',
    'GSEC10IETF.NS': '10-Yr G-Sec ETF',
    'LIQUIDBEES.NS': 'Liquid BeES',
}
SHORT_NAMES = {
    'NIFTYBEES.NS' : 'NiftyBees',
    'JUNIORBEES.NS': 'JuniorBees',
    'BANKBEES.NS'  : 'BankBees',
    'MID150BEES.NS': 'Mid150Bees',
    'MON100.NS'    : 'Nasdaq100',
    'GOLDBEES.NS'  : 'GoldBees',
    'SILVERBEES.NS': 'SilverBees',
    'GSEC10IETF.NS': 'GSec10Yr',
    'LIQUIDBEES.NS': 'LiquidBees',
}
DESC = {
    'NIFTYBEES.NS' : "Tracks Nifty 50 — India's benchmark large-cap index (50 stocks)",
    'JUNIORBEES.NS': 'Tracks Nifty Next 50 — mid-to-large cap segment (50 stocks)',
    'BANKBEES.NS'  : 'Tracks Nifty Bank — top 12 liquid banking stocks',
    'MID150BEES.NS': 'Tracks Nifty Midcap 150 — high growth midcap segment',
    'MON100.NS'    : 'Tracks Nasdaq 100 — US Tech exposure + USD currency hedge',
    'GOLDBEES.NS'  : 'Physical gold ETF — tracks domestic gold spot price',
    'SILVERBEES.NS': 'Physical silver ETF — industrial commodity exposure',
    'GSEC10IETF.NS': 'Tracks 10-Yr Sovereign Govt Bonds — long-duration fixed income',
    'LIQUIDBEES.NS': 'Overnight liquid fund — near-zero risk, money-market returns',
}

START_DATE    = '2019-01-01'
END_DATE      = datetime.date.today().strftime('%Y-%m-%d')
REPORT_DATE   = datetime.date.today().strftime('%d %B %Y')

MAX_WEIGHT    = 0.45    # 45% cap per asset
N_MC          = 10_000  # Monte Carlo portfolios
TRADING_DAYS  = 252
RAW_RETURN_THRESHOLD = 0.15   # flag |daily return| > 15% as artifact

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — DATA DOWNLOAD & CLEANING
# ─────────────────────────────────────────────────────────────────────────────

def download_and_clean(tickers=TICKERS, start=START_DATE, end=END_DATE,
                       threshold=RAW_RETURN_THRESHOLD, verbose=True):
    """
    Download adjusted closing prices from Yahoo Finance for the given tickers,
    detect and linearly interpolate split/corporate-action artifacts, and
    return a clean DataFrame of prices.

    Args:
        tickers (list[str]): Yahoo Finance ticker symbols.
        start   (str): Start date in 'YYYY-MM-DD' format.
        end     (str): End date in 'YYYY-MM-DD' format.
        threshold (float): Single-day |return| above this value is flagged as artifact.
        verbose (bool): Print progress messages.

    Returns:
        pd.DataFrame: Clean daily adjusted closing prices, one column per ticker.
        list[str]:    List of successfully downloaded tickers (column names).
        dict:         cleaned_dates — {ticker: [list of cleaned date strings]}.
    """
    if verbose:
        print("📥  Downloading historical price data from Yahoo Finance …")

    raw = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=verbose,
        group_by='column',
    )

    # Handle both MultiIndex (multi-ticker) and flat (single-ticker) column formats
    if isinstance(raw.columns, pd.MultiIndex):
        if 'Close' in raw.columns.get_level_values(0):
            prices = raw['Close'].copy()
        else:
            raise KeyError("No 'Close' level found in downloaded data.")
    else:
        prices = raw.copy()

    # Normalise column names to uppercase
    prices.columns = [c.upper() for c in prices.columns]

    # Drop completely empty rows, forward-fill minor holiday gaps
    prices.dropna(how='all', inplace=True)
    prices.ffill(inplace=True)
    prices.dropna(inplace=True)

    # ── Identify available tickers ────────────────────────────────────────────
    available = [t for t in tickers if t.upper() in prices.columns
                 and not prices[t.upper()].isna().all()]
    prices = prices[[t.upper() for t in available]].copy()

    if verbose and len(available) < len(tickers):
        missing = [t for t in tickers if t not in available]
        print(f"  ⚠️   {len(missing)} ticker(s) unavailable: {missing}")

    # ── Clean split / corporate-action price discontinuities ─────────────────
    # Yahoo Finance can produce multi-day price jumps around stock splits
    # (e.g., NIFTYBEES/BANKBEES/GOLDBEES 1:10 split in Dec 2019).
    # Strategy: NaN the bad price AND the price before it (which causes the
    # bad return), then restore via linear time interpolation.
    prices_c = prices.copy().astype(float)
    cleaned_dates = {}

    for col in prices_c.columns:
        chk     = prices_c[col].pct_change()
        bad_idx = chk.index[chk.abs() > threshold].tolist()
        if bad_idx:
            nan_set = set()
            for bad_dt in bad_idx:
                pos = prices_c.index.get_loc(bad_dt)
                if pos > 0:
                    nan_set.add(prices_c.index[pos - 1])
                nan_set.add(bad_dt)
            prices_c.loc[sorted(nan_set), col] = np.nan
            cleaned_dates[col] = sorted([str(d.date()) for d in nan_set])
            if verbose:
                print(f"  ⚠️   {col}: cleaned artifacts on {cleaned_dates[col]}")

    prices_c = prices_c.interpolate(method='time', limit=10)
    prices_c.ffill(inplace=True)
    prices_c.bfill(inplace=True)

    # Verify cleaning
    verify_ret = prices_c.pct_change()
    still_bad  = verify_ret.abs() > threshold
    if still_bad.any().any():
        count = int(still_bad.sum().sum())
        if verbose:
            print(f"  ⚠️   {count} artifact(s) could not be cleaned automatically.")
    else:
        if verbose:
            print("  ✓ All data artifacts cleaned successfully.")

    return prices_c, available, cleaned_dates


def download_benchmark(start=START_DATE, end=END_DATE, verbose=False):
    """
    Download Nifty 50 index (^NSEI) as a market benchmark.

    Returns:
        pd.Series: Daily benchmark price series (or None if download fails).
    """
    try:
        raw = yf.download(BENCHMARK_TICKER, start=start, end=end,
                          auto_adjust=True, progress=verbose)
        if isinstance(raw.columns, pd.MultiIndex):
            bm = raw['Close'].iloc[:, 0]
        else:
            bm = raw['Close'] if 'Close' in raw.columns else raw.iloc[:, 0]
        bm = bm.dropna()
        if verbose:
            print(f"  ✓ Benchmark downloaded: {len(bm)} days ({BENCHMARK_TICKER})")
        return bm
    except Exception as e:
        if verbose:
            print(f"  ⚠️   Benchmark download failed ({e}). Continuing without it.")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — RETURNS & STATISTICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_returns(prices):
    """
    Compute annualised expected returns, covariance, and correlation matrices.

    Args:
        prices (pd.DataFrame): Clean daily price DataFrame.

    Returns:
        tuple: (daily_returns, mu, Sigma, corr)
            - daily_returns: daily % change DataFrame
            - mu:    np.ndarray of annualised expected returns
            - Sigma: np.ndarray annualised covariance matrix
            - corr:  pd.DataFrame correlation matrix
    """
    daily  = prices.pct_change().dropna()
    mu_s   = daily.mean() * TRADING_DAYS
    cov_s  = daily.cov()  * TRADING_DAYS
    corr   = daily.corr()
    return daily, mu_s.values, cov_s.values, corr


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — PORTFOLIO MATH
# ─────────────────────────────────────────────────────────────────────────────

def port_return(w, mu):
    """Weighted portfolio return."""
    return float(np.dot(w, mu))


def port_vol(w, Sigma):
    """Portfolio standard deviation (volatility)."""
    return float(np.sqrt(w @ Sigma @ w))


def port_sharpe(w, mu, Sigma, rf=RISK_FREE_RATE):
    """Annualised Sharpe ratio."""
    v = port_vol(w, Sigma)
    return (port_return(w, mu) - rf) / v if v > 1e-10 else 0.0


def port_sortino(w, mu, daily_returns, tickers, rf=RISK_FREE_RATE):
    """
    Sortino ratio — like Sharpe but penalises only downside volatility.
    Better measure for assets with skewed return distributions (e.g. Gold).

    Args:
        w (np.ndarray): Portfolio weights.
        mu (np.ndarray): Annualised expected returns.
        daily_returns (pd.DataFrame): Daily return DataFrame.
        tickers (list): Ticker column names matching w order.
        rf (float): Risk-free rate.

    Returns:
        float: Annualised Sortino ratio.
    """
    port_daily = daily_returns[tickers].dot(pd.Series(w, index=tickers))
    downside   = port_daily[port_daily < 0]
    if len(downside) < 2:
        return 0.0
    downside_vol = downside.std() * np.sqrt(TRADING_DAYS)
    ann_ret      = port_return(w, mu)
    return (ann_ret - rf) / downside_vol if downside_vol > 1e-10 else 0.0


def port_calmar(ann_return, max_drawdown_value):
    """
    Calmar ratio — annualised return divided by maximum drawdown.
    Used by hedge funds to assess drawdown-adjusted performance.

    Args:
        ann_return (float): Annualised portfolio return.
        max_drawdown_value (float): Max drawdown (negative number, e.g. -0.25).

    Returns:
        float: Calmar ratio (positive is better).
    """
    mdd = abs(max_drawdown_value)
    return ann_return / mdd if mdd > 1e-10 else 0.0


def max_drawdown(price_series):
    """
    Maximum peak-to-trough drawdown of a price or cumulative-return series.

    Returns:
        float: Maximum drawdown (negative value, e.g. -0.32 means -32%).
    """
    cum      = (1 + price_series.pct_change().dropna()).cumprod()
    roll_max = cum.cummax()
    dd       = (cum - roll_max) / roll_max
    return float(dd.min())


def portfolio_drawdown(w_vec, daily_returns, tickers):
    """
    Time-series of portfolio drawdown given weight vector.

    Returns:
        pd.Series: Drawdown series (values <= 0).
    """
    pret = daily_returns[tickers].dot(pd.Series(w_vec, index=tickers))
    cum  = (1 + pret).cumprod()
    return (cum - cum.cummax()) / cum.cummax()


def cvar_95(daily_return_series):
    """
    Conditional Value-at-Risk (CVaR) at 95% confidence — the average daily
    loss in the worst 5% of trading days. Also called Expected Shortfall.

    Returns:
        float: CVaR (negative value represents a loss).
    """
    threshold = np.percentile(daily_return_series, 5)
    tail      = daily_return_series[daily_return_series <= threshold]
    return float(tail.mean()) if len(tail) > 0 else float(threshold)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — PORTFOLIO OPTIMIZATION
# ─────────────────────────────────────────────────────────────────────────────

def _clean_w(w):
    """Zero-out numerical noise and re-normalise weights."""
    w[w < 1e-5] = 0.0
    w /= w.sum()
    return w


def optimize_portfolios(mu, Sigma, n, rf=RISK_FREE_RATE,
                        max_weight=MAX_WEIGHT, verbose=True):
    """
    Compute Max Sharpe and Min Volatility portfolio weights using SLSQP.

    Args:
        mu (np.ndarray):    Annualised expected returns vector (length n).
        Sigma (np.ndarray): Annualised covariance matrix (n × n).
        n (int):            Number of assets.
        rf (float):         Risk-free rate.
        max_weight (float): Maximum weight per asset (e.g. 0.45).
        verbose (bool):     Print convergence status.

    Returns:
        dict with keys:
            'w_sharpe', 'w_minvol', 'w_equal',
            'res_sh', 'res_mv'
    """
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds      = tuple((0.0, max_weight) for _ in range(n))
    w0          = np.array([1 / n] * n)

    # ── Max Sharpe ────────────────────────────────────────────────────────────
    def neg_sharpe(w):
        v = port_vol(w, Sigma)
        return -(port_return(w, mu) - rf) / v if v > 1e-10 else 0.0

    res_sh = minimize(neg_sharpe, w0, method='SLSQP',
                      bounds=bounds, constraints=constraints,
                      options={'maxiter': 3000, 'ftol': 1e-12})

    # ── Min Volatility ────────────────────────────────────────────────────────
    res_mv = minimize(lambda w: port_vol(w, Sigma), w0, method='SLSQP',
                      bounds=bounds, constraints=constraints,
                      options={'maxiter': 3000, 'ftol': 1e-12})

    w_sh = _clean_w(res_sh.x if res_sh.success else w0.copy())
    w_mv = _clean_w(res_mv.x if res_mv.success else w0.copy())
    w_eq = _clean_w(w0.copy())

    if verbose:
        sh_status = "✓ Converged" if res_sh.success else "⚠️  Did not converge"
        mv_status = "✓ Converged" if res_mv.success else "⚠️  Did not converge"
        print(f"  Max Sharpe optimizer : {sh_status}")
        print(f"  Min Vol optimizer    : {mv_status}")

    return {
        'w_sharpe': w_sh,
        'w_minvol': w_mv,
        'w_equal' : w_eq,
        'res_sh'  : res_sh,
        'res_mv'  : res_mv,
    }


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — MONTE CARLO SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

def run_monte_carlo(mu, Sigma, n, n_mc=N_MC, max_weight=MAX_WEIGHT,
                    rf=RISK_FREE_RATE, seed=42):
    """
    Simulate n_mc random portfolios using Dirichlet sampling with a
    max_weight clip (note: this introduces a mild boundary-sampling bias;
    portfolios near the weight cap are slightly underrepresented).

    Args:
        mu (np.ndarray): Annualised expected returns.
        Sigma (np.ndarray): Annualised covariance matrix.
        n (int): Number of assets.
        n_mc (int): Number of Monte Carlo portfolios.
        max_weight (float): Maximum weight per asset.
        rf (float): Risk-free rate for Sharpe calculation.
        seed (int): Random seed for reproducibility.

    Returns:
        dict with keys: 'returns', 'vols', 'sharpes', 'weights', 'best_idx'
    """
    np.random.seed(seed)
    mc_r  = np.zeros(n_mc)
    mc_v  = np.zeros(n_mc)
    mc_sr = np.zeros(n_mc)
    mc_w  = np.zeros((n_mc, n))

    for i in range(n_mc):
        # Iterative clip + renormalize until all weights respect the cap.
        # Plain clip-once + renormalize can violate the cap when n is small
        # because renormalization can push a weight back above max_weight.
        w = np.random.dirichlet(np.ones(n))
        for _ in range(20):   # converges in < 5 iterations for typical inputs
            w = np.clip(w, 0.0, max_weight)
            s = w.sum()
            if s < 1e-10:
                w = np.ones(n) / n
                break
            w = w / s
            if w.max() <= max_weight + 1e-9:
                break
        mc_w[i] = w

        r       = port_return(w, mu)
        v       = port_vol(w, Sigma)
        mc_r[i]  = r
        mc_v[i]  = v
        mc_sr[i] = (r - rf) / v if v > 1e-10 else 0.0

    return {
        'returns' : mc_r,
        'vols'    : mc_v,
        'sharpes' : mc_sr,
        'weights' : mc_w,
        'best_idx': int(np.argmax(mc_sr)),
    }


# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 — COMPREHENSIVE ASSET STATISTICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_asset_stats(prices, daily_returns, mu_s, cov_s, rf=RISK_FREE_RATE):
    """
    Compute a comprehensive statistics dictionary for each ETF, including
    Sortino ratio, Calmar ratio, and CVaR (Expected Shortfall at 95%).

    Args:
        prices (pd.DataFrame): Clean price DataFrame.
        daily_returns (pd.DataFrame): Daily % change DataFrame.
        mu_s (pd.Series): Annualised expected returns (indexed by ticker).
        cov_s (pd.DataFrame): Annualised covariance matrix.
        rf (float): Risk-free rate.

    Returns:
        dict: {ticker: {metric: value, ...}}
    """
    stats = {}
    for t in prices.columns:
        dr   = daily_returns[t].dropna()
        mdd  = max_drawdown(prices[t])
        ann  = float(mu_s[t]) if hasattr(mu_s, '__getitem__') else float(mu_s)
        vol  = float(np.sqrt(cov_s.loc[t, t]))

        # Downside volatility (for Sortino)
        down = dr[dr < 0]
        down_vol = float(down.std() * np.sqrt(TRADING_DAYS)) if len(down) > 1 else 1e-10

        stats[t] = {
            'ann_ret'   : ann,
            'ann_vol'   : vol,
            'sharpe'    : (ann - rf) / vol if vol > 1e-10 else 0.0,
            'sortino'   : (ann - rf) / down_vol if down_vol > 1e-10 else 0.0,
            'calmar'    : port_calmar(ann, mdd),
            'cvar_95'   : cvar_95(dr),           # daily CVaR (95%)
            'max_dd'    : mdd,
            'skew'      : float(skew(dr)),
            'kurt'      : float(kurtosis(dr)),    # excess kurtosis
            'best_day'  : float(dr.max()),
            'worst_day' : float(dr.min()),
            'total_ret' : float((prices[t].iloc[-1] / prices[t].iloc[0]) - 1),
        }
    return stats


# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 — TIME SERIES & ECONOMETRICS (v2.0)
# ─────────────────────────────────────────────────────────────────────────────

def compute_rolling_metrics(daily_returns, window=252):
    """
    Computes rolling annualized return and volatility for regime shift analysis.
    """
    roll_ret = daily_returns.rolling(window).mean() * TRADING_DAYS
    roll_vol = daily_returns.rolling(window).std() * np.sqrt(TRADING_DAYS)
    return roll_ret, roll_vol

def compute_ewma_volatility(daily_returns, lambda_decay=0.94):
    """
    Computes RiskMetrics™ EWMA (Exponentially Weighted Moving Average) Volatility.
    Captures volatility clustering (ARCH effect) common in financial time series.
    """
    ewma_var = daily_returns.ewm(alpha=(1 - lambda_decay)).var()
    ewma_vol = np.sqrt(ewma_var) * np.sqrt(TRADING_DAYS)
    return ewma_vol

def run_backtest_rebalancing(daily_returns, target_weights, tickers, frequency='QE'):
    """
    Simulates a walk-forward portfolio that rebalances to target_weights 
    at the specified frequency (e.g., 'QE' for Quarter-End).
    """
    w = pd.Series(target_weights, index=tickers)
    
    # Identify rebalance dates (last trading day of the frequency period)
    rebal_dates = set(daily_returns.resample(frequency).last().dropna(how='all').index)
    
    port_vals = []
    current_buckets = 100.0 * w
    
    for date, ret in daily_returns[tickers].iterrows():
        # EOD bucket values
        current_buckets = current_buckets * (1 + ret)
        eod_value = current_buckets.sum()
        port_vals.append(eod_value)
        
        # If today is a rebalance date, redistribute the EOD value across target weights
        if date in rebal_dates:
            current_buckets = eod_value * w
            
    return pd.Series(port_vals, index=daily_returns.index)

def stress_test_drawdowns(portfolio_growth_series):
    """
    Evaluates portfolio performance during known historical crisis windows.
    Returns a dict with max drawdowns and returns during those specific periods.
    """
    crises = {
        'COVID-19 Crash (Feb-Apr 2020)': ('2020-02-19', '2020-04-15'),
        'Rate Hike Tech Shock (Jan-Oct 2022)': ('2022-01-03', '2022-10-21'),
        'Election Volatility (Jun 2024)': ('2024-06-03', '2024-06-05')
    }
    
    results = {}
    # Convert index to timezone-naive for safe string slicing if it's tz-aware
    idx = portfolio_growth_series.index
    if idx.tz is not None:
        safe_series = portfolio_growth_series.copy()
        safe_series.index = safe_series.index.tz_localize(None)
    else:
        safe_series = portfolio_growth_series

    for name, (start, end) in crises.items():
        try:
            window = safe_series.loc[start:end]
            if len(window) > 2:
                peak = window.cummax()
                drawdown = (window - peak) / peak
                max_dd = drawdown.min()
                total_ret = (window.iloc[-1] / window.iloc[0]) - 1
                results[name] = {'max_drawdown': float(max_dd), 'total_return': float(total_ret)}
        except Exception:
            pass # Data might not cover this period
            
    return results


# ─────────────────────────────────────────────────────────────────────────────
# STEP 8 — PORTFOLIO PERFORMANCE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def portfolio_metrics(w, mu, Sigma, daily_returns, tickers, rf=RISK_FREE_RATE):
    """
    Compute full performance metrics for a single portfolio weight vector.

    Returns:
        dict: Return, volatility, Sharpe, Sortino, max drawdown, Calmar, CVaR
    """
    r    = port_return(w, mu)
    v    = port_vol(w, Sigma)
    sr   = (r - rf) / v if v > 1e-10 else 0.0
    dd_s = portfolio_drawdown(w, daily_returns, tickers)
    mdd  = float(dd_s.min())

    port_daily = daily_returns[tickers].dot(pd.Series(w, index=tickers))
    down       = port_daily[port_daily < 0]
    down_vol   = float(down.std() * np.sqrt(TRADING_DAYS)) if len(down) > 1 else 1e-10
    sortino    = (r - rf) / down_vol if down_vol > 1e-10 else 0.0
    calmar     = port_calmar(r, mdd)
    cv         = cvar_95(port_daily)

    return {
        'return'  : r,
        'vol'     : v,
        'sharpe'  : sr,
        'sortino' : sortino,
        'calmar'  : calmar,
        'max_dd'  : mdd,
        'cvar_95' : cv,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CONVENIENCE: full pipeline in one call
# ─────────────────────────────────────────────────────────────────────────────

def run_full_pipeline(verbose=True):
    """
    Execute the complete MPT pipeline and return all results in one dict.

    Returns a dict with keys:
        prices, available, cleaned_dates, benchmark,
        daily, mu_series, cov_series, corr, mu, Sigma,
        roll_ret, roll_vol,
        opts (dict of weights + res),
        mc (Monte Carlo results),
        asset_stats,
        port_metrics (dict: 'sharpe', 'minvol', 'equal'),
        port_growth (dict: 'sharpe', 'minvol', 'equal', 'benchmark'),
        drawdowns (dict: 'sharpe', 'minvol', 'equal'),
        meta (dates, counts)
    """
    # 1. Data
    prices, available, cleaned_dates = download_and_clean(verbose=verbose)
    benchmark = download_benchmark(verbose=verbose)
    tickers   = available   # column names are uppercase tickers

    # 2. Returns
    daily_r, mu, Sigma, corr = compute_returns(prices)
    mu_s  = pd.Series(mu,  index=tickers)
    cov_s = pd.DataFrame(Sigma, index=tickers, columns=tickers)

    # Rolling windows
    daily_df = prices.pct_change().dropna()
    roll_ret  = daily_df.rolling(252).mean() * 252
    roll_vol  = daily_df.rolling(252).std()  * np.sqrt(252)

    # 3. Optimization
    opts = optimize_portfolios(mu, Sigma, len(tickers), verbose=verbose)
    w_sh, w_mv, w_eq = opts['w_sharpe'], opts['w_minvol'], opts['w_equal']

    # 4. Monte Carlo
    mc = run_monte_carlo(mu, Sigma, len(tickers))

    # 5. Asset stats (includes Sortino, Calmar, CVaR)
    asset_stats = compute_asset_stats(prices, daily_df, mu_s, cov_s)

    # 6. Portfolio-level metrics
    pm = {}
    for name, w in [('sharpe', w_sh), ('minvol', w_mv), ('equal', w_eq)]:
        pm[name] = portfolio_metrics(w, mu, Sigma, daily_df, tickers)

    # 7. Cumulative growth (₹100 invested)
    cum_g = (1 + daily_df).cumprod() * 100
    pg = {}
    for name, w in [('sharpe', w_sh), ('minvol', w_mv), ('equal', w_eq)]:
        pg[name] = (1 + daily_df[tickers].dot(pd.Series(w, index=tickers))).cumprod() * 100

    # Benchmark growth (aligned dates)
    if benchmark is not None:
        bm_daily = benchmark.pct_change().dropna()
        bm_daily = bm_daily.reindex(daily_df.index).dropna()
        pg['benchmark'] = (1 + bm_daily).cumprod() * 100
    else:
        pg['benchmark'] = None

    # 8. Drawdowns
    dds = {}
    for name, w in [('sharpe', w_sh), ('minvol', w_mv), ('equal', w_eq)]:
        dds[name] = portfolio_drawdown(w, daily_df, tickers)

    meta = {
        'actual_start': prices.index[0].strftime('%Y-%m-%d'),
        'actual_end'  : prices.index[-1].strftime('%Y-%m-%d'),
        'n_days'      : len(prices),
        'n_assets'    : len(tickers),
    }

    return {
        'prices'       : prices,
        'available'    : available,
        'cleaned_dates': cleaned_dates,
        'benchmark_px' : benchmark,
        'daily'        : daily_df,
        'mu_series'    : mu_s,
        'cov_series'   : cov_s,
        'corr'         : corr,
        'mu'           : mu,
        'Sigma'        : Sigma,
        'roll_ret'     : roll_ret,
        'roll_vol'     : roll_vol,
        'opts'         : opts,
        'mc'           : mc,
        'asset_stats'  : asset_stats,
        'port_metrics' : pm,
        'port_growth'  : pg,
        'drawdowns'    : dds,
        'cum_g'        : cum_g,
        'meta'         : meta,
    }
