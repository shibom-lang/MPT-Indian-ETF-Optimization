from http.server import BaseHTTPRequestHandler
import json
import yfinance as yf

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            tickers = ['NIFTYBEES.NS','JUNIORBEES.NS','BANKBEES.NS','GOLDBEES.NS','LIQUIDBEES.NS']
            names = {
                'NIFTYBEES.NS': 'Nifty 50 BeES',
                'JUNIORBEES.NS': 'Junior BeES',
                'BANKBEES.NS': 'Bank BeES',
                'GOLDBEES.NS': 'Gold BeES',
                'LIQUIDBEES.NS': 'Liquid BeES'
            }
            
            # Download recent data to ensure we have the last two valid trading days
            data = yf.download(tickers, period='5d', progress=False)
            
            # yfinance returns a MultiIndex column DataFrame if multiple tickers are passed
            # We want to extract just the 'Close' prices
            if 'Close' in data:
                closes = data['Close']
            else:
                closes = data
                
            results = []
            for t in tickers:
                series = closes[t].dropna()
                if len(series) >= 2:
                    current_price = series.iloc[-1]
                    prev_price = series.iloc[-2]
                    change = current_price - prev_price
                    pct_change = (change / prev_price) * 100
                elif len(series) == 1:
                    current_price = series.iloc[-1]
                    change = 0.0
                    pct_change = 0.0
                else:
                    current_price = 0.0
                    change = 0.0
                    pct_change = 0.0
                    
                results.append({
                    "ticker": t.replace('.NS', ''),
                    "name": names[t],
                    "price": float(round(current_price, 2)),
                    "change": float(round(change, 2)),
                    "pct_change": float(round(pct_change, 2))
                })
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        return
