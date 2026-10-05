import requests
import json
import time

tickers = ['NIFTYBEES.NS', 'JUNIORBEES.NS', 'BANKBEES.NS', 'MID150BEES.NS', 
           'MON100.NS', 'GOLDBEES.NS', 'SILVERBEES.NS', 'GSEC10IETF.NS', 'LIQUIDBEES.NS']
headers = {'User-Agent': 'Mozilla/5.0'}
for t in tickers:
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{t}?interval=1mo&range=5y"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        try:
            ts = data['chart']['result'][0]['timestamp'][0]
            print(f"{t}: start timestamp {ts}")
        except:
            print(f"{t}: error parsing")
    else:
        print(f"{t}: {resp.status_code}")
    time.sleep(1)
