from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            import yfinance as yf
            import pandas as pd

            tickers = ['NIFTYBEES.NS', 'JUNIORBEES.NS', 'BANKBEES.NS', 'GOLDBEES.NS', 'LIQUIDBEES.NS']
            names = {
                'NIFTYBEES.NS':  'Nifty 50 BeES',
                'JUNIORBEES.NS': 'Junior BeES',
                'BANKBEES.NS':   'Bank BeES',
                'GOLDBEES.NS':   'Gold BeES',
                'LIQUIDBEES.NS': 'Liquid BeES',
            }

            # Download last 5 trading days to ensure we have at least 2 valid close prices
            raw = yf.download(tickers, period='5d', auto_adjust=True, progress=False, group_by='column')

            # Safely extract Close prices — handle both MultiIndex and flat column layouts
            if isinstance(raw.columns, pd.MultiIndex):
                if 'Close' in raw.columns.get_level_values(0):
                    closes = raw['Close'].copy()
                else:
                    # Try the other level
                    closes = raw.xs('Close', axis=1, level=1) if 'Close' in raw.columns.get_level_values(1) else raw
            else:
                closes = raw.copy()

            results = []
            for t in tickers:
                # Column name may or may not include exchange suffix depending on yfinance version
                col = t if t in closes.columns else t.split('.')[0]
                if col not in closes.columns:
                    # Try uppercase match
                    match = [c for c in closes.columns if t.upper() in str(c).upper()]
                    col = match[0] if match else None

                if col is None:
                    results.append({
                        "ticker": t.replace('.NS', ''),
                        "name":   names[t],
                        "price":  None,
                        "change": None,
                        "pct_change": None,
                        "error": "Data unavailable"
                    })
                    continue

                series = closes[col].dropna()

                if len(series) >= 2:
                    current_price = float(series.iloc[-1])
                    prev_price    = float(series.iloc[-2])
                    change        = current_price - prev_price
                    pct_change    = (change / prev_price) * 100
                elif len(series) == 1:
                    current_price = float(series.iloc[-1])
                    change        = 0.0
                    pct_change    = 0.0
                else:
                    results.append({
                        "ticker": t.replace('.NS', ''),
                        "name":   names[t],
                        "price":  None,
                        "change": None,
                        "pct_change": None,
                        "error": "No data returned"
                    })
                    continue

                results.append({
                    "ticker":     t.replace('.NS', ''),
                    "name":       names[t],
                    "price":      round(current_price, 2),
                    "change":     round(change, 2),
                    "pct_change": round(pct_change, 2),
                })

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
