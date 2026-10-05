
"""
/api/compare — Returns full MPT comparison data (portfolio weights, metrics,
cumulative growth series, efficient frontier cloud) for the Compare Dashboard.
Heavy endpoint (~30s cold start) — results are cached for 6 hours.
"""

from http.server import BaseHTTPRequestHandler
import json
import time

_CACHE: dict = {}
CACHE_TTL = 6 * 3600  # 6 hours


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _CACHE
        try:
            now = time.time()
            if _CACHE.get('ts') and now - _CACHE['ts'] < CACHE_TTL:
                payload = _CACHE['data']
            else:
                payload = _build_data()
                _CACHE = {'ts': now, 'data': payload}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.end_headers()
            self.wfile.write(payload.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))


def _build_data() -> str:
    import numpy as np
    import pandas as pd
    import yfinance as yf
    from scipy.optimize import minimize
    import datetime

    TICKERS = [
        'NIFTYBEES.NS', 'JUNIORBEES.NS', 'BANKBEES.NS', 'MID150BEES.NS',
        'MON100.NS', 'GOLDBEES.NS', 'SILVERBEES.NS', 'SETF10GILT.NS', 'LIQUIDBEES.NS'
    ]
    SHORT = {
        'NIFTYBEES.NS': 'NiftyBees', 'JUNIORBEES.NS': 'JuniorBees', 'BANKBEES.NS': 'BankBees',
        'MID150BEES.NS': 'Mid150Bees', 'MON100.NS': 'Nasdaq100', 'GOLDBEES.NS': 'GoldBees',
        'SILVERBEES.NS': 'SilverBees', 'SETF10GILT.NS': 'GSec10Yr', 'LIQUIDBEES.NS': 'LiquidBees'
    }
    COLORS = {
        'NIFTYBEES.NS': '#60a5fa', 'JUNIORBEES.NS': '#ef4444',
        'BANKBEES.NS': '#f59e0b',  'GOLDBEES.NS': '#fbbf24',
        'LIQUIDBEES.NS': '#a78bfa', 'MID150BEES.NS': '#14b8a6',
        'MON100.NS': '#8b5cf6', 'SILVERBEES.NS': '#94a3b8',
        'SETF10GILT.NS': '#ec4899'
    }
    RF = 0.068
    MAX_W = 0.45
    TDAYS = 252
    N_MC = 3000

    end = datetime.date.today().strftime('%Y-%m-%d')
    raw = yf.download(TICKERS, start='2019-01-01', end=end,
                      auto_adjust=True, progress=False, group_by='column')

    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw['Close'].copy()
    else:
        prices = raw.copy()

    prices.dropna(how='all', inplace=True)
    prices.ffill(inplace=True)
    prices.dropna(inplace=True)

    # Clean split artifacts
    prices_c = prices.copy().astype(float)
    for col in prices_c.columns:
        chk = prices_c[col].pct_change()
        bad = chk.index[chk.abs() > 0.15].tolist()
        if bad:
            nan_set = set()
            for d in bad:
                pos = prices_c.index.get_loc(d)
                if pos > 0:
                    nan_set.add(prices_c.index[pos - 1])
                nan_set.add(d)
            prices_c.loc[sorted(nan_set), col] = np.nan
    prices_c = prices_c.interpolate(method='time', limit=10)
    prices_c.ffill(inplace=True)
    prices_c.bfill(inplace=True)
    prices = prices_c

    available = list(prices.columns)
    n = len(available)
    snames = [SHORT[t] for t in available]
    colors = [COLORS[t] for t in available]

    daily = prices.pct_change().dropna()
    mu_s = daily.mean() * TDAYS
    cov_s = daily.cov() * TDAYS
    corr_s = daily.corr()
    mu = mu_s.values
    Sigma = cov_s.values

    def perf(w):
        r = float(np.dot(w, mu))
        v = float(np.sqrt(w @ Sigma @ w))
        sr = (r - RF) / v if v > 1e-10 else 0.0
        return r, v, sr

    con = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bds = tuple((0, MAX_W) for _ in range(n))
    w0 = np.ones(n) / n

    res_sh = minimize(lambda w: -perf(w)[2], w0, method='SLSQP',
                      bounds=bds, constraints=con,
                      options={'maxiter': 3000, 'ftol': 1e-12})
    res_mv = minimize(lambda w: perf(w)[1], w0, method='SLSQP',
                      bounds=bds, constraints=con,
                      options={'maxiter': 3000, 'ftol': 1e-12})

    def clean(w):
        w[w < 1e-5] = 0.0
        w /= w.sum()
        return w

    w_sh = clean(res_sh.x if res_sh.success else w0.copy())
    w_mv = clean(res_mv.x if res_mv.success else w0.copy())
    w_eq = clean(w0.copy())

    r_sh, v_sh, sr_sh = perf(w_sh)
    r_mv, v_mv, sr_mv = perf(w_mv)
    r_eq, v_eq, sr_eq = perf(w_eq)

    # Sortino & max drawdown per portfolio
    def port_metrics(w, name=''):
        pd_s = daily[available].dot(pd.Series(w, index=available))
        down = pd_s[pd_s < 0]
        down_vol = float(down.std() * np.sqrt(TDAYS)) if len(down) > 1 else 1e-10
        r, v, sr = perf(w)
        sortino = (r - RF) / down_vol if down_vol > 1e-10 else 0.0
        cum = (1 + pd_s).cumprod()
        mdd = float(((cum / cum.cummax()) - 1).min())
        calmar = r / abs(mdd) if abs(mdd) > 1e-10 else 0.0
        cvar_thresh = float(np.percentile(pd_s, 5))
        cvar = float(pd_s[pd_s <= cvar_thresh].mean())
        return {
            'return': round(r * 100, 2),
            'vol': round(v * 100, 2),
            'sharpe': round(sr, 4),
            'sortino': round(sortino, 4),
            'max_dd': round(mdd * 100, 2),
            'calmar': round(calmar, 4),
            'cvar_95': round(cvar * 100, 2),
        }

    pm_sh = port_metrics(w_sh)
    pm_mv = port_metrics(w_mv)
    pm_eq = port_metrics(w_eq)

    # Cumulative growth (normalised to 100)
    def cum_growth(w):
        pd_s = daily[available].dot(pd.Series(w, index=available))
        return (1 + pd_s).cumprod() * 100

    dates = [d.strftime('%Y-%m-%d') for d in daily.index]
    g_sh = [round(float(v), 4) for v in cum_growth(w_sh).values]
    g_mv = [round(float(v), 4) for v in cum_growth(w_mv).values]
    g_eq = [round(float(v), 4) for v in cum_growth(w_eq).values]

    # Individual ETF growth
    etf_growth = {}
    for t in available:
        cum = (1 + daily[t]).cumprod() * 100
        etf_growth[SHORT[t]] = [round(float(v), 4) for v in cum.values]

    # Drawdown series
    def dd_series(w):
        pd_s = daily[available].dot(pd.Series(w, index=available))
        cum = (1 + pd_s).cumprod()
        dd = (cum / cum.cummax()) - 1
        return [round(float(v) * 100, 4) for v in dd.values]

    # Monte Carlo (small subset for chart)
    np.random.seed(42)
    mc_r, mc_v, mc_sr = [], [], []
    for _ in range(N_MC):
        w = np.clip(np.random.dirichlet(np.ones(n)), 0, MAX_W)
        w /= w.sum()
        r, v, sr = perf(w)
        mc_r.append(round(r * 100, 3))
        mc_v.append(round(v * 100, 3))
        mc_sr.append(round(sr, 4))

    # Correlation matrix
    corr_list = corr_s.values.tolist()

    # Individual asset stats
    asset_stats = []
    for i, t in enumerate(available):
        dr = daily[t].dropna()
        ann = float(mu_s[t])
        vol = float(np.sqrt(cov_s.loc[t, t]))
        mdd = float(((prices[t] / prices[t].cummax()) - 1).min())
        total = float((prices[t].iloc[-1] / prices[t].iloc[0]) - 1)
        asset_stats.append({
            'name': SHORT[t],
            'color': COLORS[t],
            'ann_return': round(ann * 100, 2),
            'ann_vol': round(vol * 100, 2),
            'sharpe': round((ann - RF) / vol if vol > 1e-10 else 0, 4),
            'max_dd': round(mdd * 100, 2),
            'total_return': round(total * 100, 2),
            'best_day': round(float(dr.max()) * 100, 2),
            'worst_day': round(float(dr.min()) * 100, 2),
        })

    result = {
        'generated_at': datetime.datetime.now().isoformat(),
        'tickers': snames,
        'colors': colors,
        'portfolios': {
            'maxsharpe': {
                'label': 'Max Sharpe ⭐',
                'color': '#fbbf24',
                'weights': {snames[i]: round(float(w_sh[i]) * 100, 2) for i in range(n)},
                'metrics': pm_sh,
            },
            'minvol': {
                'label': 'Min Volatility 🛡️',
                'color': '#60a5fa',
                'weights': {snames[i]: round(float(w_mv[i]) * 100, 2) for i in range(n)},
                'metrics': pm_mv,
            },
            'equal': {
                'label': 'Equal Weight ⚖️',
                'color': '#94a3b8',
                'weights': {snames[i]: round(float(w_eq[i]) * 100, 2) for i in range(n)},
                'metrics': pm_eq,
            },
        },
        'dates': dates,
        'growth': {
            'maxsharpe': g_sh,
            'minvol': g_mv,
            'equal': g_eq,
            **etf_growth,
        },
        'drawdown': {
            'maxsharpe': dd_series(w_sh),
            'minvol': dd_series(w_mv),
            'equal': dd_series(w_eq),
        },
        'monte_carlo': {
            'vols': mc_v,
            'returns': mc_r,
            'sharpes': mc_sr,
        },
        'correlation': {
            'labels': snames,
            'matrix': corr_list,
        },
        'asset_stats': asset_stats,
        'meta': {
            'start': str(daily.index[0].date()),
            'end': str(daily.index[-1].date()),
            'n_days': len(daily),
            'rf': RF,
        },
    }
    return json.dumps(result)
