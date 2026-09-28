# 📊 Indian ETF Portfolio Optimization — MPT Analysis

🚀 **Live Dashboard:** [https://web-six-zeta-72.vercel.app](https://web-six-zeta-72.vercel.app)
*(Live NSE ETF prices · On-demand PDF generation via Vercel Serverless Python API)*

An end-to-end quantitative finance project in Python that applies **Modern Portfolio Theory (MPT)** to 5 major NSE-listed ETFs. Covers live data ingestion, automated data quality engineering, constrained portfolio optimization, Monte Carlo simulation, and institutional-grade PDF reporting — deployed as a full-stack web application.

> Built as part of preparation for the **NISM Research Analyst (RA Series 15)** examination.

---

## 🏆 Key Results

| Portfolio | Ann. Return | Volatility | Sharpe Ratio | End Value (₹100) |
|---|---|---|---|---|
| **Max Sharpe (Optimized)** | — | — | — | — |
| Min Volatility | — | — | — | — |
| Equal Weight (Benchmark) | — | — | — | — |
| Nifty 50 Index | — | — | — | — |

> *Run `python mpt_detailed_report.py` to generate a live report with current values.*

---

## ⚙️ Technical Highlights

| Area | Implementation |
|---|---|
| **Optimization** | Max Sharpe & Min Volatility via `scipy.optimize.minimize` (SLSQP), 45% weight cap |
| **Monte Carlo** | 10,000 Dirichlet-sampled portfolios to map the Efficient Frontier |
| **Risk Metrics** | Sharpe, **Sortino**, **Calmar**, **CVaR (95%)**, Max Drawdown, Skewness, Excess Kurtosis |
| **Data Quality** | Auto-detection and linear interpolation of Dec 2019 1:10 stock split artifacts |
| **Benchmark** | Nifty 50 Index comparison on all cumulative growth charts |
| **Reporting** | 10-page white-background institutional PDF via `matplotlib.backends.backend_pdf` |
| **Deployment** | Vercel serverless Python API + Vanilla JS frontend with live ETF prices |
| **Architecture** | Modular `mpt_core.py` shared engine — zero code duplication across scripts |

---

## 📁 Project Structure

```
.
├── mpt_core.py               # Shared engine: data, optimization, all metrics
├── mpt_detailed_report.py    # Generates 10-page institutional PDF report
├── mpt_indian_etf_analysis.py # Generates dark-mode dashboard charts
├── mpt_white_pdf.py          # Alternative white PDF layouts
├── requirements.txt          # Pinned Python dependencies
├── tests/
│   └── test_optimizer.py     # 21 unit tests (pytest-compatible)
├── notebooks/
│   └── 01_exploratory_analysis.ipynb  # Exploratory scratch analysis
├── web/                      # Vercel serverless full-stack app
│   ├── index.html / style.css / main.js
│   └── api/
│       ├── generate.py       # PDF generation endpoint
│       ├── mpt_generator.py  # Core computation for web API
│       └── prices.py         # Live price fetching
└── output/                   # Generated charts and PDFs (auto-created)
```

---

## 🔬 Strategic Insight

The analysis demonstrates that **naive equal-weighting is provably sub-optimal**. By exploiting the low correlation between broad equity ETFs (Nifty 50, Next 50) and physical Gold, the optimized portfolio achieves a significantly higher Sharpe ratio while keeping volatility in check. BankBees is excluded by the optimizer due to its high redundancy with NiftyBees (ρ > 0.80).

**Actionable recommendation**: Cap banking sector exposure and maintain a 25–35% strategic allocation to Gold ETFs as a portfolio ballast.

---

## ▶️ Setup & Execution

```bash
# 1. Install pinned dependencies
pip install -r requirements.txt

# 2. Generate the 10-page institutional PDF report
python mpt_detailed_report.py

# 3. Generate dark-mode dashboard charts + PDF
python mpt_indian_etf_analysis.py

# 4. Run unit tests
python tests/test_optimizer.py
# or: python -m pytest tests/ -v
```

Output files are written to `./output/` (created automatically — no hardcoded paths).

---

## 🧰 Skills Demonstrated

`Python` · `NumPy` · `Pandas` · `SciPy` · `Matplotlib` · `yfinance` · `Quantitative Finance` · `Modern Portfolio Theory` · `Monte Carlo Simulation` · `Portfolio Optimization` · `Risk Management` · `Data Quality Engineering` · `PDF Automation` · `REST API` · `Vercel Serverless` · `JavaScript` · `NISM RA Series 15`

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**. It does not constitute investment advice. Past performance is not indicative of future results. Please consult a SEBI-registered investment advisor before making investment decisions.
