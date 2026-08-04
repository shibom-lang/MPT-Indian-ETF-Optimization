# Indian ETF Portfolio Optimization (MPT)

 **Live Demo & Dashboard:** [https://web-six-zeta-72.vercel.app](https://web-six-zeta-72.vercel.app)  
*(Features live ETF prices and on-demand dynamic PDF report generation using a Vercel Serverless Python API)*

An automated portfolio optimization model in Python using live market data (2019–2026) for 5 major NSE-listed ETFs to construct institutional-grade asset allocation strategies. This project was built as part of preparation for the NISM Research Analyst (RA Series 15) exam.

## Key Technical Highlights

* **Modern Portfolio Theory (MPT):** Constructed Max Sharpe and Min Volatility portfolios.
* **Monte Carlo Simulations:** Mapped the Efficient Frontier using 10,000 simulated allocations.
* **Risk Analytics:** Generated Correlation Matrices, Asset Return Distributions, and Drawdown profiles.
* **Real-World Constraints:** Applied a 45% maximum weight cap per asset to ensure realistic diversification.
* **Data Cleansing:** Implemented automated detection and linear interpolation to fix historical stock split data anomalies (e.g., 1:10 split in Dec 2019).
* **Automated Reporting:** The script utilizes `matplotlib` and `matplotlib.backends.backend_pdf` to automatically generate a highly professional 10-page analytical report.

## Strategic Takeaway

The data clearly proves the flaw of naive equal-weighting. By utilizing the lack of correlation between broad equities (like Nifty 50 and Nifty Next 50) and physical Gold ETFs, the optimized model significantly improves risk-adjusted returns (alpha). 

## Output

Check out the generated report: [MPT_Indian_ETF_Detailed_Report.pdf](./MPT_Indian_ETF_Detailed_Report.pdf)

## Setup & Execution

```bash
# Install dependencies
pip install numpy pandas matplotlib scipy yfinance cffi

# Run the script to generate the PDF report
python mpt_detailed_report.py
```
