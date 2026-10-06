import os
import pathlib

OUTPUT_DIR = pathlib.Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
DOC_PATH = OUTPUT_DIR / "ETF_Quant_Final_Architecture_Manual.html"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian ETF Quant Engine v3.0 - Final Architecture Manual</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        :root {
            --bg: #ffffff;
            --text: #1f2937;
            --muted: #6b7280;
            --primary: #2563eb;
            --border: #e5e7eb;
            --code-bg: #f3f4f6;
            --code-text: #111827;
            --accent: #f59e0b;
        }
        @media print {
            body { background: white; color: black; font-size: 11pt; }
            .no-print { display: none; }
            .page-break { page-break-before: always; }
            pre { border: 1px solid #ccc; page-break-inside: avoid; }
            h2, h3 { page-break-after: avoid; }
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', sans-serif; background: #f9fafb; color: var(--text); line-height: 1.6; }
        .container { max-width: 900px; margin: 40px auto; padding: 60px; background: var(--bg); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-radius: 8px; border-top: 8px solid var(--primary); }
        .cover { text-align: center; margin-bottom: 60px; padding-bottom: 40px; border-bottom: 1px solid var(--border); }
        .version { display: inline-block; padding: 4px 12px; background: #dbeafe; color: var(--primary); font-size: 12px; font-weight: 700; border-radius: 99px; letter-spacing: 1px; margin-bottom: 20px; }
        h1 { font-size: 36px; font-weight: 800; letter-spacing: -1px; margin-bottom: 12px; }
        h2 { font-size: 24px; font-weight: 700; margin: 40px 0 20px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
        h3 { font-size: 18px; font-weight: 600; margin: 24px 0 12px; color: var(--primary); }
        p { margin-bottom: 16px; font-size: 15px; }
        ul { margin-bottom: 16px; padding-left: 24px; }
        li { margin-bottom: 8px; font-size: 15px; }
        pre { background: var(--code-bg); padding: 16px; border-radius: 6px; overflow-x: auto; margin: 20px 0; }
        code { font-family: 'Fira Code', monospace; font-size: 13px; color: var(--code-text); }
        p code, li code { background: var(--code-bg); padding: 2px 6px; border-radius: 4px; color: #dc2626; }
        .mermaid { margin: 40px 0; display: flex; justify-content: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="cover">
            <span class="version">FINAL VERSION 3.0</span>
            <h1>My Indian ETF Robo-Advisor</h1>
            <p>End-to-End System Architecture & Workflow Manual</p>
            <p style="font-size: 14px; margin-top: 24px; color: #9ca3af;">Documenting the full-stack integration: Vercel, SciPy, Matplotlib, and OpenPyxl.</p>
        </div>

        <h2>1. Executive Summary</h2>
        <p>This document outlines the final production architecture of my ETF Portfolio Optimization engine. After building the core Modern Portfolio Theory (MPT) engine in Python, I successfully scaled it into a full-stack, automated <strong>Robo-Advisor</strong>. The platform now features a glassmorphism web interface that connects to a Vercel serverless backend, dynamically generating institutional-grade PDF and Excel reports on the fly.</p>

        <h2>2. Complete System Workflow Diagram</h2>
        <p>This flowchart illustrates the end-to-end data pipeline from user input to final report delivery:</p>
        
        <div class="mermaid">
        flowchart TD
            A[User Browser UI] -->|Selects Strategy & Amount| B(Vercel Serverless Backend)
            
            B -->|GET /api/generate| C1[Matplotlib PDF Engine]
            B -->|GET /api/excel| C2[OpenPyxl Excel Engine]
            
            C1 --> D{yfinance API}
            C2 --> D
            
            D -->|5Y Live Market Data| E[Data Cleaning & Alignment]
            
            E --> F(SciPy MPT Optimizer)
            F -->|Covariance Matrix| G1[SLSQP Max Sharpe Solver]
            F -->|Volatility Penalty| G2[Min Volatility Solver]
            
            G1 --> H[Optimal 9-ETF Weights]
            G2 --> H
            
            H --> C1
            H --> C2
            
            C1 -->|Yields PDF Stream| A
            C2 -->|Yields XLSX Stream| A
        </div>

        <div class="page-break"></div>

        <h2>3. Serverless Backend & Dynamic Reporting</h2>
        
        <h3>3.1 Matplotlib PDF Generation</h3>
        <p>Instead of relying on third-party SaaS services for reporting, I built a bespoke PDF generator using <code>matplotlib.backends.backend_pdf</code>. The backend plots the Efficient Frontier, Correlation Heatmaps, and 12-Month Rolling Return charts completely in memory (headless), streams them directly to a PDF buffer, and serves it back to the client.</p>

        <h3>3.2 Excel Portfolio Wealth Model</h3>
        <p>For investors wanting to perform their own financial modeling, I integrated <code>openpyxl</code> to dynamically construct an Excel workbook. It takes the user's exact investment amount and chosen MPT strategy and builds a three-statement <strong>Portfolio Wealth Model</strong>:</p>
        <ul>
            <li><strong>Portfolio Beta Calculator:</strong> Calculates live Weighted Beta against the Nifty 50.</li>
            <li><strong>10-Year Projection Schedule:</strong> Forecasts compounding wealth based on MPT expected returns.</li>
            <li><strong>Cash Flow Schedule:</strong> Models expected annual dividend yields for the basket.</li>
        </ul>

        <h2>4. The 9-ETF MPT Optimizer</h2>
        <p>At the core of the backend is the <code>scipy.optimize.minimize</code> algorithm. It ingests 5 years of daily returns across a highly diversified 9-ETF universe (encompassing Indian Equities, US Equities, Gold, Silver, and Government Securities).</p>
        <p>The optimizer uses the <strong>SLSQP (Sequential Least SQuares Programming)</strong> method to maximize the Sharpe ratio, strictly enforcing boundaries so no single asset exceeds a 45% weight (preventing over-concentration) and the weights sum perfectly to 1.</p>
        
        <pre><code># Core Optimization Logic (SciPy SLSQP)
def maximize_sharpe(mean_returns, cov_matrix, risk_free_rate):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    
    # Target function to minimize (Negative Sharpe)
    def neg_sharpe(weights, mean_returns, cov_matrix, risk_free_rate):
        p_ret = np.sum(mean_returns * weights) * 252
        p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        return -(p_ret - risk_free_rate) / p_vol

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.0, 0.45) for asset in range(num_assets))
    
    result = minimize(neg_sharpe, num_assets*[1./num_assets,], args=args,
                      method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x</code></pre>

        <p style="text-align: center; margin-top: 60px; color: #9ca3af; font-size: 14px;">End of Final Architecture Manual</p>
    </div>
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'default' });
    </script>
</body>
</html>
"""

with open(DOC_PATH, "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)
print(f"Generated Final Manual: {DOC_PATH}")

if __name__ == "__main__":
    pass
