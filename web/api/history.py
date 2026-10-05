"""
/api/history — Returns 30-day historical price data + stats for live dashboard.
Endpoint: GET /api/history?period=1mo
Returns JSON with daily OHLCV + pct_change for Chart.js sparklines.
"""

from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np

            qs = parse_qs(urlparse(self.path).query)
            period = qs.get('period', ['1mo'])[0]
            # Validate period
            allowed = ['5d', '1mo', '3mo', '6mo', '1y', '2y', '5y']
            if period not in allowed:
                period = '1mo'

            tickers = [
                'NIFTYBEES.NS', 'JUNIORBEES.NS', 'BANKBEES.NS', 'MID150BEES.NS', 
                'MON100.NS', 'GOLDBEES.NS', 'SILVERBEES.NS', 'GSEC10IETF.NS', 'LIQUIDBEES.NS'
            ]
            names = {
                'NIFTYBEES.NS':  'Nifty 50 BeES',
                'JUNIORBEES.NS': 'Junior BeES',
                'BANKBEES.NS':   'Bank BeES',
                'MID150BEES.NS': 'Midcap 150 BeES',
                'MON100.NS':     'Motilal Nasdaq 100',
                'GOLDBEES.NS':   'Gold BeES',
                'SILVERBEES.NS': 'Silver BeES',
                'GSEC10IETF.NS': '10-Yr G-Sec ETF',
                'LIQUIDBEES.NS': 'Liquid BeES',
            }
            colors = {
                'NIFTYBEES.NS':  '#60a5fa',
                'JUNIORBEES.NS': '#ef4444',
                'BANKBEES.NS':   '#f59e0b',
                'MID150BEES.NS': '#14b8a6',
                'MON100.NS':     '#8b5cf6',
                'GOLDBEES.NS':   '#fbbf24',
                'SILVERBEES.NS': '#94a3b8',
                'GSEC10IETF.NS': '#ec4899',
                'LIQUIDBEES.NS': '#a78bfa',
            }

            raw = yf.download(
                tickers, period=period,
                auto_adjust=True, progress=False, group_by='column'
            )

            if isinstance(raw.columns, pd.MultiIndex):
                closes = raw['Close'].copy() if 'Close' in raw.columns.get_level_values(0) else raw.iloc[:, :5]
            else:
                closes = raw.copy()

            closes.dropna(how='all', inplace=True)
            closes.ffill(inplace=True)

            result = {}
            for t in tickers:
                col = t if t in closes.columns else t.split('.')[0]
                if col not in closes.columns:
                    match = [c for c in closes.columns if t.upper() in str(c).upper()]
                    col = match[0] if match else None

                if col is None:
                    result[t] = {'error': 'unavailable'}
                    continue

                series = closes[col].dropna()
                if len(series) < 2:
                    result[t] = {'error': 'insufficient data'}
                    continue

                # Normalise to 100 at start
                norm = (series / series.iloc[0]) * 100
                daily_ret = series.pct_change().dropna()

                # Dates as ISO strings
                dates = [d.strftime('%Y-%m-%d') for d in series.index]
                prices_list = [round(float(v), 2) for v in series.values]
                norm_list   = [round(float(v), 4) for v in norm.values]
                ret_list    = [round(float(v) * 100, 4) for v in daily_ret.values]

                current = float(series.iloc[-1])
                prev    = float(series.iloc[-2])
                chg     = current - prev
                pct_chg = (chg / prev) * 100

                # Period stats
                total_ret = float((series.iloc[-1] / series.iloc[0]) - 1) * 100
                ann_vol   = float(daily_ret.std() * np.sqrt(252)) * 100
                max_dd_val = float(
                    ((series / series.cummax()) - 1).min()
                ) * 100

                result[t] = {
                    'name':         names[t],
                    'color':        colors[t],
                    'ticker_short': t.replace('.NS', ''),
                    'dates':        dates,
                    'prices':       prices_list,
                    'normalised':   norm_list,
                    'daily_returns': ret_list,
                    'current':      round(current, 2),
                    'change':       round(chg, 2),
                    'pct_change':   round(pct_chg, 2),
                    'period_return':round(total_ret, 2),
                    'ann_vol':      round(ann_vol, 2),
                    'max_dd':       round(max_dd_val, 2),
                    'high_52w':     round(float(series.max()), 2),
                    'low_52w':      round(float(series.min()), 2),
                }

            payload = json.dumps(result)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, max-age=60')
            self.end_headers()
            self.wfile.write(payload.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
