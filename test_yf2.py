import requests
tickers = ['SETF10GILT.NS', 'LICNETFGSC.NS']
headers = {'User-Agent': 'Mozilla/5.0'}
for t in tickers:
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{t}?interval=1mo&range=10y"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        try:
            ts = data['chart']['result'][0]['timestamp'][0]
            print(f"{t}: start timestamp {ts}")
        except: pass
