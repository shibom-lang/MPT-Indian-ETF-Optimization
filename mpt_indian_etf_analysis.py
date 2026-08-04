#!/usr/bin/env python3
"""
Portfolio Optimization with Modern Portfolio Theory (MPT)
Indian NSE-Listed Index ETFs Analysis
Date: 2026-07-15  |  Risk-Free Rate: India 10-Yr G-Sec ~6.80%
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving files
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import yfinance as yf
from scipy.optimize import minimize
import warnings
import os
import datetime
import sys

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
OUTPUT_DIR = "/Users/surajitdas/untitled folder 5"

# ✅ India 10-Year G-Sec yield as of 15-Jul-2026 (~6.80%)
# Source: worldgovernmentbonds.com / tradingeconomics.com
RISK_FREE_RATE = 0.068   # 6.80% per annum

TICKERS = [
    'NIFTYBEES.NS',
    'JUNIORBEES.NS',
    'BANKBEES.NS',
    'GOLDBEES.NS',
    'LIQUIDBEES.NS',
]
TICKER_NAMES = {
    'NIFTYBEES.NS': 'Nifty 50 BeES',
    'JUNIORBEES.NS': 'Junior BeES\n(Next 50)',
    'BANKBEES.NS': 'Bank BeES',
    'GOLDBEES.NS': 'Gold BeES',
    'LIQUIDBEES.NS': 'Liquid BeES',
}
SHORT_NAMES = {
    'NIFTYBEES.NS': 'NiftyBees',
    'JUNIORBEES.NS': 'JuniorBees',
    'BANKBEES.NS': 'BankBees',
    'GOLDBEES.NS': 'GoldBees',
    'LIQUIDBEES.NS': 'LiquidBees',
}

START_DATE  = '2019-01-01'
END_DATE    = datetime.date.today().strftime('%Y-%m-%d')

MAX_WEIGHT  = 0.45   # 45% cap per asset
N_MC        = 10_000  # Monte Carlo portfolios
TRADING_DAYS = 252

# Color palette (vibrant, dark-mode friendly)
PALETTE     = ['#00D4FF', '#FF6B6B', '#FFD93D', '#6BCB77', '#C77DFF']
BG_COLOR    = '#0D1117'
CARD_COLOR  = '#161B22'
TEXT_COLOR  = '#E6EDF3'
ACCENT      = '#58A6FF'

print("=" * 65)
print("  INDIAN ETF PORTFOLIO OPTIMIZER — MPT ANALYSIS")
print(f"  Date range : {START_DATE}  →  {END_DATE}")
print(f"  Risk-Free  : {RISK_FREE_RATE:.2%}  (India 10-Yr G-Sec, Jul-2026)")
print(f"  Max weight : {MAX_WEIGHT:.0%} per asset")
print("=" * 65)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: DOWNLOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
print("\n📥  Downloading historical price data from Yahoo Finance …")

raw = yf.download(
    TICKERS,
    start=START_DATE,
    end=END_DATE,
    auto_adjust=True,       # returns 'Close' already split/dividend-adjusted
    progress=True,
    group_by='column',
)

# Extract 'Close' prices — works with both new and legacy yfinance column layouts
if isinstance(raw.columns, pd.MultiIndex):
    if 'Close' in raw.columns.get_level_values(0):
        prices = raw['Close'].copy()
    else:
        raise KeyError("No 'Close' level found in downloaded data.")
else:
    prices = raw.copy()

prices.columns = prices.columns.str.upper() if hasattr(prices.columns, 'str') else prices.columns

# ── Ticker health-check ──────────────────────────────────────────────────────
ALTERNATIVES = {
    'NIFTYBEES.NS' : 'NIFTYBEES.NS  (try NIFTYBEES.BO if .NS fails)',
    'JUNIORBEES.NS': 'JUNIORBEES.NS (try SETFNN50.NS — Nifty Next 50 ETF)',
    'BANKBEES.NS'  : 'BANKBEES.NS   (try BANKBEES.BO if .NS fails)',
    'GOLDBEES.NS'  : 'GOLDBEES.NS   (try GOLDBEES.BO if .NS fails)',
    'LIQUIDBEES.NS': 'LIQUIDBEES.NS (try LIQUIDBEES.BO if .NS fails)',
}

missing_tickers = []
downloaded_tickers = list(prices.columns)

for ticker in TICKERS:
    col = ticker.upper()
    if col not in downloaded_tickers or prices[col].isna().all():
        print(f"\n  ⚠️  TICKER FAILED: {ticker}")
        print(f"      → Suggestion: {ALTERNATIVES.get(ticker, 'No suggestion available')}")
        missing_tickers.append(ticker)

if missing_tickers:
    print(f"\n  ❌  {len(missing_tickers)} ticker(s) could not be downloaded.")
    print("      Proceeding with available tickers only.\n")

# Keep only successfully downloaded tickers
available_tickers = [t.upper() for t in TICKERS if t.upper() in downloaded_tickers and not prices[t.upper()].isna().all()]
prices = prices[available_tickers].copy()

# ── Handle LIQUIDBEES — it trades near ₹1,000 (stable NAV) ──────────────────
# Identify any ticker with essentially zero variance (liquid/money-market fund)
returns_check = prices.pct_change().dropna()
zero_vol_cols = [c for c in returns_check.columns if returns_check[c].std() < 0.0005]
if zero_vol_cols:
    print(f"  ℹ️   Near-zero volatility detected for: {zero_vol_cols}")
    print("      These are liquid / money-market ETFs — included as cash-like asset.\n")

prices.dropna(how='all', inplace=True)
prices.ffill(inplace=True)    # forward-fill minor gaps (holidays, halts)
prices.dropna(inplace=True)   # drop any remaining NaN rows

# ── Clean split / corporate-action artifacts ─────────────────────────────────
# Yahoo Finance has 2-day price discontinuities around NSE stock splits
# (e.g., NIFTYBEES/BANKBEES/GOLDBEES 1:10 split in Dec 2019).
# The bad price causes TWO bad returns: the day the price is bad, AND the
# following day (return from bad_price -> next_good_price).
# Fix: detect |return| > 15% and NaN both the bad price AND the next price,
# then interpolate linearly to restore a smooth continuous price series.
RAW_RETURN_THRESHOLD = 0.15   # flag any single-day move beyond ±15%

prices_clean = prices.copy().astype(float)

for col in prices_clean.columns:
    chk = prices_clean[col].pct_change()
    bad_idx = chk.index[chk.abs() > RAW_RETURN_THRESHOLD].tolist()
    if bad_idx:
        dates_to_nan = set()
        for bad_dt in bad_idx:
            pos = prices_clean.index.get_loc(bad_dt)
            # NaN the bad price itself and the price BEFORE it (causing the bad return)
            if pos > 0:
                dates_to_nan.add(prices_clean.index[pos - 1])
            dates_to_nan.add(bad_dt)
        print(f"  ⚠️   {col}: cleaning {sorted([str(d.date()) for d in dates_to_nan])}")
        prices_clean.loc[sorted(dates_to_nan), col] = np.nan

# Linearly interpolate the cleaned gaps, then ffill/bfill any edge NaNs
prices_clean = prices_clean.interpolate(method='time', limit=10)
prices_clean.ffill(inplace=True)
prices_clean.bfill(inplace=True)
prices = prices_clean

# Verify cleaning worked
verify_ret = prices.pct_change()
still_bad = verify_ret.abs() > RAW_RETURN_THRESHOLD
if still_bad.any().any():
    print(f"  ⚠️   Warning: {still_bad.sum().sum()} data artifact(s) could not be cleaned automatically.")
else:
    print("  ✓ All data-artifact rows cleaned successfully.\n")

actual_start = prices.index[0].strftime('%Y-%m-%d')
actual_end   = prices.index[-1].strftime('%Y-%m-%d')
n_days       = len(prices)

print(f"\n  ✅  Download complete!")
print(f"      Tickers in use : {available_tickers}")
print(f"      Date range used: {actual_start}  →  {actual_end}")
print(f"      Trading days   : {n_days}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: RETURNS & STATISTICS
# ─────────────────────────────────────────────────────────────────────────────
print("\n📊  Calculating returns and covariance matrix …")

daily_returns = prices.pct_change().dropna()
mean_returns  = daily_returns.mean() * TRADING_DAYS   # annualised
cov_matrix    = daily_returns.cov() * TRADING_DAYS    # annualised
corr_matrix   = daily_returns.corr()

n_assets = len(available_tickers)

print("\n  Annualised Expected Returns:")
for t in available_tickers:
    name = SHORT_NAMES.get(t + '.NS' if not t.endswith('.NS') else t, t)
    name = SHORT_NAMES.get(t, SHORT_NAMES.get(t.replace('.NS', '') + '.NS', t))
    print(f"    {name:14s}  {mean_returns[t]:>8.2%}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: PORTFOLIO PERFORMANCE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def port_return(w, mu):
    return float(np.dot(w, mu))

def port_vol(w, Sigma):
    return float(np.sqrt(w @ Sigma @ w))

def port_sharpe(w, mu, Sigma, rf=RISK_FREE_RATE):
    vol = port_vol(w, Sigma)
    return (port_return(w, mu) - rf) / vol if vol > 1e-10 else 0.0

def neg_sharpe(w, mu, Sigma, rf=RISK_FREE_RATE):
    return -port_sharpe(w, mu, Sigma, rf)

def min_vol_obj(w, Sigma):
    return port_vol(w, Sigma)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: OPTIMIZATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n🚀  Optimizing portfolios …")

mu    = mean_returns.values
Sigma = cov_matrix.values

constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
bounds      = tuple((0.0, MAX_WEIGHT) for _ in range(n_assets))
w0          = np.array([1 / n_assets] * n_assets)

# ── Max Sharpe ───────────────────────────────────────────────────────────────
res_sharpe = minimize(
    neg_sharpe, w0,
    args=(mu, Sigma, RISK_FREE_RATE),
    method='SLSQP',
    bounds=bounds,
    constraints=constraints,
    options={'maxiter': 2000, 'ftol': 1e-12},
)
w_sharpe = res_sharpe.x if res_sharpe.success else w0.copy()

# ── Min Volatility ───────────────────────────────────────────────────────────
res_minvol = minimize(
    min_vol_obj, w0,
    args=(Sigma,),
    method='SLSQP',
    bounds=bounds,
    constraints=constraints,
    options={'maxiter': 2000, 'ftol': 1e-12},
)
w_minvol = res_minvol.x if res_minvol.success else w0.copy()

# ── Equal Weight ─────────────────────────────────────────────────────────────
w_equal = w0.copy()

# Clip tiny numerical noise
for w in [w_sharpe, w_minvol, w_equal]:
    w[w < 1e-6] = 0.0
    w /= w.sum()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: PERFORMANCE METRICS
# ─────────────────────────────────────────────────────────────────────────────
def metrics(w):
    r   = port_return(w, mu)
    v   = port_vol(w, Sigma)
    sr  = (r - RISK_FREE_RATE) / v if v > 1e-10 else 0.0
    return r, v, sr

r_sh, v_sh, sr_sh       = metrics(w_sharpe)
r_mv, v_mv, sr_mv       = metrics(w_minvol)
r_eq, v_eq, sr_eq       = metrics(w_equal)

print(f"\n  {'Portfolio':18s} {'Return':>8s} {'Volatility':>12s} {'Sharpe':>8s}")
print("  " + "-" * 52)
print(f"  {'Max Sharpe':18s} {r_sh:>8.2%} {v_sh:>12.2%} {sr_sh:>8.3f}")
print(f"  {'Min Volatility':18s} {r_mv:>8.2%} {v_mv:>12.2%} {sr_mv:>8.3f}")
print(f"  {'Equal Weight':18s} {r_eq:>8.2%} {v_eq:>12.2%} {sr_eq:>8.3f}")

print(f"\n  Max Sharpe Weights:")
for t, w in zip(available_tickers, w_sharpe):
    name = SHORT_NAMES.get(t, t)
    print(f"    {name:14s}: {w:.2%}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: MONTE CARLO EFFICIENT FRONTIER
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n🎲  Running {N_MC:,} Monte Carlo simulations …")

np.random.seed(42)
mc_ret = np.zeros(N_MC)
mc_vol = np.zeros(N_MC)
mc_sr  = np.zeros(N_MC)
mc_w   = np.zeros((N_MC, n_assets))

for i in range(N_MC):
    raw_w  = np.random.dirichlet(np.ones(n_assets))
    raw_w  = np.clip(raw_w, 0, MAX_WEIGHT)
    raw_w /= raw_w.sum()
    mc_w[i]   = raw_w
    mc_ret[i] = port_return(raw_w, mu)
    mc_vol[i] = port_vol(raw_w, Sigma)
    mc_sr[i]  = port_sharpe(raw_w, mu, Sigma)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: CUMULATIVE GROWTH
# ─────────────────────────────────────────────────────────────────────────────
cum_growth = (1 + daily_returns).cumprod() * 100  # ₹100 invested

# Portfolio cumulative growth
port_daily_returns = daily_returns[available_tickers].dot(pd.Series(w_sharpe, index=available_tickers))
port_cum = (1 + port_daily_returns).cumprod() * 100

# ─────────────────────────────────────────────────────────────────────────────
# STEP 8: CHARTING
# ─────────────────────────────────────────────────────────────────────────────
print("\n🎨  Generating charts …")

plt.rcParams.update({
    'figure.facecolor'  : BG_COLOR,
    'axes.facecolor'    : CARD_COLOR,
    'axes.edgecolor'    : '#30363D',
    'axes.labelcolor'   : TEXT_COLOR,
    'text.color'        : TEXT_COLOR,
    'xtick.color'       : TEXT_COLOR,
    'ytick.color'       : TEXT_COLOR,
    'grid.color'        : '#21262D',
    'legend.facecolor'  : '#21262D',
    'legend.edgecolor'  : '#30363D',
    'font.family'       : 'DejaVu Sans',
    'font.size'         : 10,
})

short_labels = [SHORT_NAMES.get(t, t) for t in available_tickers]

# ── Chart 1: Correlation Heatmap ─────────────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(8, 6))
fig1.patch.set_facecolor(BG_COLOR)

cmap = LinearSegmentedColormap.from_list(
    'custom_rg',
    ['#FF6B6B', '#FFFFFF', '#6BCB77'],
    N=256,
)
im = ax1.imshow(corr_matrix.values, cmap=cmap, vmin=-1, vmax=1, aspect='auto')
plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)

ax1.set_xticks(range(n_assets))
ax1.set_yticks(range(n_assets))
ax1.set_xticklabels(short_labels, rotation=30, ha='right', fontsize=9)
ax1.set_yticklabels(short_labels, fontsize=9)

for i in range(n_assets):
    for j in range(n_assets):
        val = corr_matrix.values[i, j]
        color = 'black' if abs(val) < 0.5 else 'white'
        ax1.text(j, i, f'{val:.2f}', ha='center', va='center',
                 color=color, fontsize=9, fontweight='bold')

ax1.set_title('Correlation Matrix — Indian ETFs', pad=14,
              fontsize=13, fontweight='bold', color=ACCENT)
fig1.tight_layout()
heatmap_path = os.path.join(OUTPUT_DIR, 'chart_1_correlation_heatmap.png')
fig1.savefig(heatmap_path, dpi=150, bbox_inches='tight',
             facecolor=BG_COLOR)
plt.close(fig1)
print(f"  ✓ Saved: {heatmap_path}")

# ── Chart 2: Efficient Frontier ───────────────────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 7))
fig2.patch.set_facecolor(BG_COLOR)

sc = ax2.scatter(mc_vol * 100, mc_ret * 100, c=mc_sr, cmap='plasma',
                 alpha=0.4, s=2, zorder=1)
cb = plt.colorbar(sc, ax=ax2)
cb.set_label('Sharpe Ratio', color=TEXT_COLOR)
cb.ax.yaxis.set_tick_params(color=TEXT_COLOR)
plt.setp(cb.ax.yaxis.get_ticklabels(), color=TEXT_COLOR)

stock_vols = np.sqrt(np.diag(Sigma)) * 100
stock_rets = mu * 100
for i, (t, sv, sr) in enumerate(zip(available_tickers, stock_vols, stock_rets)):
    ax2.scatter(sv, sr, s=100, c=PALETTE[i % len(PALETTE)],
                marker='D', zorder=4, edgecolors='white', linewidths=0.8)
    ax2.annotate(short_labels[i], (sv, sr),
                 xytext=(7, 4), textcoords='offset points',
                 fontsize=8.5, color=PALETTE[i % len(PALETTE)], fontweight='bold')

ax2.scatter(v_sh * 100, r_sh * 100, s=300, c='#FFD700', marker='*',
            zorder=5, edgecolors='black', linewidths=1.2, label='Max Sharpe')
ax2.scatter(v_mv * 100, r_mv * 100, s=200, c='#00D4FF', marker='s',
            zorder=5, edgecolors='black', linewidths=1.2, label='Min Volatility')
ax2.scatter(v_eq * 100, r_eq * 100, s=200, c='#FF6B6B', marker='^',
            zorder=5, edgecolors='black', linewidths=1.2, label='Equal Weight')

ax2.set_xlabel('Annualised Volatility (%)', fontsize=11)
ax2.set_ylabel('Annualised Expected Return (%)', fontsize=11)
ax2.set_title(f'Efficient Frontier — {N_MC:,} Monte Carlo Portfolios\n(45% max weight cap)',
              fontsize=13, fontweight='bold', color=ACCENT, pad=12)
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.25, linestyle='--')
fig2.tight_layout()
frontier_path = os.path.join(OUTPUT_DIR, 'chart_2_efficient_frontier.png')
fig2.savefig(frontier_path, dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close(fig2)
print(f"  ✓ Saved: {frontier_path}")

# ── Chart 3: Max Sharpe Allocation Pie ───────────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(8, 7))
fig3.patch.set_facecolor(BG_COLOR)

non_zero_mask = w_sharpe > 0.005
pie_labels = [short_labels[i] if non_zero_mask[i] else '' for i in range(n_assets)]
explode = [0.04 if w > 0.005 else 0 for w in w_sharpe]

wedges, texts, autotexts = ax3.pie(
    w_sharpe, labels=pie_labels, autopct='%1.1f%%',
    colors=PALETTE[:n_assets], startangle=90,
    explode=explode, pctdistance=0.75,
    wedgeprops=dict(linewidth=1.5, edgecolor=BG_COLOR),
)
for text in texts:
    text.set_color(TEXT_COLOR)
    text.set_fontsize(10)
    text.set_fontweight('bold')
for at in autotexts:
    at.set_color('#0D1117')
    at.set_fontsize(9)
    at.set_fontweight('bold')

centre_circle = plt.Circle((0, 0), 0.55, color=CARD_COLOR, linewidth=0)
ax3.add_artist(centre_circle)
ax3.text(0, 0.08, 'Max Sharpe', ha='center', va='center',
         fontsize=9, color=TEXT_COLOR)
ax3.text(0, -0.08, f'SR = {sr_sh:.3f}', ha='center', va='center',
         fontsize=11, color='#FFD700', fontweight='bold')

ax3.set_title('Max Sharpe Portfolio — Optimal Allocation',
              fontsize=13, fontweight='bold', color=ACCENT, pad=18)
fig3.tight_layout()
pie_path = os.path.join(OUTPUT_DIR, 'chart_3_max_sharpe_pie.png')
fig3.savefig(pie_path, dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close(fig3)
print(f"  ✓ Saved: {pie_path}")

# ── Chart 4: Cumulative Growth ₹100 ──────────────────────────────────────────
fig4, ax4 = plt.subplots(figsize=(12, 6))
fig4.patch.set_facecolor(BG_COLOR)

for i, t in enumerate(available_tickers):
    ax4.plot(cum_growth.index, cum_growth[t],
             color=PALETTE[i % len(PALETTE)],
             linewidth=1.5, alpha=0.85, label=short_labels[i])

ax4.plot(port_cum.index, port_cum.values,
         color='#FFD700', linewidth=2.5, linestyle='--',
         label='Max Sharpe Portfolio', zorder=5)

ax4.axhline(100, color='#30363D', linewidth=1, linestyle=':')
ax4.set_xlabel('Date', fontsize=11)
ax4.set_ylabel('Value of ₹100 Invested', fontsize=11)
ax4.set_title(f'Cumulative Growth — ₹100 Invested ({actual_start} → {actual_end})',
              fontsize=13, fontweight='bold', color=ACCENT, pad=12)
ax4.legend(fontsize=9, loc='upper left', ncol=2)
ax4.grid(True, alpha=0.2, linestyle='--')
fig4.tight_layout()
growth_path = os.path.join(OUTPUT_DIR, 'chart_4_cumulative_growth.png')
fig4.savefig(growth_path, dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close(fig4)
print(f"  ✓ Saved: {growth_path}")

# ── Chart 5: Min Volatility Pie ───────────────────────────────────────────────
fig5, ax5 = plt.subplots(figsize=(8, 7))
fig5.patch.set_facecolor(BG_COLOR)

non_zero_mv = w_minvol > 0.005
pie_labels_mv = [short_labels[i] if non_zero_mv[i] else '' for i in range(n_assets)]
explode_mv = [0.04 if w > 0.005 else 0 for w in w_minvol]

wedges5, texts5, autotexts5 = ax5.pie(
    w_minvol, labels=pie_labels_mv, autopct='%1.1f%%',
    colors=PALETTE[:n_assets], startangle=90,
    explode=explode_mv, pctdistance=0.75,
    wedgeprops=dict(linewidth=1.5, edgecolor=BG_COLOR),
)
for text in texts5:
    text.set_color(TEXT_COLOR)
    text.set_fontsize(10)
    text.set_fontweight('bold')
for at in autotexts5:
    at.set_color('#0D1117')
    at.set_fontsize(9)
    at.set_fontweight('bold')

centre_circle5 = plt.Circle((0, 0), 0.55, color=CARD_COLOR, linewidth=0)
ax5.add_artist(centre_circle5)
ax5.text(0, 0.08, 'Min Volatility', ha='center', va='center',
         fontsize=9, color=TEXT_COLOR)
ax5.text(0, -0.08, f'Vol = {v_mv:.2%}', ha='center', va='center',
         fontsize=11, color='#00D4FF', fontweight='bold')

ax5.set_title('Minimum Volatility Portfolio — Allocation',
              fontsize=13, fontweight='bold', color=ACCENT, pad=18)
fig5.tight_layout()
minvol_path = os.path.join(OUTPUT_DIR, 'chart_5_min_vol_pie.png')
fig5.savefig(minvol_path, dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close(fig5)
print(f"  ✓ Saved: {minvol_path}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 9: SUMMARY TABLE
# ─────────────────────────────────────────────────────────────────────────────
print("\n📋  Building summary table …")

summary_data = {
    'Metric': [
        'Expected Return (p.a.)',
        'Volatility (p.a.)',
        'Sharpe Ratio',
        '─── Weights ───',
    ] + short_labels,
    'Max Sharpe': [
        f'{r_sh:.2%}', f'{v_sh:.2%}', f'{sr_sh:.3f}', '',
    ] + [f'{w:.2%}' for w in w_sharpe],
    'Min Volatility': [
        f'{r_mv:.2%}', f'{v_mv:.2%}', f'{sr_mv:.3f}', '',
    ] + [f'{w:.2%}' for w in w_minvol],
    'Equal Weight': [
        f'{r_eq:.2%}', f'{v_eq:.2%}', f'{sr_eq:.3f}', '',
    ] + [f'{w:.2%}' for w in w_equal],
}
summary_df = pd.DataFrame(summary_data)

print("\n" + "=" * 70)
print(summary_df.to_string(index=False))
print("=" * 70)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 10: A4 PDF DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
print("\n📄  Assembling PDF dashboard …")

# Build dashboard as a single matplotlib figure (A4 landscape)
fig_pdf = plt.figure(figsize=(16.54, 11.69))   # A4 landscape inches
fig_pdf.patch.set_facecolor(BG_COLOR)

# Title banner
fig_pdf.text(
    0.5, 0.965,
    'Indian NSE ETF Portfolio — Modern Portfolio Theory Dashboard',
    ha='center', va='top', fontsize=17, fontweight='bold',
    color=ACCENT,
)
fig_pdf.text(
    0.5, 0.935,
    f'Data: {actual_start} → {actual_end}  |  {n_days} trading days  |  '
    f'Risk-Free Rate: {RISK_FREE_RATE:.2%} (India 10-Yr G-Sec, Jul-2026)  |  '
    f'Max Weight Cap: {MAX_WEIGHT:.0%}',
    ha='center', va='top', fontsize=9, color='#8B949E',
)

# Grid: 3 rows × 3 cols
gs = gridspec.GridSpec(
    3, 3,
    figure=fig_pdf,
    top=0.91, bottom=0.05,
    left=0.05, right=0.98,
    wspace=0.28, hspace=0.38,
)

# ── Sub-plot A: Efficient Frontier (large) ────────────────────────────────────
axA = fig_pdf.add_subplot(gs[0:2, 0:2])
scA = axA.scatter(mc_vol * 100, mc_ret * 100, c=mc_sr, cmap='plasma',
                  alpha=0.35, s=1.5, zorder=1)
cbA = plt.colorbar(scA, ax=axA, pad=0.02)
cbA.set_label('Sharpe Ratio', fontsize=8)
cbA.ax.tick_params(labelsize=7)

for i, (sv, sr_i) in enumerate(zip(stock_vols, stock_rets)):
    axA.scatter(sv, sr_i, s=80, c=PALETTE[i % len(PALETTE)],
                marker='D', zorder=4, edgecolors='white', linewidths=0.6)
    axA.annotate(short_labels[i], (sv, sr_i),
                 xytext=(6, 3), textcoords='offset points',
                 fontsize=7.5, color=PALETTE[i % len(PALETTE)], fontweight='bold')

axA.scatter(v_sh * 100, r_sh * 100, s=200, c='#FFD700', marker='*',
            zorder=5, edgecolors='black', linewidths=1, label='Max Sharpe')
axA.scatter(v_mv * 100, r_mv * 100, s=150, c='#00D4FF', marker='s',
            zorder=5, edgecolors='black', linewidths=1, label='Min Volatility')
axA.scatter(v_eq * 100, r_eq * 100, s=150, c='#FF6B6B', marker='^',
            zorder=5, edgecolors='black', linewidths=1, label='Equal Weight')

axA.set_xlabel('Volatility (%)', fontsize=9)
axA.set_ylabel('Expected Return (%)', fontsize=9)
axA.set_title(f'Efficient Frontier ({N_MC:,} Monte Carlo Portfolios)', fontsize=10, color=ACCENT)
axA.legend(fontsize=7.5, framealpha=0.8)
axA.grid(True, alpha=0.2, linestyle='--')
axA.tick_params(labelsize=8)

# ── Sub-plot B: Correlation Heatmap ──────────────────────────────────────────
axB = fig_pdf.add_subplot(gs[0:2, 2])
imB = axB.imshow(corr_matrix.values, cmap=cmap, vmin=-1, vmax=1)
plt.colorbar(imB, ax=axB, fraction=0.05, pad=0.03)
axB.set_xticks(range(n_assets))
axB.set_yticks(range(n_assets))
axB.set_xticklabels(short_labels, rotation=35, ha='right', fontsize=7.5)
axB.set_yticklabels(short_labels, fontsize=7.5)
for i in range(n_assets):
    for j in range(n_assets):
        val = corr_matrix.values[i, j]
        color = 'black' if abs(val) < 0.5 else 'white'
        axB.text(j, i, f'{val:.2f}', ha='center', va='center',
                 color=color, fontsize=7, fontweight='bold')
axB.set_title('Correlation Matrix', fontsize=10, color=ACCENT)
axB.tick_params(labelsize=7.5)

# ── Sub-plot C: Max Sharpe Pie ────────────────────────────────────────────────
axC = fig_pdf.add_subplot(gs[2, 0])
non_z = w_sharpe > 0.005
pie_l = [short_labels[i] if non_z[i] else '' for i in range(n_assets)]
expl  = [0.04 if w > 0.005 else 0 for w in w_sharpe]
wedgesC, textsC, autotextsC = axC.pie(
    w_sharpe, labels=pie_l, autopct='%1.0f%%',
    colors=PALETTE[:n_assets], startangle=90, explode=expl,
    pctdistance=0.75,
    wedgeprops=dict(linewidth=1.2, edgecolor=BG_COLOR),
)
for t in textsC:
    t.set_color(TEXT_COLOR); t.set_fontsize(7)
for at in autotextsC:
    at.set_color('#0D1117'); at.set_fontsize(7)
cC = plt.Circle((0, 0), 0.50, color=CARD_COLOR)
axC.add_artist(cC)
axC.text(0, 0, f'SR={sr_sh:.2f}', ha='center', va='center',
         fontsize=8, color='#FFD700', fontweight='bold')
axC.set_title('Max Sharpe\nAllocation', fontsize=9, color=ACCENT)

# ── Sub-plot D: Min Vol Pie ────────────────────────────────────────────────────
axD = fig_pdf.add_subplot(gs[2, 1])
non_zmv = w_minvol > 0.005
pie_lmv = [short_labels[i] if non_zmv[i] else '' for i in range(n_assets)]
explmv  = [0.04 if w > 0.005 else 0 for w in w_minvol]
wedgesD, textsD, autotextsD = axD.pie(
    w_minvol, labels=pie_lmv, autopct='%1.0f%%',
    colors=PALETTE[:n_assets], startangle=90, explode=explmv,
    pctdistance=0.75,
    wedgeprops=dict(linewidth=1.2, edgecolor=BG_COLOR),
)
for t in textsD:
    t.set_color(TEXT_COLOR); t.set_fontsize(7)
for at in autotextsD:
    at.set_color('#0D1117'); at.set_fontsize(7)
cD = plt.Circle((0, 0), 0.50, color=CARD_COLOR)
axD.add_artist(cD)
axD.text(0, 0, f'Vol={v_mv:.1%}', ha='center', va='center',
         fontsize=8, color='#00D4FF', fontweight='bold')
axD.set_title('Min Volatility\nAllocation', fontsize=9, color=ACCENT)

# ── Sub-plot E: Cumulative Growth ─────────────────────────────────────────────
axE = fig_pdf.add_subplot(gs[2, 2])
for i, t in enumerate(available_tickers):
    axE.plot(cum_growth.index, cum_growth[t],
             color=PALETTE[i % len(PALETTE)], linewidth=1.2,
             alpha=0.75, label=short_labels[i])
axE.plot(port_cum.index, port_cum.values,
         color='#FFD700', linewidth=2, linestyle='--',
         label='Max Sharpe', zorder=5)
axE.axhline(100, color='#30363D', linewidth=0.8, linestyle=':')
axE.set_xlabel('Date', fontsize=8)
axE.set_ylabel('₹100 Invested', fontsize=8)
axE.set_title('Cumulative Growth', fontsize=9, color=ACCENT)
axE.legend(fontsize=6, ncol=2, loc='upper left')
axE.grid(True, alpha=0.18, linestyle='--')
axE.tick_params(labelsize=7)
plt.setp(axE.get_xticklabels(), rotation=30, ha='right')

# ── Summary table text at bottom ─────────────────────────────────────────────
table_y  = 0.032
col_x    = [0.10, 0.38, 0.57, 0.76]
headers  = ['Metric', 'Max Sharpe', 'Min Volatility', 'Equal Weight']
row_data = [
    ['Return (p.a.)',  f'{r_sh:.2%}', f'{r_mv:.2%}', f'{r_eq:.2%}'],
    ['Volatility',     f'{v_sh:.2%}', f'{v_mv:.2%}', f'{v_eq:.2%}'],
    ['Sharpe Ratio',   f'{sr_sh:.3f}',f'{sr_mv:.3f}',f'{sr_eq:.3f}'],
]
for idx, sl in enumerate(short_labels):
    row_data.append([
        f'Weight: {sl}',
        f'{w_sharpe[idx]:.1%}',
        f'{w_minvol[idx]:.1%}',
        f'{w_equal[idx]:.1%}',
    ])

header_color = ACCENT
for hx, h in zip(col_x, headers):
    fig_pdf.text(hx, table_y + 0.012, h, ha='left', va='bottom',
                 fontsize=7.5, fontweight='bold', color=header_color)

row_colors = [TEXT_COLOR, '#8B949E']
for ri, row in enumerate(row_data):
    ry = table_y - ri * 0.011
    color = row_colors[ri % 2]
    for hx, cell in zip(col_x, row):
        fig_pdf.text(hx, ry, cell, ha='left', va='bottom',
                     fontsize=6.8, color=color)

fig_pdf.text(
    0.5, 0.002,
    f'Generated by MPT Optimizer  |  Data: Yahoo Finance  |  '
    f'Risk-free rate {RISK_FREE_RATE:.2%} (India 10-Yr G-Sec)  |  '
    f'Analysis date: {END_DATE}',
    ha='center', fontsize=6.5, color='#484F58',
)

pdf_path = os.path.join(OUTPUT_DIR, 'MPT_Indian_ETF_Dashboard_A4.pdf')
fig_pdf.savefig(pdf_path, dpi=200, bbox_inches='tight',
                facecolor=BG_COLOR, format='pdf')
plt.close(fig_pdf)
print(f"  ✓ Saved: {pdf_path}")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  FINAL RESULTS SUMMARY")
print("=" * 65)
print(f"\n  Data range : {actual_start}  →  {actual_end}  ({n_days} trading days)")
print(f"  Tickers    : {', '.join(available_tickers)}")
print(f"  Risk-Free  : {RISK_FREE_RATE:.2%}  (India 10-Yr G-Sec, Jul-2026)")
print(f"  Weight cap : {MAX_WEIGHT:.0%} per asset")

print(f"\n  ┌{'─'*52}┐")
print(f"  │{'PORTFOLIO COMPARISON':^52}│")
print(f"  ├{'─'*18}┬{'─'*10}┬{'─'*12}┬{'─'*9}┤")
print(f"  │{'Portfolio':^18}│{'Return':^10}│{'Volatility':^12}│{'Sharpe':^9}│")
print(f"  ├{'─'*18}┼{'─'*10}┼{'─'*12}┼{'─'*9}┤")
print(f"  │{'Max Sharpe':^18}│{r_sh:^10.2%}│{v_sh:^12.2%}│{sr_sh:^9.3f}│")
print(f"  │{'Min Volatility':^18}│{r_mv:^10.2%}│{v_mv:^12.2%}│{sr_mv:^9.3f}│")
print(f"  │{'Equal Weight':^18}│{r_eq:^10.2%}│{v_eq:^12.2%}│{sr_eq:^9.3f}│")
print(f"  └{'─'*18}┴{'─'*10}┴{'─'*12}┴{'─'*9}┘")

print(f"\n  MAX SHARPE PORTFOLIO — Optimal Weights:")
print(f"  {'─'*38}")
for t, w in sorted(zip(available_tickers, w_sharpe), key=lambda x: -x[1]):
    bar = '█' * int(w * 30)
    print(f"  {SHORT_NAMES.get(t, t):14s}: {w:6.2%}  {bar}")

print(f"\n  Sharpe Ratio (Max Sharpe): {sr_sh:.4f}")
print(f"  Expected Return           : {r_sh:.2%}")
print(f"  Volatility                : {v_sh:.2%}")

print(f"\n  Output files:")
print(f"    • {heatmap_path}")
print(f"    • {frontier_path}")
print(f"    • {pie_path}")
print(f"    • {growth_path}")
print(f"    • {minvol_path}")
print(f"    • {pdf_path}")
print("\n" + "=" * 65)
print("  ✅  Analysis complete!")
print("=" * 65)
