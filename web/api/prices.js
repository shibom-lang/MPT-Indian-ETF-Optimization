export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=300');

  const tickers = [
    { id: 'NIFTYBEES.NS', name: 'Nifty 50 BeES', short: 'NIFTYBEES' },
    { id: 'JUNIORBEES.NS', name: 'Junior BeES', short: 'JUNIORBEES' },
    { id: 'BANKBEES.NS', name: 'Bank BeES', short: 'BANKBEES' },
    { id: 'MID150BEES.NS', name: 'Midcap 150 BeES', short: 'MID150BEES' },
    { id: 'MON100.NS', name: 'Motilal Nasdaq 100', short: 'MON100' },
    { id: 'GOLDBEES.NS', name: 'Gold BeES', short: 'GOLDBEES' },
    { id: 'SILVERBEES.NS', name: 'Silver BeES', short: 'SILVERBEES' },
    { id: 'SETF10GILT.NS', name: '10-Yr G-Sec ETF', short: 'SETF10GILT' },
    { id: 'LIQUIDBEES.NS', name: 'Liquid BeES', short: 'LIQUIDBEES' },
  ];

  const fallbackPrices = {
    'NIFTYBEES.NS': { price: 289.60, prev: 286.54 },
    'JUNIORBEES.NS': { price: 742.10, prev: 745.60 },
    'BANKBEES.NS': { price: 54.10, prev: 53.80 },
    'MID150BEES.NS': { price: 22.30, prev: 22.10 },
    'MON100.NS': { price: 172.50, prev: 171.20 },
    'GOLDBEES.NS': { price: 68.45, prev: 68.10 },
    'SILVERBEES.NS': { price: 96.20, prev: 95.80 },
    'SETF10GILT.NS': { price: 104.80, prev: 104.75 },
    'LIQUIDBEES.NS': { price: 1000.00, prev: 1000.00 },
  };

  const results = await Promise.all(
    tickers.map(async (t) => {
      try {
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${t.id}?interval=1d&range=5d`;
        const resp = await fetch(url, {
          headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        const meta = data.chart?.result?.[0]?.meta;
        const price = meta?.regularMarketPrice || fallbackPrices[t.id].price;
        const prev = meta?.chartPreviousClose || fallbackPrices[t.id].prev;
        const change = price - prev;
        const pct_change = (change / prev) * 100;
        return {
          ticker: t.short,
          name: t.name,
          price: Number(price.toFixed(2)),
          change: Number(change.toFixed(2)),
          pct_change: Number(pct_change.toFixed(2)),
        };
      } catch (err) {
        const fb = fallbackPrices[t.id];
        const change = fb.price - fb.prev;
        const pct_change = (change / fb.prev) * 100;
        return {
          ticker: t.short,
          name: t.name,
          price: Number(fb.price.toFixed(2)),
          change: Number(change.toFixed(2)),
          pct_change: Number(pct_change.toFixed(2)),
        };
      }
    })
  );

  return res.status(200).json(results);
}
