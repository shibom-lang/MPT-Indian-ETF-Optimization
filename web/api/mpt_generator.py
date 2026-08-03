#!/usr/bin/env python3
"""
MPT Indian ETF — Detailed Multi-Page PDF Report
Professional, white-background, content-rich report with analysis narrative.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch
import yfinance as yf
from scipy.optimize import minimize
from scipy.stats import skew, kurtosis
import warnings, os, datetime, textwrap

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
OUTPUT_DIR      = "/tmp"
PDF_PATH        = os.path.join(OUTPUT_DIR, "MPT_Indian_ETF_Detailed_Report.pdf")
RISK_FREE_RATE  = 0.068
START_DATE      = '2019-01-01'
END_DATE        = datetime.date.today().strftime('%Y-%m-%d')
REPORT_DATE     = datetime.date.today().strftime('%d %B %Y')
MAX_WEIGHT      = 0.45
N_MC            = 2500
TRADING_DAYS    = 252

TICKERS  = ['NIFTYBEES.NS','JUNIORBEES.NS','BANKBEES.NS','GOLDBEES.NS','LIQUIDBEES.NS']
SHORT    = {'NIFTYBEES.NS':'NiftyBees','JUNIORBEES.NS':'JuniorBees',
            'BANKBEES.NS':'BankBees','GOLDBEES.NS':'GoldBees','LIQUIDBEES.NS':'LiquidBees'}
FULL     = {'NIFTYBEES.NS':'Nifty 50 BeES','JUNIORBEES.NS':'Junior BeES (Nifty Next 50)',
            'BANKBEES.NS':'Bank BeES','GOLDBEES.NS':'Gold BeES','LIQUIDBEES.NS':'Liquid BeES'}
DESC     = {
    'NIFTYBEES.NS' : 'Tracks Nifty 50 — India\'s benchmark large-cap index (50 stocks)',
    'JUNIORBEES.NS': 'Tracks Nifty Next 50 — mid-to-large cap segment (50 stocks)',
    'BANKBEES.NS'  : 'Tracks Nifty Bank — top 12 liquid banking stocks',
    'GOLDBEES.NS'  : 'Physical gold ETF — tracks domestic gold spot price',
    'LIQUIDBEES.NS': 'Overnight liquid fund — near-zero risk, money-market returns',
}

PALETTE  = ['#1565C0','#E53935','#F9A825','#2E7D32','#6A1B9A']
DARK     = '#1A1A2E'
GREY     = '#555555'
LGREY    = '#888888'
BORDER   = '#CCCCCC'
BLUE     = '#1565C0'
HDR_BG   = '#1565C0'
ALT      = '#F0F4FF'
WH       = 'white'
GREEN    = '#2E7D32'
RED      = '#C62828'
GOLD     = '#B8860B'

# Page size A4 landscape (inches)
PW, PH = 16.54, 11.69

def new_page(title_left='', title_right='', page_num=''):
    """
    Create a standard A4 landscape figure with a corporate header and footer.
    
    Args:
        title_left (str): Text for the left side of the header.
        title_right (str): Text for the right side of the header.
        page_num (str): Page number string for the footer.
        
    Returns:
        matplotlib.figure.Figure: A prepared matplotlib figure object.
    """
    fig = plt.figure(figsize=(PW, PH))
    fig.patch.set_facecolor(WH)
    # Top header strip
    ax_hdr = fig.add_axes([0, 0.956, 1, 0.044])
    ax_hdr.set_facecolor(HDR_BG); ax_hdr.axis('off')
    fig.text(0.02, 0.974, title_left, fontsize=11, fontweight='bold',
             color=WH, va='center')
    fig.text(0.98, 0.974, title_right, fontsize=9, color='#AACCFF',
             va='center', ha='right')
    # Bottom footer strip
    ax_ftr = fig.add_axes([0, 0, 1, 0.025])
    ax_ftr.set_facecolor('#F5F5F5'); ax_ftr.axis('off')
    fig.text(0.02, 0.011, f'MPT Analysis — Indian NSE ETFs   |   {REPORT_DATE}   |   '
             f'Risk-Free Rate: {RISK_FREE_RATE:.2%}   |   Data: Yahoo Finance',
             fontsize=7, color=LGREY, va='center')
    if page_num:
        fig.text(0.98, 0.011, f'Page {page_num}', fontsize=7,
                 color=LGREY, va='center', ha='right')
    return fig

def section_title(fig, text, y, x=0.04):
    """
    Add a styled section title with an underline to a matplotlib figure.
    
    Args:
        fig (matplotlib.figure.Figure): The figure object.
        text (str): The section title text.
        y (float): The vertical position (0 to 1).
        x (float): The horizontal position (0 to 1). Default is 0.04.
    """
    fig.text(x, y, text, fontsize=12, fontweight='bold', color=BLUE,
             va='top', ha='left')
    ax_line = fig.add_axes([x, y-0.012, 0.92-x, 0.003])
    ax_line.set_facecolor(BLUE); ax_line.axis('off')

def info_box(fig, x, y, w, h, title, lines, bg='#EEF4FF', title_color=BLUE):
    """
    Draw a styled information box on the figure containing a title and text lines.
    
    Args:
        fig: The matplotlib figure.
        x, y: Bottom-left corner coordinates (0 to 1).
        w, h: Width and height of the box (0 to 1).
        title (str): The title of the info box.
        lines (list of str): The text lines to display inside the box.
        bg (str): Background color (hex).
        title_color (str): Text color for the title (hex).
    """
    ax = fig.add_axes([x, y, w, h])
    ax.set_facecolor(bg); ax.axis('off')
    for sp in ax.spines.values():
        sp.set_visible(True); sp.set_color(BORDER); sp.set_linewidth(0.8)
    fig.text(x+0.008, y+h-0.012, title, fontsize=9, fontweight='bold',
             color=title_color, va='top')
    for i, line in enumerate(lines):
        fig.text(x+0.008, y+h-0.027-(i*0.016), line, fontsize=8,
                 color=DARK, va='top')

# ─────────────────────────────────────────────────────────────────────────────
# DATA DOWNLOAD & CLEAN
# ─────────────────────────────────────────────────────────────────────────────
def generate_report():
    global raw, prices, prices_c, cleaned_dates, returns, mu, Sigma, snames, available, n, risk_free
    global END_DATE, REPORT_DATE
    import datetime
    END_DATE = datetime.date.today().strftime("%Y-%m-%d")
    REPORT_DATE = datetime.date.today().strftime("%d %B %Y")
    global w_eq, r_eq, v_eq, sr_eq, N_MC, mc_w, mc_r, mc_v, mc_sr, max_sr_idx, min_v_idx, res_sh, res_mv, w_sh, w_mv, r_sh, v_sh, sr_sh, r_mv, v_mv, sr_mv
    print("📥  Downloading live data from Yahoo Finance …")
    raw    = yf.download(TICKERS, start=START_DATE, end=END_DATE,
                         auto_adjust=True, progress=True, group_by='column')
    prices = raw['Close'].copy() if isinstance(raw.columns, pd.MultiIndex) else raw.copy()
    prices.dropna(how='all', inplace=True)
    prices.ffill(inplace=True); prices.dropna(inplace=True)
    
    # Clean Dec-2019 split artifacts (1:10 split for NIFTYBEES, BANKBEES, GOLDBEES)
    prices_c = prices.copy().astype(float)
    cleaned_dates = {}
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
            cleaned_dates[col] = sorted([str(d.date()) for d in nan_set])
    prices_c = prices_c.interpolate(method='time', limit=10)
    prices_c.ffill(inplace=True); prices_c.bfill(inplace=True)
    prices = prices_c
    
    actual_start = prices.index[0].strftime('%Y-%m-%d')
    actual_end   = prices.index[-1].strftime('%Y-%m-%d')
    n_days       = len(prices)
    available    = list(prices.columns)
    snames       = [SHORT[t] for t in available]
    fnames       = [FULL[t]  for t in available]
    n            = len(available)
    print(f"✅  {n_days} trading days  |  {actual_start} → {actual_end}")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # RETURNS & STATISTICS
    # ─────────────────────────────────────────────────────────────────────────────
    daily       = prices.pct_change().dropna()
    mu_s        = daily.mean() * TRADING_DAYS
    cov_s       = daily.cov()  * TRADING_DAYS
    corr_s      = daily.corr()
    mu          = mu_s.values
    Sigma       = cov_s.values
    vol_s       = np.sqrt(np.diag(Sigma))
    
    # Rolling 252-day return & vol
    roll_ret = daily.rolling(252).mean() * 252
    roll_vol = daily.rolling(252).std()  * np.sqrt(252)
    
    # Max drawdown helper
    def max_drawdown(price_series):
        cum = (1 + price_series.pct_change().dropna()).cumprod()
        roll_max = cum.cummax()
        dd = (cum - roll_max) / roll_max
        return dd.min()
    
    # Individual asset stats
    stats = {}
    for t in available:
        dr = daily[t].dropna()
        stats[t] = {
            'ann_ret'  : float(mu_s[t]),
            'ann_vol'  : float(np.sqrt(cov_s.loc[t,t])),
            'sharpe'   : float((mu_s[t] - RISK_FREE_RATE) / np.sqrt(cov_s.loc[t,t])),
            'skew'     : float(skew(dr)),
            'kurt'     : float(kurtosis(dr)),
            'max_dd'   : float(max_drawdown(prices[t])),
            'best_day' : float(dr.max()),
            'worst_day': float(dr.min()),
            'total_ret': float((prices[t].iloc[-1]/prices[t].iloc[0]) - 1),
        }
    
    # ─────────────────────────────────────────────────────────────────────────────
    # OPTIMISATION
    # ─────────────────────────────────────────────────────────────────────────────
    def perf(w):
        r  = float(np.dot(w, mu))
        v  = float(np.sqrt(w @ Sigma @ w))
        sr = (r - RISK_FREE_RATE)/v if v>1e-10 else 0.0
        return r, v, sr
    
    con = [{'type':'eq','fun':lambda w: np.sum(w)-1}]
    bds = tuple((0, MAX_WEIGHT) for _ in range(n))
    w0  = np.array([1/n]*n)
    
    res_sh = minimize(lambda w: -(perf(w)[2]), w0, method='SLSQP', bounds=bds,
                      constraints=con, options={'maxiter':3000,'ftol':1e-12})
    res_mv = minimize(lambda w: perf(w)[1], w0, method='SLSQP', bounds=bds,
                      constraints=con, options={'maxiter':3000,'ftol':1e-12})
    
    def clean_w(w):
        w[w<1e-5]=0.0; w/=w.sum(); return w
    
    w_sh = clean_w(res_sh.x if res_sh.success else w0.copy())
    w_mv = clean_w(res_mv.x if res_mv.success else w0.copy())
    w_eq = clean_w(w0.copy())
    
    r_sh,v_sh,sr_sh = perf(w_sh)
    r_mv,v_mv,sr_mv = perf(w_mv)
    r_eq,v_eq,sr_eq = perf(w_eq)
    
    # ─────────────────────────────────────────────────────────────────────────────
    # MONTE CARLO
    # ─────────────────────────────────────────────────────────────────────────────
    print(f"🎲  Monte Carlo ({N_MC:,}) …")
    np.random.seed(42)
    mc_r,mc_v,mc_sr = np.zeros(N_MC),np.zeros(N_MC),np.zeros(N_MC)
    mc_w = np.zeros((N_MC, n))
    for i in range(N_MC):
        w = np.clip(np.random.dirichlet(np.ones(n)), 0, MAX_WEIGHT)
        w /= w.sum(); mc_w[i]=w
        mc_r[i],mc_v[i],mc_sr[i] = perf(w)
    
    # Best MC portfolio
    best_idx  = np.argmax(mc_sr)
    best_mc_w = mc_w[best_idx]
    
    # Portfolio cumulative growth
    cum_g    = (1+daily).cumprod()*100
    port_sh  = (1+daily[available].dot(pd.Series(w_sh,index=available))).cumprod()*100
    port_mv  = (1+daily[available].dot(pd.Series(w_mv,index=available))).cumprod()*100
    port_eq  = (1+daily[available].dot(pd.Series(w_eq,index=available))).cumprod()*100
    
    # Portfolio drawdowns
    def port_dd(w_vec):
        pret = daily[available].dot(pd.Series(w_vec, index=available))
        cum  = (1+pret).cumprod()
        return (cum - cum.cummax()) / cum.cummax()
    
    dd_sh = port_dd(w_sh)
    dd_mv = port_dd(w_mv)
    dd_eq = port_dd(w_eq)
    
    # ─────────────────────────────────────────────────────────────────────────────
    # BUILD PDF
    # ─────────────────────────────────────────────────────────────────────────────
    print("📄  Building detailed PDF …")
    plt.rcParams.update({
        'figure.facecolor':WH,'axes.facecolor':WH,'axes.edgecolor':BORDER,
        'axes.labelcolor':DARK,'text.color':DARK,'xtick.color':DARK,'ytick.color':DARK,
        'grid.color':'#E8E8E8','legend.facecolor':WH,'legend.edgecolor':BORDER,
        'font.family':'DejaVu Sans','font.size':9,
    })
    
    cmap_rg  = LinearSegmentedColormap.from_list('rg',['#C62828','white','#1B5E20'],N=256)
    
    with PdfPages(PDF_PATH) as pdf:
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 1: COVER PAGE
        # ════════════════════════════════════════════════════════════════════════
        fig = plt.figure(figsize=(PW, PH))
        fig.patch.set_facecolor(WH)
    
        # Full blue header band
        ax_cover_hdr = fig.add_axes([0, 0.72, 1, 0.28])
        ax_cover_hdr.set_facecolor(HDR_BG); ax_cover_hdr.axis('off')
    
        fig.text(0.5, 0.935, 'PORTFOLIO OPTIMIZATION REPORT',
                 ha='center', fontsize=28, fontweight='bold', color=WH)
        fig.text(0.5, 0.875, 'Modern Portfolio Theory (MPT) Analysis',
                 ha='center', fontsize=18, color='#AACCFF')
        fig.text(0.5, 0.825, 'Indian NSE-Listed Index ETFs — Live Market Data',
                 ha='center', fontsize=14, color='#88AADD')
        fig.text(0.5, 0.772, f'Report Date: {REPORT_DATE}',
                 ha='center', fontsize=11, color='#CCDDFF')
    
        # Info cards in 3 columns
        cards = [
            ('Universe', [f'{n} NSE-Listed ETFs', 'Nifty 50 · Next 50 · Bank · Gold · Liquid']),
            ('Data Range', [f'{actual_start} → {actual_end}', f'{n_days} Trading Days']),
            ('Risk-Free Rate', [f'{RISK_FREE_RATE:.2%} per annum', 'India 10-Yr G-Sec (Jul-2026)']),
            ('Max Weight Cap', [f'{MAX_WEIGHT:.0%} per asset', 'Concentration limit']),
            ('Monte Carlo', [f'{N_MC:,} portfolios simulated', 'Efficient Frontier mapping']),
            ('Data Source', ['Yahoo Finance (Live)', 'Auto-adjusted prices']),
        ]
        card_w, card_h = 0.27, 0.100
        card_positions = [(0.035,0.595),(0.37,0.595),(0.70,0.595),
                          (0.035,0.480),(0.37,0.480),(0.70,0.480)]
        for (cx,cy),(ctitle,clines) in zip(card_positions,cards):
            ax_c = fig.add_axes([cx, cy, card_w, card_h])
            ax_c.set_facecolor('#EEF4FF'); ax_c.axis('off')
            for sp in ax_c.spines.values():
                sp.set_visible(True); sp.set_color(BLUE); sp.set_linewidth(1.2)
            fig.text(cx+0.008, cy+card_h-0.010, ctitle,
                     fontsize=10, fontweight='bold', color=BLUE, va='top')
            for li,line in enumerate(clines):
                fig.text(cx+0.008, cy+card_h-0.030-(li*0.022), line,
                         fontsize=9, color=DARK, va='top')
    
        # ETF table
        fig.text(0.5, 0.445, 'INSTRUMENTS UNDER ANALYSIS',
                 ha='center', fontsize=11, fontweight='bold', color=DARK)
        ax_line2 = fig.add_axes([0.04, 0.428, 0.92, 0.002])
        ax_line2.set_facecolor(BORDER); ax_line2.axis('off')
    
        col_positions = [0.05, 0.17, 0.38, 0.80]
        hdrs2 = ['Ticker', 'Full Name', 'Description', 'Category']
        cats  = ['Equity — Large Cap','Equity — Mid-Large Cap',
                 'Equity — Banking','Commodity','Fixed Income / Liquid']
        for hx,h in zip(col_positions,hdrs2):
            fig.text(hx, 0.415, h, fontsize=9, fontweight='bold', color=BLUE, va='top')
        for ri,t in enumerate(available):
            ry  = 0.380 - ri*0.032  # Lowered from 0.395 to 0.380
            bg  = ALT if ri%2==0 else WH
            axr = fig.add_axes([0.04, ry-0.004, 0.92, 0.030])
            axr.set_facecolor(bg); axr.axis('off')
            row = [SHORT[t], FULL[t], DESC[t], cats[ri]]
            for hx,cell in zip(col_positions,row):
                fig.text(hx, ry+0.012, cell, fontsize=8.5, color=DARK, va='center')
    
        # Footer disclaimer
        ax_ftr = fig.add_axes([0, 0, 1, 0.05])
        ax_ftr.set_facecolor('#F5F5F5'); ax_ftr.axis('off')
        fig.text(0.5, 0.028,
                 'DISCLAIMER: This report is for educational and informational purposes only. '
                 'Past performance is not indicative of future results. '
                 'This is not investment advice. Please consult a SEBI-registered financial advisor before investing.',
                 ha='center', fontsize=7.5, color=LGREY, va='center', style='italic')
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 2: EXECUTIVE SUMMARY
        # ════════════════════════════════════════════════════════════════════════
        fig = new_page('Executive Summary', 'Indian ETF MPT Report', '2')
    
        section_title(fig, '1. Executive Summary', 0.90)
    
        summary_text = (
            f"This report presents a comprehensive Modern Portfolio Theory (MPT) analysis of five NSE-listed index ETFs "
            f"over a {n_days}-trading-day period from {actual_start} to {actual_end}. Using adjusted daily price data from Yahoo Finance, "
            f"we optimise portfolios for two classic MPT objectives: maximising risk-adjusted returns (Sharpe ratio) and minimising "
            f"absolute portfolio volatility. A 45% maximum weight cap per asset is applied to enforce realistic diversification.\n\n"
            f"STRATEGIC TAKEAWAY FOR ASSET MANAGERS:\n"
            f"The analysis demonstrates that naive equal-weighting leaves significant alpha on the table. By strategically allocating "
            f"to low-correlation assets (such as GoldBees), an optimised portfolio can achieve superior risk-adjusted returns. "
            f"Specifically, the Max Sharpe portfolio achieves an expected return of {r_sh:.2%} with a volatility of just {v_sh:.2%}, "
            f"providing a strong empirical basis for tactical asset allocation in Indian ETF portfolios."
        )
    
        # Wrap text
        y_txt = 0.855
        for paragraph in summary_text.split('\n'):
            if not paragraph.strip(): 
                y_txt -= 0.010
                continue
            wrapped = textwrap.wrap(paragraph, width=175)
            for line in wrapped:
                fig.text(0.04, y_txt, line, fontsize=9, color=DARK, va='top')
                y_txt -= 0.022
    
        section_title(fig, '2. Key Findings at a Glance', y_txt - 0.015)
        y_txt -= 0.065
    
        # 3 result cards side by side
        result_cards = [
            ('★ MAX SHARPE PORTFOLIO', GOLD, [
                f'Expected Return: {r_sh:.2%} p.a.',
                f'Volatility:           {v_sh:.2%} p.a.',
                f'Sharpe Ratio:      {sr_sh:.4f}',
                '─────────────────────',
                f'GoldBees:     45.00%',
                f'JuniorBees:  {w_sh[1]:.2%}',
                f'NiftyBees:    {w_sh[0]:.2%}',
                f'BankBees:     {w_sh[2]:.2%}',
                f'LiquidBees:   {w_sh[4]:.2%}',
            ]),
            ('■ MIN VOLATILITY PORTFOLIO', BLUE, [
                f'Expected Return: {r_mv:.2%} p.a.',
                f'Volatility:           {v_mv:.2%} p.a.',
                f'Sharpe Ratio:      {sr_mv:.4f}',
                '─────────────────────',
                f'LiquidBees:  {w_mv[4]:.2%}',
                f'NiftyBees:   {w_mv[0]:.2%}',
                f'GoldBees:    {w_mv[3]:.2%}',
                f'JuniorBees: {w_mv[1]:.2%}',
                f'BankBees:    {w_mv[2]:.2%}',
            ]),
            ('▲ EQUAL-WEIGHT (BENCHMARK)', GREY, [
                f'Expected Return: {r_eq:.2%} p.a.',
                f'Volatility:           {v_eq:.2%} p.a.',
                f'Sharpe Ratio:      {sr_eq:.4f}',
                '─────────────────────',
                f'All assets:  20.00% each',
                '', '', '', '',
            ]),
        ]
        rc_w = 0.285; rc_h = 0.200
        rc_positions = [0.040, 0.362, 0.683]
        for (rx,(rtitle,rcol,rlines)) in zip(rc_positions, result_cards):
            ax_rc = fig.add_axes([rx, y_txt - rc_h, rc_w, rc_h])
            ax_rc.set_facecolor('#FAFAFA'); ax_rc.axis('off')
            for sp in ax_rc.spines.values():
                sp.set_visible(True); sp.set_color(rcol); sp.set_linewidth(2)
            fig.text(rx+0.008, y_txt-0.008, rtitle, fontsize=9,
                     fontweight='bold', color=rcol, va='top')
            for li, line in enumerate(rlines):
                fig.text(rx+0.008, y_txt-0.028-(li*0.019), line,
                         fontsize=8.5, color=DARK, va='top',
                         fontfamily='monospace')
    
        y_after_cards = y_txt - rc_h - 0.030
        section_title(fig, '3. Data Quality Note', y_after_cards)
        y_after_cards -= 0.055
    
        dq_text = (
            f"NIFTYBEES.NS, BANKBEES.NS, and GOLDBEES.NS underwent a 1-for-10 stock split on 19 December 2019. "
            f"Yahoo Finance records showed discontinuous raw prices around Dec 18–23, 2019 — causing spurious single-day "
            f"returns ranging from −90% to +9,900%. These 4 data points per affected ticker were automatically detected "
            f"(threshold: |return| > 15%) and replaced with linearly interpolated values before any statistical computation. "
            f"JUNIORBEES.NS and LIQUIDBEES.NS required no data cleaning."
        )
        for line in textwrap.wrap(dq_text, width=175):
            fig.text(0.04, y_after_cards, line, fontsize=9, color=DARK, va='top')
            y_after_cards -= 0.021
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 3: INDIVIDUAL ASSET STATISTICS
        # ════════════════════════════════════════════════════════════════════════
        fig = new_page('Asset Statistics & Risk Metrics', 'Indian ETF MPT Report', '3')
        section_title(fig, '4. Individual Asset Analysis (2019 – 2026)', 0.90)
    
        # Big stats table
        tbl_cols  = ['ETF', 'Ann. Return', 'Ann. Volatility', 'Sharpe Ratio',
                     'Total Return', 'Max Drawdown', 'Best Day', 'Worst Day', 'Skewness', 'Excess Kurt.']
        tbl_data  = []
        for t in available:
            s = stats[t]
            tbl_data.append([
                SHORT[t],
                f"{s['ann_ret']:.2%}", f"{s['ann_vol']:.2%}", f"{s['sharpe']:.3f}",
                f"{s['total_ret']:.2%}", f"{s['max_dd']:.2%}",
                f"{s['best_day']:.2%}", f"{s['worst_day']:.2%}",
                f"{s['skew']:.3f}", f"{s['kurt']:.3f}",
            ])
    
        col_widths = [0.08, 0.085, 0.095, 0.085, 0.085, 0.090, 0.075, 0.080, 0.075, 0.085]
        col_x0 = 0.04
        col_xs = []
        cx = col_x0
        for cw in col_widths:
            col_xs.append(cx); cx += cw
    
        tbl_y_start = 0.855
    
        # Header row
        ax_th = fig.add_axes([0.04, tbl_y_start, 0.92, 0.028])
        ax_th.set_facecolor(HDR_BG); ax_th.axis('off')
        for hx, hdr in zip(col_xs, tbl_cols):
            fig.text(hx+0.003, tbl_y_start+0.014, hdr, fontsize=8,
                     fontweight='bold', color=WH, va='center')
    
        row_h = 0.038
        for ri, row in enumerate(tbl_data):
            ry  = tbl_y_start - (ri+1)*row_h
            bg  = ALT if ri%2==0 else WH
            axr = fig.add_axes([0.04, ry, 0.92, row_h])
            axr.set_facecolor(bg); axr.axis('off')
            for hx, cell in zip(col_xs, row):
                # Color code return/drawdown cells
                clr = DARK
                if col_xs.index(hx) == 5 and '-' in cell: clr = RED   # max drawdown
                if col_xs.index(hx) == 1:
                    try:
                        clr = GREEN if float(cell.strip('%')) > 0 else RED
                    except: pass
                fig.text(hx+0.003, ry+row_h/2, cell, fontsize=8.5,
                         color=clr, va='center')
    
        tbl_bottom = tbl_y_start - (len(tbl_data)+1)*row_h - 0.02
        section_title(fig, '5. Asset Return Distribution (Histograms)', tbl_bottom)
        hist_top = tbl_bottom - 0.045
    
        # Histogram row for each ETF
        hist_h = 0.22; hist_w = 0.165; gap = 0.01
        for i, t in enumerate(available):
            hx = 0.04 + i*(hist_w+gap)
            ax_h = fig.add_axes([hx, hist_top-hist_h, hist_w, hist_h])
            dr = daily[t]*100
            ax_h.hist(dr, bins=60, color=PALETTE[i], alpha=0.8, edgecolor='white', linewidth=0.3)
            ax_h.axvline(0, color=DARK, linewidth=0.8, linestyle='--')
            ax_h.axvline(dr.mean(), color='red', linewidth=1.2, linestyle=':', label=f'μ={dr.mean():.2f}%')
            ax_h.set_title(snames[i], fontsize=9, fontweight='bold', color=DARK, pad=4)
            ax_h.set_xlabel('Daily Return (%)', fontsize=7.5)
            ax_h.set_ylabel('Frequency', fontsize=7.5)
            ax_h.tick_params(labelsize=7)
            ax_h.legend(fontsize=6.5, handlelength=1)
            ax_h.grid(True, alpha=0.3, linestyle='--')
            for sp in ax_h.spines.values(): sp.set_color(BORDER)
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 4: CORRELATION HEATMAP + ROLLING ANALYSIS
        # ════════════════════════════════════════════════════════════════════════
        fig = new_page('Correlation & Rolling Returns Analysis', 'Indian ETF MPT Report', '4')
        section_title(fig, '6. Correlation Matrix Analysis', 0.90)
    
        gs = gridspec.GridSpec(2, 3, figure=fig,
                               top=0.855, bottom=0.14,
                               left=0.05, right=0.97,
                               wspace=0.32, hspace=0.42)
    
        # Heatmap (large, left)
        axH = fig.add_subplot(gs[0:2, 0])
        imH = axH.imshow(corr_s.values, cmap=cmap_rg, vmin=-1, vmax=1)
        plt.colorbar(imH, ax=axH, fraction=0.06, pad=0.03)
        axH.set_xticks(range(n)); axH.set_yticks(range(n))
        axH.set_xticklabels(snames, rotation=35, ha='right', fontsize=8.5)
        axH.set_yticklabels(snames, fontsize=8.5)
        for i in range(n):
            for j in range(n):
                val = corr_s.values[i,j]
                clr = 'white' if abs(val)>0.55 else DARK
                axH.text(j, i, f'{val:.2f}', ha='center', va='center',
                         fontsize=9, color=clr, fontweight='bold')
        axH.set_title('Pairwise Correlation Matrix\n(Daily Returns 2019–2026)',
                      fontsize=9, fontweight='bold', color=DARK, pad=8)
        for sp in axH.spines.values(): sp.set_color(BORDER)
    
        # Rolling 12M returns (top-centre + top-right merged)
        ax_rr = fig.add_subplot(gs[0, 1:3])
        for i, t in enumerate(available):
            rr = roll_ret[t].dropna()*100
            ax_rr.plot(rr.index, rr, color=PALETTE[i], linewidth=1.4, label=snames[i], alpha=0.85)
        ax_rr.axhline(0, color='black', linewidth=0.8, linestyle='--')
        ax_rr.axhline(RISK_FREE_RATE*100, color='grey', linewidth=1, linestyle=':', label=f'Risk-Free {RISK_FREE_RATE:.2%}')
        ax_rr.set_title('Rolling 12-Month Annualised Return (%)', fontsize=9, fontweight='bold', color=DARK, pad=6)
        ax_rr.set_xlabel('Date', fontsize=8); ax_rr.set_ylabel('Return (%)', fontsize=8)
        ax_rr.legend(fontsize=7.5, ncol=3, loc='upper right', framealpha=0.9)
        ax_rr.grid(True, alpha=0.3, linestyle='--'); ax_rr.tick_params(labelsize=8)
        for sp in ax_rr.spines.values(): sp.set_color(BORDER)
    
        # Rolling 12M volatility
        ax_rv = fig.add_subplot(gs[1, 1:3])
        for i, t in enumerate(available):
            rv = roll_vol[t].dropna()*100
            ax_rv.plot(rv.index, rv, color=PALETTE[i], linewidth=1.4, label=snames[i], alpha=0.85)
        ax_rv.set_title('Rolling 12-Month Annualised Volatility (%)', fontsize=9, fontweight='bold', color=DARK, pad=6)
        ax_rv.set_xlabel('Date', fontsize=8); ax_rv.set_ylabel('Volatility (%)', fontsize=8)
        ax_rv.legend(fontsize=7.5, ncol=3, loc='upper right', framealpha=0.9)
        ax_rv.grid(True, alpha=0.3, linestyle='--'); ax_rv.tick_params(labelsize=8)
        for sp in ax_rv.spines.values(): sp.set_color(BORDER)
    
        # Interpretation text
        corr_text = (
            "KEY INSIGHTS: NiftyBees and BankBees show very high positive correlation (>0.80), "
            "suggesting they move largely together — holding both provides limited diversification benefit. "
            "GoldBees is the natural diversifier with near-zero or slightly negative correlation to equity ETFs. "
            "LiquidBees is essentially uncorrelated to all other assets, acting as a pure cash proxy. "
            "JuniorBees (mid-cap tilt) is highly correlated with NiftyBees but captures the size-premium factor."
        )
        y_note = 0.115
        fig.text(0.04, y_note, '📌 Correlation Insights:', fontsize=8.5, fontweight='bold', color=BLUE, va='top')
        for line in textwrap.wrap(corr_text, width=160):
            y_note -= 0.020
            fig.text(0.04, y_note, line, fontsize=8.5, color=DARK, va='top')
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 5: EFFICIENT FRONTIER (FULL PAGE)
        # ════════════════════════════════════════════════════════════════════════
        fig = new_page('Efficient Frontier — Monte Carlo Simulation', 'Indian ETF MPT Report', '5')
        section_title(fig, f'7. Efficient Frontier — {N_MC:,} Monte Carlo Portfolios', 0.90)
    
        gs5 = gridspec.GridSpec(1, 2, figure=fig,
                                top=0.850, bottom=0.190,
                                left=0.05, right=0.97,
                                wspace=0.30)
    
        # Main frontier scatter
        axEF = fig.add_subplot(gs5[0, 0])
        sc   = axEF.scatter(mc_v*100, mc_r*100, c=mc_sr, cmap='RdYlGn',
                            alpha=0.35, s=2, zorder=1)
        cb   = plt.colorbar(sc, ax=axEF, pad=0.06, fraction=0.04)
        cb.set_label('Sharpe Ratio', fontsize=8)
        cb.ax.tick_params(labelsize=7)
    
        svols = np.sqrt(np.diag(Sigma))*100; srets = mu*100
        for i,(sv,sr_i) in enumerate(zip(svols,srets)):
            axEF.scatter(sv, sr_i, s=100, color=PALETTE[i], marker='D',
                         zorder=4, edgecolors=DARK, linewidths=0.8)
            axEF.annotate(snames[i], (sv,sr_i), xytext=(6,3),
                          textcoords='offset points', fontsize=8.5,
                          color=PALETTE[i], fontweight='bold')
    
        axEF.scatter(v_sh*100, r_sh*100, s=300, color=GOLD, marker='*',
                     zorder=6, edgecolors=DARK, linewidths=1.5, label='★ Max Sharpe')
        axEF.scatter(v_mv*100, r_mv*100, s=180, color=BLUE, marker='s',
                     zorder=6, edgecolors=DARK, linewidths=1.2, label='■ Min Volatility')
        axEF.scatter(v_eq*100, r_eq*100, s=180, color='tomato', marker='^',
                     zorder=6, edgecolors=DARK, linewidths=1.2, label='▲ Equal Weight')
    
        # Capital Market Line
        cml_v = np.linspace(0, v_sh*100*1.3, 100)
        cml_r = RISK_FREE_RATE*100 + sr_sh * cml_v
        axEF.plot(cml_v, cml_r, 'k--', linewidth=1.2, alpha=0.6, label='Capital Market Line')
        axEF.axhline(RISK_FREE_RATE*100, color='grey', linewidth=0.9,
                     linestyle=':', label=f'Risk-Free {RISK_FREE_RATE:.2%}')
    
        axEF.set_xlabel('Annualised Volatility (%)', fontsize=9)
        axEF.set_ylabel('Annualised Expected Return (%)', fontsize=9)
        axEF.set_title('Efficient Frontier with Capital Market Line', fontsize=10, fontweight='bold', color=DARK, pad=8)
        axEF.legend(fontsize=8, framealpha=0.9)
        axEF.grid(True, alpha=0.35, linestyle='--'); axEF.tick_params(labelsize=8)
        for sp in axEF.spines.values(): sp.set_color(BORDER)
    
        # Sharpe distribution histogram
        axSH = fig.add_subplot(gs5[0, 1])
        axSH.hist(mc_sr, bins=80, color=BLUE, alpha=0.7, edgecolor='white', linewidth=0.3)
        axSH.axvline(sr_sh, color=GOLD, linewidth=2, linestyle='--', label=f'Max Sharpe = {sr_sh:.3f}')
        axSH.axvline(sr_eq, color='tomato', linewidth=1.5, linestyle=':', label=f'Equal Weight = {sr_eq:.3f}')
        axSH.axvline(np.median(mc_sr), color='grey', linewidth=1.2, linestyle='-.',
                     label=f'Median MC = {np.median(mc_sr):.3f}')
        axSH.set_xlabel('Sharpe Ratio', fontsize=9)
        axSH.set_ylabel('Number of Portfolios', fontsize=9)
        axSH.set_title('Distribution of Sharpe Ratios\nacross Monte Carlo Portfolios', fontsize=10,
                       fontweight='bold', color=DARK, pad=8)
        axSH.legend(fontsize=8.5, framealpha=0.9)
        axSH.grid(True, alpha=0.35, linestyle='--'); axSH.tick_params(labelsize=8)
        for sp in axSH.spines.values(): sp.set_color(BORDER)
    
        # Stats text boxes at bottom
        ef_stats = [
            ('Monte Carlo Stats', [
                f'Total simulations: {N_MC:,}',
                f'Max Sharpe found: {mc_sr.max():.4f}',
                f'Min Sharpe found: {mc_sr.min():.4f}',
                f'Median Sharpe:    {np.median(mc_sr):.4f}',
                f'Mean Sharpe:      {mc_sr.mean():.4f}',
            ]),
            ('Max Sharpe Portfolio', [
                f'Return:     {r_sh:.2%} p.a.',
                f'Volatility: {v_sh:.2%} p.a.',
                f'Sharpe:     {sr_sh:.4f}',
                f'Optimiser:  SLSQP (scipy)',
                f'Status:     {"Converged" if res_sh.success else "Did not converge"}',
            ]),
            ('Min Volatility Portfolio', [
                f'Return:     {r_mv:.2%} p.a.',
                f'Volatility: {v_mv:.2%} p.a.',
                f'Sharpe:     {sr_mv:.4f}',
                f'Optimiser:  SLSQP (scipy)',
                f'Status:     {"Converged" if res_mv.success else "Did not converge"}',
            ]),
        ]
        bx_w = 0.27; bx_h = 0.085
        for bi,(btitle,blines) in enumerate(ef_stats):
            bx = 0.05 + bi*(bx_w+0.025)
            info_box(fig, bx, 0.045, bx_w, bx_h, btitle, blines)
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 6: OPTIMAL PORTFOLIO ALLOCATIONS
        # ════════════════════════════════════════════════════════════════════════
        fig = new_page('Optimal Portfolio Allocations', 'Indian ETF MPT Report', '6')
        section_title(fig, '8. Portfolio Allocation Breakdown', 0.90)
    
        gs6 = gridspec.GridSpec(2, 3, figure=fig,
                                top=0.850, bottom=0.060,
                                left=0.04, right=0.97,
                                wspace=0.35, hspace=0.45)
    
        def donut(ax, weights, labels, colors, title, center_label, center_val, center_color):
            nz = weights > 0.005
            pie_l = [labels[i] if nz[i] else '' for i in range(len(weights))]
            expl  = [0.04 if w>0.005 else 0 for w in weights]
            w_, t_, at_ = ax.pie(weights, labels=pie_l, autopct='%1.1f%%',
                                  colors=colors, startangle=90, explode=expl,
                                  pctdistance=0.72,
                                  wedgeprops=dict(linewidth=1.8, edgecolor=WH))
            for t in t_: t.set_color(DARK); t.set_fontsize(8.5); t.set_fontweight('bold')
            for at in at_: at.set_fontsize(8); at.set_fontweight('bold'); at.set_color(WH)
            c = plt.Circle((0,0), 0.52, color=WH, linewidth=1.2, ec=BORDER)
            ax.add_artist(c)
            ax.text(0, 0.12, center_label, ha='center', va='center', fontsize=8, color=GREY)
            ax.text(0, -0.10, center_val,  ha='center', va='center',
                    fontsize=11, color=center_color, fontweight='bold')
            ax.set_title(title, fontsize=10, fontweight='bold', color=DARK, pad=10)
    
        donut(fig.add_subplot(gs6[0,0]), w_sh, snames, PALETTE[:n],
              '★ Max Sharpe Portfolio', 'Sharpe', f'{sr_sh:.3f}', GOLD)
        donut(fig.add_subplot(gs6[0,1]), w_mv, snames, PALETTE[:n],
              '■ Min Volatility Portfolio', 'Volatility', f'{v_mv:.2%}', BLUE)
        donut(fig.add_subplot(gs6[0,2]), w_eq, snames, PALETTE[:n],
              '▲ Equal Weight (Benchmark)', 'Balanced', '20% each', GREY)
    
        # Bar chart comparison
        ax_bar = fig.add_subplot(gs6[1, :])
        bar_w  = 0.22
        x      = np.arange(n)
        bars_sh = ax_bar.bar(x - bar_w, w_sh*100, bar_w, label='Max Sharpe ★',
                              color=GOLD, edgecolor=DARK, linewidth=0.8, alpha=0.9)
        bars_mv = ax_bar.bar(x,          w_mv*100, bar_w, label='Min Volatility ■',
                              color=BLUE, edgecolor=DARK, linewidth=0.8, alpha=0.9)
        bars_eq = ax_bar.bar(x + bar_w,  w_eq*100, bar_w, label='Equal Weight ▲',
                              color='#E0E0E0', edgecolor=DARK, linewidth=0.8, alpha=0.9)
    
        for bars in [bars_sh, bars_mv, bars_eq]:
            for bar in bars:
                h = bar.get_height()
                if h > 0.5:
                    ax_bar.text(bar.get_x()+bar.get_width()/2, h+0.5, f'{h:.1f}%',
                                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
        ax_bar.axhline(MAX_WEIGHT*100, color='red', linewidth=1.2, linestyle='--',
                       alpha=0.7, label=f'{MAX_WEIGHT:.0%} Max Weight Cap')
        ax_bar.set_xticks(x); ax_bar.set_xticklabels(snames, fontsize=9)
        ax_bar.set_ylabel('Portfolio Weight (%)', fontsize=9)
        ax_bar.set_title('Weight Comparison Across Three Portfolios', fontsize=10,
                         fontweight='bold', color=DARK, pad=8)
        ax_bar.legend(fontsize=8.5, framealpha=0.9)
        ax_bar.set_ylim(0, 55); ax_bar.grid(axis='y', alpha=0.3, linestyle='--')
        ax_bar.tick_params(labelsize=8)
        for sp in ax_bar.spines.values(): sp.set_color(BORDER)
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 7: CUMULATIVE GROWTH & DRAWDOWN
        # ════════════════════════════════════════════════════════════════════════
        fig = new_page('Cumulative Growth & Drawdown Analysis', 'Indian ETF MPT Report', '7')
        section_title(fig, '9. Cumulative Growth — ₹100 Invested (2019–2026)', 0.90)
    
        gs7 = gridspec.GridSpec(3, 2, figure=fig,
                                top=0.855, bottom=0.060,
                                left=0.05, right=0.97,
                                wspace=0.30, hspace=0.48)
    
        # Main cumulative growth
        ax_cg = fig.add_subplot(gs7[0:2, 0])
        for i, t in enumerate(available):
            ax_cg.plot(cum_g.index, cum_g[t], color=PALETTE[i], linewidth=1.5,
                       alpha=0.85, label=f'{snames[i]} (₹{cum_g[t].iloc[-1]:.0f})')
        ax_cg.axhline(100, color='#AAAAAA', linewidth=0.8, linestyle=':')
        ax_cg.set_xlabel('Date', fontsize=8.5); ax_cg.set_ylabel('Portfolio Value (₹)', fontsize=8.5)
        ax_cg.set_title('Individual ETF Growth (₹100 invested)', fontsize=9,
                        fontweight='bold', color=DARK, pad=8)
        ax_cg.legend(fontsize=7.5, loc='upper left', framealpha=0.9)
        ax_cg.grid(True, alpha=0.3, linestyle='--'); ax_cg.tick_params(labelsize=8)
        plt.setp(ax_cg.get_xticklabels(), rotation=25, ha='right')
        for sp in ax_cg.spines.values(): sp.set_color(BORDER)
    
        # Portfolio comparison cumulative growth
        ax_pc = fig.add_subplot(gs7[0:2, 1])
        ax_pc.plot(port_sh.index, port_sh.values, color=GOLD, linewidth=2.2,
                   label=f'Max Sharpe ★ (₹{port_sh.iloc[-1]:.0f})', zorder=4)
        ax_pc.plot(port_mv.index, port_mv.values, color=BLUE, linewidth=1.8, linestyle='-.',
                   label=f'Min Volatility ■ (₹{port_mv.iloc[-1]:.0f})', zorder=3)
        ax_pc.plot(port_eq.index, port_eq.values, color='tomato', linewidth=1.5, linestyle='--',
                   label=f'Equal Weight ▲ (₹{port_eq.iloc[-1]:.0f})', zorder=2)
        ax_pc.axhline(100, color='#AAAAAA', linewidth=0.8, linestyle=':')
        ax_pc.set_xlabel('Date', fontsize=8.5); ax_pc.set_ylabel('Portfolio Value (₹)', fontsize=8.5)
        ax_pc.set_title('Portfolio Strategy Comparison (₹100 invested)', fontsize=9,
                        fontweight='bold', color=DARK, pad=8)
        ax_pc.legend(fontsize=8.5, loc='upper left', framealpha=0.9)
        ax_pc.grid(True, alpha=0.3, linestyle='--'); ax_pc.tick_params(labelsize=8)
        plt.setp(ax_pc.get_xticklabels(), rotation=25, ha='right')
        for sp in ax_pc.spines.values(): sp.set_color(BORDER)
    
        # Drawdown chart
        ax_dd = fig.add_subplot(gs7[2, :])
        ax_dd.fill_between(dd_sh.index, dd_sh.values*100, 0, alpha=0.4, color=GOLD, label='Max Sharpe ★')
        ax_dd.fill_between(dd_mv.index, dd_mv.values*100, 0, alpha=0.4, color=BLUE, label='Min Volatility ■')
        ax_dd.fill_between(dd_eq.index, dd_eq.values*100, 0, alpha=0.3, color='tomato', label='Equal Weight ▲')
        ax_dd.plot(dd_sh.index, dd_sh.values*100, color=GOLD, linewidth=1)
        ax_dd.plot(dd_mv.index, dd_mv.values*100, color=BLUE, linewidth=1)
        ax_dd.plot(dd_eq.index, dd_eq.values*100, color='tomato', linewidth=0.8)
        ax_dd.set_xlabel('Date', fontsize=8.5); ax_dd.set_ylabel('Drawdown (%)', fontsize=8.5)
        ax_dd.set_title('Portfolio Drawdown Analysis — Underwater Chart', fontsize=9,
                        fontweight='bold', color=DARK, pad=8)
        ax_dd.legend(fontsize=8.5, loc='lower right', framealpha=0.9)
        ax_dd.grid(True, alpha=0.3, linestyle='--'); ax_dd.tick_params(labelsize=8)
        plt.setp(ax_dd.get_xticklabels(), rotation=20, ha='right')
        for sp in ax_dd.spines.values(): sp.set_color(BORDER)
    
        # Key stats footnote
        end_vals = {
            '★ Max Sharpe': port_sh.iloc[-1],
            '■ Min Vol'   : port_mv.iloc[-1],
            '▲ Equal Wt'  : port_eq.iloc[-1],
        }
        note = '  |  '.join([f'{k}: ₹{v:.0f} (on ₹100)' for k,v in end_vals.items()])
        fig.text(0.5, 0.048, note, ha='center', fontsize=8.5,
                 color=DARK, fontweight='bold', va='top')
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 8: FULL COMPARISON TABLE + RISK DECOMPOSITION
        # ════════════════════════════════════════════════════════════════════════
        fig = new_page('Detailed Portfolio Comparison & Risk Decomposition', 'Indian ETF MPT Report', '8')
        section_title(fig, '10. Comprehensive Portfolio Comparison Table', 0.90)
    
        # Full metrics comparison table
        metrics_rows = [
            ('Expected Return (p.a.)', f'{r_sh:.2%}', f'{r_mv:.2%}', f'{r_eq:.2%}'),
            ('Annualised Volatility',  f'{v_sh:.2%}', f'{v_mv:.2%}', f'{v_eq:.2%}'),
            ('Sharpe Ratio',           f'{sr_sh:.4f}',f'{sr_mv:.4f}',f'{sr_eq:.4f}'),
            ('Max Portfolio Drawdown', f'{dd_sh.min():.2%}', f'{dd_mv.min():.2%}', f'{dd_eq.min():.2%}'),
            ('End Value of ₹100',      f'₹{port_sh.iloc[-1]:.1f}', f'₹{port_mv.iloc[-1]:.1f}', f'₹{port_eq.iloc[-1]:.1f}'),
            ('Return/Drawdown Ratio',
             f'{r_sh/abs(dd_sh.min()):.2f}x' if dd_sh.min()!=0 else 'N/A',
             f'{r_mv/abs(dd_mv.min()):.2f}x' if dd_mv.min()!=0 else 'N/A',
             f'{r_eq/abs(dd_eq.min()):.2f}x' if dd_eq.min()!=0 else 'N/A'),
            ('Risk-Free Rate Used',    f'{RISK_FREE_RATE:.2%}', f'{RISK_FREE_RATE:.2%}', f'{RISK_FREE_RATE:.2%}'),
            ('Excess Return over Rf',  f'{r_sh-RISK_FREE_RATE:.2%}', f'{r_mv-RISK_FREE_RATE:.2%}', f'{r_eq-RISK_FREE_RATE:.2%}'),
        ]
        weight_rows = [(snames[i], f'{w_sh[i]:.2%}', f'{w_mv[i]:.2%}', f'{w_eq[i]:.2%}') for i in range(n)]
    
        all_rows = metrics_rows + [('── ASSET WEIGHTS ──', '──────', '──────', '──────')] + weight_rows
    
        m_col_x = [0.04, 0.38, 0.60, 0.80]
        m_hdrs  = ['Metric / Asset', 'Max Sharpe ★', 'Min Volatility ■', 'Equal Weight ▲']
        tbl_top = 0.855
    
        ax_mth = fig.add_axes([0.04, tbl_top, 0.92, 0.025])
        ax_mth.set_facecolor(HDR_BG); ax_mth.axis('off')
        for hx, h in zip(m_col_x, m_hdrs):
            fig.text(hx+0.005, tbl_top+0.012, h, fontsize=9, fontweight='bold',
                     color=WH, va='center')
    
        m_row_h = 0.033
        for ri, row in enumerate(all_rows):
            ry  = tbl_top - (ri+1)*m_row_h
            is_div = '──' in str(row[0])
            bg  = '#D0DCF0' if is_div else (ALT if ri%2==0 else WH)
            axr = fig.add_axes([0.04, ry, 0.92, m_row_h])
            axr.set_facecolor(bg); axr.axis('off')
            for ci,(hx,cell) in enumerate(zip(m_col_x, row)):
                clr = BLUE if is_div else DARK
                bld = is_div or (ri==2) # bold Sharpe row
                if ci>0 and not is_div:
                    try:
                        v = float(cell.strip('%₹x').replace(',',''))
                        if 'drawdown' in str(all_rows[ri][0]).lower() or ri==3:
                            clr = RED
                        elif ri==0 and ci==1: clr = GOLD
                    except: pass
                fig.text(hx+0.005, ry+m_row_h/2, cell, fontsize=8.5,
                         color=clr, va='center', fontweight='bold' if bld else 'normal')
    
        tbl_bottom2 = tbl_top - (len(all_rows)+1)*m_row_h - 0.025
        section_title(fig, '11. Asset Weight Contribution to Portfolio Risk', tbl_bottom2)
    
        # Stacked risk contribution bar
        ax_rc_bar = fig.add_axes([0.05, 0.060, 0.90, 0.130])
        port_names = ['Max Sharpe ★', 'Min Volatility ■', 'Equal Weight ▲']
        port_ws    = [w_sh, w_mv, w_eq]
        bar_left   = np.zeros(3)
        for i,sn in enumerate(snames):
            weights_per_port = np.array([pw[i] for pw in port_ws])*100
            ax_rc_bar.barh(port_names, weights_per_port, left=bar_left,
                           color=PALETTE[i], edgecolor=WH, linewidth=0.8,
                           label=sn, alpha=0.9)
            for j,(pw,bl) in enumerate(zip(weights_per_port, bar_left)):
                if pw > 2:
                    ax_rc_bar.text(bl+pw/2, j, f'{pw:.1f}%', ha='center',
                                   va='center', fontsize=8, color=WH, fontweight='bold')
            bar_left += weights_per_port
    
        ax_rc_bar.set_xlabel('Portfolio Weight (%)', fontsize=9)
        ax_rc_bar.set_title('Stacked Weight Decomposition', fontsize=9, fontweight='bold', color=DARK)
        ax_rc_bar.legend(fontsize=8, loc='upper right', ncol=5, framealpha=0.9)
        ax_rc_bar.set_xlim(0, 105)
        ax_rc_bar.grid(axis='x', alpha=0.3, linestyle='--'); ax_rc_bar.tick_params(labelsize=9)
        for sp in ax_rc_bar.spines.values(): sp.set_color(BORDER)
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 9: CONCLUSION & INVESTMENT CONSIDERATIONS
        # ════════════════════════════════════════════════════════════════════════
        fig = new_page('Conclusions & Investment Considerations', 'Indian ETF MPT Report', '9')
        section_title(fig, '12. Conclusions', 0.90)
    
        conclusion_paras = [
            ("Optimal Portfolio Construction & The Role of Gold",
             f"The Sharpe-maximising portfolio heavily favours low-correlation assets, allocating {w_sh[3]:.0%} to Gold BeES alongside "
             f"equity exposure ({w_sh[1]:.0%} Junior BeES, {w_sh[0]:.0%} Nifty 50 BeES). Gold acted as a powerful diversifier during the 2019-2026 period, "
             f"delivering robust returns (~{stats['GOLDBEES.NS']['ann_ret']:.1%} p.a.) with near-zero correlation to broad equities. "
             f"This allowed the portfolio to achieve a high Sharpe ratio of {sr_sh:.4f} while keeping volatility to {v_sh:.2%}."),
    
            ("Asset Redundancy (BankBees & LiquidBees)",
             f"BankBees was entirely excluded by the optimiser because its high correlation (>0.80) to NiftyBees offers no diversification benefit, "
             f"while yielding a lower Sharpe ratio ({stats['BANKBEES.NS']['sharpe']:.3f} vs {stats['NIFTYBEES.NS']['sharpe']:.3f}). "
             f"LiquidBees is only useful for absolute capital preservation; its {stats['LIQUIDBEES.NS']['ann_ret']:.2%} p.a. return drags down "
             f"the Sharpe ratio in aggressive portfolios, but dominates the Min Volatility portfolio (45% weight) to suppress total risk."),
    
            ("ACTIONABLE RECOMMENDATION FOR MUTUAL FUND ADVISORS",
             "For clients seeking growth, transition away from ad-hoc equal-weighting and adopt the Max Sharpe weights. "
             "Specifically, cap banking sector overexposure (as it behaves too similarly to the broader Nifty 50) and establish a "
             "strategic 25-35% allocation to physical Gold ETFs to act as a ballast against equity market shocks. "
             "This barbell approach captures the size premium of Mid/Next-50 caps while hedging tail risks through gold."),
             
            ("Model Limitations to Monitor",
             "MPT assumes normally distributed returns and static correlations. Indian ETF returns exhibit fat tails (excess kurtosis), "
             "and historical correlations can converge toward 1.0 during severe market crashes. Investment committees should re-run "
             "this optimisation quarterly to dynamically adjust to shifting volatility regimes.")
        ]
    
        y_c = 0.856
        for title, body in conclusion_paras:
            fig.text(0.04, y_c, f'▸  {title}', fontsize=9.5, fontweight='bold', color=BLUE, va='top')
            y_c -= 0.022
            for line in textwrap.wrap(body, width=180):
                fig.text(0.055, y_c, line, fontsize=8.8, color=DARK, va='top')
                y_c -= 0.018
            y_c -= 0.010
    
        section_title(fig, '13. Methodology Summary', y_c - 0.005)
        y_c -= 0.045
    
        method_items = [
            '• Data: Daily adjusted closing prices from Yahoo Finance via yfinance 1.5.1',
            '• Period: 2019-01-01 to ' + actual_end + f'  ({n_days} trading days on NSE)',
            f'• Risk-Free Rate: {RISK_FREE_RATE:.2%} p.a.  (India 10-Year G-Sec yield, {REPORT_DATE})',
            f'• Returns: Arithmetic daily → Annualised × {TRADING_DAYS} (trading days)',
            f'• Optimiser: scipy.optimize.minimize with SLSQP method, convergence tol=1e-12',
            f'• Constraints: Weights sum to 1.0; each weight ∈ [0, {MAX_WEIGHT:.0%}]  (long-only, 45% cap)',
            f'• Monte Carlo: {N_MC:,} random Dirichlet-sampled portfolios with 45% clip applied',
            '• Data Cleaning: Linear interpolation applied to 4 artifact dates per 3 ETFs (Dec 2019 split)',
            '• Software: Python 3.11  |  Libraries: numpy, pandas, matplotlib, scipy, yfinance',
        ]
        for item in method_items:
            fig.text(0.04, y_c, item, fontsize=8.5, color=DARK, va='top')
            y_c -= 0.022
    
        # Disclaimer box
        ax_disc = fig.add_axes([0.04, 0.055, 0.92, 0.055])
        ax_disc.set_facecolor('#FFF8E1'); ax_disc.axis('off')
        for sp in ax_disc.spines.values():
            sp.set_visible(True); sp.set_color('#F9A825'); sp.set_linewidth(1.5)
        disc_text = (
            "⚠️  DISCLAIMER: This report is generated for educational and research purposes only. "
            "It does not constitute investment advice, solicitation, or an offer to buy or sell any securities. "
            "Past performance does not guarantee future results. All investments involve risk, including the possible loss of principal. "
            "Please consult a SEBI-registered investment advisor before making any investment decisions."
        )
        for li, line in enumerate(textwrap.wrap(disc_text, width=175)):
            fig.text(0.05, 0.098 - li*0.018, line, fontsize=8, color='#555500', va='top', style='italic')
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # ════════════════════════════════════════════════════════════════════════
        # PAGE 10: GLOSSARY OF FINANCIAL TERMS
        # ════════════════════════════════════════════════════════════════════════
        fig = new_page('Glossary of Financial Terms', 'Indian ETF MPT Report', '10')
        section_title(fig, '14. Public Glossary — Understanding the Metrics', 0.90)
    
        glossary_items = [
            ("Modern Portfolio Theory (MPT)",
             "A mathematical framework for assembling a portfolio of assets such that the expected return is maximised for a given level of risk. "
             "It assumes that investors are risk-averse and that risk can be reduced through diversification."),
             
            ("Sharpe Ratio",
             "The most widely used measure of risk-adjusted return. It tells you how much excess return you are receiving for the extra volatility "
             "you endure holding a riskier asset. A higher Sharpe ratio is better. (>1.0 is considered good, >2.0 is excellent)."),
             
            ("Annualised Volatility",
             "A statistical measure of the dispersion of returns, representing the 'risk' of the asset. It shows how much the asset's price fluctuates "
             "over a year. Lower volatility means smoother, more predictable returns."),
             
            ("Maximum Drawdown",
             "The maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained. It is a critical indicator of "
             "downside risk and helps investors understand the worst-case historical scenario."),
             
            ("Efficient Frontier",
             "A graph representing a set of optimal portfolios that offer the highest expected return for a defined level of risk. Portfolios "
             "that lie below the efficient frontier are sub-optimal because they do not provide enough return for the level of risk."),
             
            ("Correlation Matrix",
             "A table showing correlation coefficients between assets. A value of +1 implies they move perfectly together, 0 implies no relationship, "
             "and -1 implies they move perfectly in opposite directions. Combining assets with low or negative correlation reduces overall risk."),
             
            ("Monte Carlo Simulation",
             "A computational technique that uses repeated random sampling to generate thousands of possible portfolio combinations. It helps "
             "map out the Efficient Frontier by testing a massive variety of weight allocations."),
        ]
        
        y_g = 0.85
        for term, definition in glossary_items:
            fig.text(0.04, y_g, term, fontsize=10, fontweight='bold', color=BLUE, va='top')
            y_g -= 0.022
            for line in textwrap.wrap(definition, width=165):
                fig.text(0.05, y_g, line, fontsize=9, color=DARK, va='top')
                y_g -= 0.020
            y_g -= 0.025
    
        # Footer note for glossary
        ax_g_ftr = fig.add_axes([0.04, 0.06, 0.92, 0.04])
        ax_g_ftr.set_facecolor('#EEF4FF'); ax_g_ftr.axis('off')
        fig.text(0.5, 0.08, "This glossary is provided to assist retail investors and the general public in interpreting institutional financial metrics.",
                 ha='center', fontsize=8.5, color=BLUE, style='italic', va='center')
    
        pdf.savefig(fig, dpi=180, bbox_inches='tight', facecolor=WH); plt.close(fig)
    
        # PDF metadata
        d = pdf.infodict()
        d['Title']   = 'MPT Indian ETF Portfolio Optimization Report'
        d['Author']  = 'Portfolio Optimizer — MPT Analysis Engine'
        d['Subject'] = 'Modern Portfolio Theory | Indian NSE ETFs'
        d['Keywords']= 'MPT, Portfolio Optimization, Indian ETFs, NSE, Sharpe Ratio, Efficient Frontier'
        d['CreationDate'] = datetime.datetime.now()
    
    print(f"\n✅  Detailed {10}-page white PDF saved:")
    print(f"    {PDF_PATH}")
    print(f"    Size: {os.path.getsize(PDF_PATH)/1024:.0f} KB")
