#!/usr/bin/env python3
"""
MPT Indian ETF — White-Background PDF Report Generator
Produces a clean, print-ready A4 PDF with white background and full content.
Re-uses the live data that was already downloaded.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from matplotlib.table import Table
import yfinance as yf
from scipy.optimize import minimize
import warnings, os, datetime

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
OUTPUT_DIR      = "/Users/surajitdas/untitled folder 5"
RISK_FREE_RATE  = 0.068        # 6.80% India 10-Yr G-Sec, Jul-2026
START_DATE      = '2019-01-01'
END_DATE        = datetime.date.today().strftime('%Y-%m-%d')
MAX_WEIGHT      = 0.45
N_MC            = 10_000
TRADING_DAYS    = 252

TICKERS = ['NIFTYBEES.NS','JUNIORBEES.NS','BANKBEES.NS','GOLDBEES.NS','LIQUIDBEES.NS']
SHORT   = {'NIFTYBEES.NS':'NiftyBees','JUNIORBEES.NS':'JuniorBees',
           'BANKBEES.NS':'BankBees','GOLDBEES.NS':'GoldBees','LIQUIDBEES.NS':'LiquidBees'}
FULL    = {'NIFTYBEES.NS':'Nifty 50 BeES','JUNIORBEES.NS':'Junior BeES (Next 50)',
           'BANKBEES.NS':'Bank BeES','GOLDBEES.NS':'Gold BeES','LIQUIDBEES.NS':'Liquid BeES'}

# White-report colour palette
PALETTE     = ['#1565C0','#E53935','#F9A825','#2E7D32','#6A1B9A']
WH          = 'white'
BORDER      = '#CCCCCC'
DARK        = '#1A1A2E'
HEADER_BG   = '#1565C0'
ALT_ROW     = '#F0F4FF'

# ─────────────────────────────────────────────────────────────────────────────
# 1. DOWNLOAD & CLEAN DATA
# ─────────────────────────────────────────────────────────────────────────────
print("📥  Downloading data …")
raw    = yf.download(TICKERS, start=START_DATE, end=END_DATE,
                     auto_adjust=True, progress=True, group_by='column')
prices = raw['Close'].copy() if isinstance(raw.columns, pd.MultiIndex) else raw.copy()
prices.dropna(how='all', inplace=True)
prices.ffill(inplace=True)
prices.dropna(inplace=True)

# Clean split artifacts (Dec 2019 1:10 split for NIFTYBEES/BANKBEES/GOLDBEES)
prices_c = prices.copy().astype(float)
for col in prices_c.columns:
    chk = prices_c[col].pct_change()
    bad = chk.index[chk.abs() > 0.15].tolist()
    if bad:
        nan_set = set()
        for d in bad:
            pos = prices_c.index.get_loc(d)
            if pos > 0: nan_set.add(prices_c.index[pos-1])
            nan_set.add(d)
        prices_c.loc[sorted(nan_set), col] = np.nan
prices_c = prices_c.interpolate(method='time', limit=10)
prices_c.ffill(inplace=True); prices_c.bfill(inplace=True)
prices = prices_c

actual_start = prices.index[0].strftime('%Y-%m-%d')
actual_end   = prices.index[-1].strftime('%Y-%m-%d')
n_days       = len(prices)
available    = list(prices.columns)
print(f"✅  {n_days} trading days  |  {actual_start} → {actual_end}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. RETURNS & STATS
# ─────────────────────────────────────────────────────────────────────────────
daily   = prices.pct_change().dropna()
mu_s    = daily.mean() * TRADING_DAYS       # Series
cov_s   = daily.cov()  * TRADING_DAYS       # DataFrame
corr_s  = daily.corr()
mu      = mu_s.values
Sigma   = cov_s.values
n       = len(available)
snames  = [SHORT[t] for t in available]

# ─────────────────────────────────────────────────────────────────────────────
# 3. OPTIMISATION
# ─────────────────────────────────────────────────────────────────────────────
def perf(w): 
    r = float(np.dot(w, mu))
    v = float(np.sqrt(w @ Sigma @ w))
    sr = (r - RISK_FREE_RATE) / v if v > 1e-10 else 0.0
    return r, v, sr

con  = [{'type':'eq','fun': lambda w: np.sum(w)-1}]
bds  = tuple((0, MAX_WEIGHT) for _ in range(n))
w0   = np.array([1/n]*n)

res_sh = minimize(lambda w: -(perf(w)[2]), w0, method='SLSQP', bounds=bds, constraints=con,
                  options={'maxiter':3000,'ftol':1e-12})
res_mv = minimize(lambda w: perf(w)[1], w0, method='SLSQP', bounds=bds, constraints=con,
                  options={'maxiter':3000,'ftol':1e-12})

def clean(w):
    w[w<1e-5] = 0.0; w /= w.sum(); return w

w_sh = clean(res_sh.x if res_sh.success else w0.copy())
w_mv = clean(res_mv.x if res_mv.success else w0.copy())
w_eq = clean(w0.copy())

r_sh, v_sh, sr_sh = perf(w_sh)
r_mv, v_mv, sr_mv = perf(w_mv)
r_eq, v_eq, sr_eq = perf(w_eq)

# ─────────────────────────────────────────────────────────────────────────────
# 4. MONTE CARLO
# ─────────────────────────────────────────────────────────────────────────────
print(f"🎲  Monte Carlo ({N_MC:,} portfolios) …")
np.random.seed(42)
mc_r, mc_v, mc_sr = np.zeros(N_MC), np.zeros(N_MC), np.zeros(N_MC)
for i in range(N_MC):
    w = np.clip(np.random.dirichlet(np.ones(n)), 0, MAX_WEIGHT)
    w /= w.sum()
    mc_r[i], mc_v[i], mc_sr[i] = perf(w)

# Cumulative growth
cum_g     = (1 + daily).cumprod() * 100
port_cum  = (1 + daily[available].dot(pd.Series(w_sh, index=available))).cumprod() * 100

# ─────────────────────────────────────────────────────────────────────────────
# 5. BUILD WHITE-BACKGROUND PDF  (A4 landscape = 16.54 × 11.69 in)
# ─────────────────────────────────────────────────────────────────────────────
print("📄  Building white-background PDF …")

plt.rcParams.update({
    'figure.facecolor' : WH, 'axes.facecolor': WH,
    'axes.edgecolor'   : BORDER, 'axes.labelcolor': DARK,
    'text.color'       : DARK, 'xtick.color': DARK, 'ytick.color': DARK,
    'grid.color'       : '#E0E0E0', 'legend.facecolor': WH,
    'legend.edgecolor' : BORDER, 'font.family': 'DejaVu Sans',
    'font.size'        : 9,
})

fig = plt.figure(figsize=(16.54, 11.69))
fig.patch.set_facecolor(WH)

# ── Title block ────────────────────────────────────────────────────────────
fig.text(0.5, 0.975, 'Modern Portfolio Theory — Indian NSE Index ETF Analysis',
         ha='center', va='top', fontsize=18, fontweight='bold', color=DARK)
fig.text(0.5, 0.952,
         f'Data: {actual_start} → {actual_end}  ({n_days} trading days)   |   '
         f'Risk-Free Rate: {RISK_FREE_RATE:.2%}  (India 10-Yr G-Sec, Jul-2026)   |   '
         f'Max Weight Cap: {MAX_WEIGHT:.0%} per asset   |   Monte Carlo: {N_MC:,} portfolios',
         ha='center', va='top', fontsize=9, color='#555555')

# Thin blue rule under title
ax_rule = fig.add_axes([0.04, 0.938, 0.92, 0.003])
ax_rule.set_facecolor(HEADER_BG); ax_rule.axis('off')

# ── Grid layout ────────────────────────────────────────────────────────────
gs = gridspec.GridSpec(3, 3, figure=fig,
                       top=0.925, bottom=0.06,
                       left=0.05, right=0.97,
                       wspace=0.30, hspace=0.42)

# ── A: Efficient Frontier (rows 0-1, cols 0-1) ─────────────────────────────
axA = fig.add_subplot(gs[0:2, 0:2])
scA = axA.scatter(mc_v*100, mc_r*100, c=mc_sr, cmap='RdYlGn',
                  alpha=0.35, s=1.8, zorder=1)
cbA = plt.colorbar(scA, ax=axA, pad=0.02, fraction=0.04)
cbA.set_label('Sharpe Ratio', fontsize=8, color=DARK)
cbA.ax.tick_params(labelsize=7, colors=DARK)

svols = np.sqrt(np.diag(Sigma))*100
srets = mu*100
for i,(sv,sr_i) in enumerate(zip(svols,srets)):
    axA.scatter(sv, sr_i, s=90, color=PALETTE[i%len(PALETTE)],
                marker='D', zorder=4, edgecolors=DARK, linewidths=0.7)
    axA.annotate(snames[i], (sv,sr_i), xytext=(6,3),
                 textcoords='offset points', fontsize=8,
                 color=PALETTE[i%len(PALETTE)], fontweight='bold')

axA.scatter(v_sh*100, r_sh*100, s=250, color='gold', marker='*',
            zorder=5, edgecolors=DARK, linewidths=1.2, label='★ Max Sharpe')
axA.scatter(v_mv*100, r_mv*100, s=140, color='royalblue', marker='s',
            zorder=5, edgecolors=DARK, linewidths=1.0, label='■ Min Volatility')
axA.scatter(v_eq*100, r_eq*100, s=140, color='tomato', marker='^',
            zorder=5, edgecolors=DARK, linewidths=1.0, label='▲ Equal Weight')

axA.set_xlabel('Annualised Volatility (%)', fontsize=9)
axA.set_ylabel('Annualised Expected Return (%)', fontsize=9)
axA.set_title(f'Efficient Frontier — {N_MC:,} Monte Carlo Portfolios  (45% max weight cap)',
              fontsize=10, fontweight='bold', color=DARK, pad=8)
axA.legend(fontsize=8, framealpha=0.9, edgecolor=BORDER)
axA.grid(True, alpha=0.4, linestyle='--', color='#DDDDDD')
axA.tick_params(labelsize=8)
for sp in axA.spines.values(): sp.set_color(BORDER)

# ── B: Correlation Heatmap (rows 0-1, col 2) ──────────────────────────────
axB = fig.add_subplot(gs[0:2, 2])
cmap_rg = LinearSegmentedColormap.from_list('rg',['#C62828','white','#1B5E20'],N=256)
imB = axB.imshow(corr_s.values, cmap=cmap_rg, vmin=-1, vmax=1)
cbB = plt.colorbar(imB, ax=axB, fraction=0.06, pad=0.03)
cbB.ax.tick_params(labelsize=7)
axB.set_xticks(range(n)); axB.set_yticks(range(n))
axB.set_xticklabels(snames, rotation=35, ha='right', fontsize=8)
axB.set_yticklabels(snames, fontsize=8)
for i in range(n):
    for j in range(n):
        val = corr_s.values[i,j]
        clr = 'white' if abs(val) > 0.55 else DARK
        axB.text(j, i, f'{val:.2f}', ha='center', va='center',
                 fontsize=8, color=clr, fontweight='bold')
axB.set_title('Asset Correlation Matrix', fontsize=10, fontweight='bold',
              color=DARK, pad=8)
axB.tick_params(labelsize=8)

# ── C: Max Sharpe Donut (row 2, col 0) ────────────────────────────────────
axC = fig.add_subplot(gs[2, 0])
nz_sh = w_sh > 0.005
pie_l = [snames[i] if nz_sh[i] else '' for i in range(n)]
expl  = [0.04 if w>0.005 else 0 for w in w_sh]
wC, tC, atC = axC.pie(
    w_sh, labels=pie_l, autopct='%1.0f%%',
    colors=PALETTE[:n], startangle=90, explode=expl, pctdistance=0.72,
    wedgeprops=dict(linewidth=1.5, edgecolor=WH),
)
for t in tC: t.set_color(DARK); t.set_fontsize(8); t.set_fontweight('bold')
for at in atC: at.set_fontsize(8); at.set_fontweight('bold'); at.set_color(WH)
cC = plt.Circle((0,0), 0.52, color=WH, linewidth=1.5, ec=BORDER); axC.add_artist(cC)
axC.text(0, 0.1, 'Max Sharpe', ha='center', va='center', fontsize=7.5, color='#555555')
axC.text(0, -0.12, f'SR = {sr_sh:.3f}', ha='center', va='center',
         fontsize=9.5, color='#B8860B', fontweight='bold')
axC.set_title('Max Sharpe Allocation', fontsize=9, fontweight='bold', color=DARK, pad=6)

# ── D: Min Vol Donut (row 2, col 1) ────────────────────────────────────────
axD = fig.add_subplot(gs[2, 1])
nz_mv = w_mv > 0.005
pie_lmv = [snames[i] if nz_mv[i] else '' for i in range(n)]
explmv  = [0.04 if w>0.005 else 0 for w in w_mv]
wD, tD, atD = axD.pie(
    w_mv, labels=pie_lmv, autopct='%1.0f%%',
    colors=PALETTE[:n], startangle=90, explode=explmv, pctdistance=0.72,
    wedgeprops=dict(linewidth=1.5, edgecolor=WH),
)
for t in tD: t.set_color(DARK); t.set_fontsize(8); t.set_fontweight('bold')
for at in atD: at.set_fontsize(8); at.set_fontweight('bold'); at.set_color(WH)
cD = plt.Circle((0,0), 0.52, color=WH, linewidth=1.5, ec=BORDER); axD.add_artist(cD)
axD.text(0, 0.1, 'Min Volatility', ha='center', va='center', fontsize=7.5, color='#555555')
axD.text(0, -0.12, f'Vol = {v_mv:.1%}', ha='center', va='center',
         fontsize=9.5, color='royalblue', fontweight='bold')
axD.set_title('Min Volatility Allocation', fontsize=9, fontweight='bold', color=DARK, pad=6)

# ── E: Cumulative Growth (row 2, col 2) ────────────────────────────────────
axE = fig.add_subplot(gs[2, 2])
for i, t in enumerate(available):
    axE.plot(cum_g.index, cum_g[t], color=PALETTE[i%len(PALETTE)],
             linewidth=1.3, alpha=0.85, label=snames[i])
axE.plot(port_cum.index, port_cum.values, color='#B8860B',
         linewidth=2.2, linestyle='--', label='Max Sharpe Portfolio', zorder=5)
axE.axhline(100, color='#AAAAAA', linewidth=0.9, linestyle=':')
axE.set_xlabel('Date', fontsize=8)
axE.set_ylabel('₹100 Invested', fontsize=8)
axE.set_title('Cumulative Growth (₹100)', fontsize=9, fontweight='bold', color=DARK, pad=6)
axE.legend(fontsize=6, loc='upper left', ncol=1, framealpha=0.9)
axE.grid(True, alpha=0.35, linestyle='--', color='#DDDDDD')
axE.tick_params(labelsize=7)
plt.setp(axE.get_xticklabels(), rotation=25, ha='right')
for sp in axE.spines.values(): sp.set_color(BORDER)

# ── F: Summary Table (bottom strip) ────────────────────────────────────────
# Drawn as text lines for compatibility & clarity
table_top = 0.058
col_x     = [0.05, 0.24, 0.42, 0.60, 0.78]
headers   = ['Metric', 'Max Sharpe ★', 'Min Volatility ■', 'Equal Weight ▲', '']
rows = [
    ['Expected Return (p.a.)',  f'{r_sh:.2%}', f'{r_mv:.2%}', f'{r_eq:.2%}', ''],
    ['Volatility (p.a.)',       f'{v_sh:.2%}', f'{v_mv:.2%}', f'{v_eq:.2%}', ''],
    ['Sharpe Ratio',            f'{sr_sh:.3f}',f'{sr_mv:.3f}',f'{sr_eq:.3f}',''],
    ['─── Asset Weights ───',   '',  '',  '', ''],
]
for i,sn in enumerate(snames):
    rows.append([sn, f'{w_sh[i]:.1%}', f'{w_mv[i]:.1%}', f'{w_eq[i]:.1%}', ''])

# Header bar
ax_tbl_hdr = fig.add_axes([0.04, table_top+0.020, 0.92, 0.016])
ax_tbl_hdr.set_facecolor(HEADER_BG); ax_tbl_hdr.axis('off')
for hx, h in zip(col_x, headers):
    fig.text(hx, table_top+0.028, h, ha='left', va='center',
             fontsize=8, fontweight='bold', color='white')

# Row data
row_colors = [WH, ALT_ROW]
for ri, row in enumerate(rows):
    ry = table_top + 0.016 - ri * 0.0135
    bg = row_colors[ri % 2]
    ax_row = fig.add_axes([0.04, ry - 0.002, 0.92, 0.013])
    ax_row.set_facecolor(bg); ax_row.axis('off')
    bold = (ri == 3)  # divider row
    italic_col = (ri >= 4)  # weight rows
    for hx, cell in zip(col_x, row):
        clr = '#333333'
        if ri == 0 and hx == col_x[1]: clr = '#8B6914'
        if ri == 2 and hx == col_x[1]: clr = '#8B6914'
        fig.text(hx, ry + 0.0045, cell, ha='left', va='center',
                 fontsize=7.5, color=clr,
                 fontstyle='italic' if italic_col else 'normal',
                 fontweight='bold' if bold else 'normal')

# Footer
fig.text(0.5, 0.012,
         f'Generated: {END_DATE}   |   Source: Yahoo Finance   |   '
         f'Risk-Free Rate: {RISK_FREE_RATE:.2%} (India 10-Yr G-Sec)   |   '
         f'45% maximum weight cap applied   |   10,000 Monte Carlo simulations',
         ha='center', va='bottom', fontsize=7, color='#888888',
         style='italic')

# Save
pdf_path = os.path.join(OUTPUT_DIR, 'MPT_Indian_ETF_Dashboard_WHITE.pdf')
fig.savefig(pdf_path, dpi=200, bbox_inches='tight', facecolor=WH, format='pdf')
plt.close(fig)
print(f"\n✅  White-background PDF saved:\n    {pdf_path}")
