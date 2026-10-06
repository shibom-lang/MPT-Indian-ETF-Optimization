import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TICKERS = ['NIFTYBEES.NS','JUNIORBEES.NS','BANKBEES.NS','MID150BEES.NS','MON100.NS','GOLDBEES.NS','SILVERBEES.NS','SETF10GILT.NS','LIQUIDBEES.NS']
raw = yf.download(TICKERS, start='2019-01-01', auto_adjust=True, progress=False, group_by='column')
prices = raw['Close']
prices.dropna(how='all', inplace=True)
prices.ffill(inplace=True); prices.dropna(inplace=True)
daily = prices.pct_change().dropna(how='all')

roll_ret = daily.rolling(252).mean() * 252
fig, ax = plt.subplots()
rr = roll_ret['NIFTYBEES.NS'].dropna() * 100
print(rr.index[0])
print(rr.index[-1])
print(type(rr.index))
ax.plot(rr.index, rr)
fig.savefig('test_plot.png')
