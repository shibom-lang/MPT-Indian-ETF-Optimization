import yfinance as yf
import pandas as pd

TICKERS = ['NIFTYBEES.NS','JUNIORBEES.NS','BANKBEES.NS','MID150BEES.NS','MON100.NS','GOLDBEES.NS','SILVERBEES.NS','SETF10GILT.NS','LIQUIDBEES.NS']
raw = yf.download(TICKERS, start='2019-01-01', auto_adjust=True, progress=False, group_by='column')
prices = raw['Close']
prices.dropna(how='all', inplace=True)
prices.ffill(inplace=True)
daily = prices.pct_change().dropna(how='all')

roll_ret = daily.rolling(252).mean() * 252
print("Roll ret shapes:")
for t in TICKERS:
    rr = roll_ret[t].dropna()
    print(t, rr.shape)
