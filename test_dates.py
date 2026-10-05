import yfinance as yf
tickers = ['BANKBEES.NS', 'GOLDBEES.NS', 'JUNIORBEES.NS', 'LIQUIDBEES.NS', 'NIFTYBEES.NS', 'MID150BEES.NS', 'MON100.NS', 'SILVERBEES.NS', 'GSEC10IETF.NS']
for t in tickers:
    data = yf.download(t, period='max')
    print(f"{t}: {data.index.min().date()} to {data.index.max().date()}")
