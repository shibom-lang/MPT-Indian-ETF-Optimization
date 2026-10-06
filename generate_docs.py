#!/usr/bin/env python3
"""
generate_docs.py — Consolidated Documentation Generator
Run `python generate_docs.py --help` for usage.
"""

import argparse
import os
import pathlib

OUTPUT_DIR = pathlib.Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

V1_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian ETF Quant Engine v1.0 - My Architecture Manual</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700andfamily=Fira+Code:wght@400;500anddisplay=swap" rel="stylesheet">
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
        body { font-family: 'Inter', sans-serif; line-height: 1.6; color: var(--text); background: var(--bg); padding: 40px 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .cover { text-align: center; padding: 100px 20px; border-bottom: 2px solid var(--border); margin-bottom: 40px; }
        .cover h1 { font-size: 42px; font-weight: 800; color: #111827; margin-bottom: 16px; letter-spacing: -0.5px; }
        .cover p { font-size: 18px; color: var(--muted); max-width: 600px; margin: 0 auto; }
        .cover .version { display: inline-block; background: var(--primary); color: white; padding: 4px 12px; border-radius: 99px; font-weight: 600; font-size: 14px; margin-bottom: 16px; }
        
        h2 { font-size: 28px; font-weight: 700; color: #111827; margin: 40px 0 20px 0; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
        h3 { font-size: 20px; font-weight: 600; color: #374151; margin: 24px 0 12px 0; }
        p { margin-bottom: 16px; }
        ul, ol { margin-bottom: 16px; padding-left: 24px; }
        li { margin-bottom: 8px; }
        
        .box { background: #f8fafc; border-left: 4px solid var(--primary); padding: 16px 20px; margin: 24px 0; border-radius: 0 8px 8px 0; }
        .box h4 { font-size: 16px; margin-bottom: 8px; color: #0f172a; }
        
        pre { background: var(--code-bg); color: var(--code-text); padding: 16px; border-radius: 8px; overflow-x: auto; font-family: 'Fira Code', monospace; font-size: 13px; margin-bottom: 20px; border: 1px solid var(--border); }
        code { font-family: 'Fira Code', monospace; background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; color: #b91c1c; }
        
        table { width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 14px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid var(--border); }
        th { background: #f9fafb; font-weight: 600; color: #374151; }
        
        .math { font-family: "Times New Roman", serif; font-size: 18px; font-style: italic; text-align: center; margin: 24px 0; padding: 16px; background: #f9fafb; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="no-print" style="text-align: right; margin-bottom: 20px;">
            <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; font-family: 'Inter', sans-serif;">🖨️ Print to PDF</button>
        </div>

        <div class="cover">
            <span class="version">VERSION 1.0 STABLE</span>
            <h1>My Indian ETF Portfolio Quant Engine</h1>
            <p>Comprehensive Architecture and Codebase Documentation</p>
            <p style="font-size: 14px; margin-top: 24px; color: #9ca3af;">Created as my backup reference before initiating v2.0 upgrades.</p>
        </div>

        <h2>1. Executive Summary</h2>
        <p>I built this document to serve as the permanent technical record of my <strong>v1.0 codebase</strong>. It details the mathematical foundations I implemented, my core Python architecture, the Vercel serverless deployment I configured, and the exact steps I took to calculate the Modern Portfolio Theory (MPT) metrics.</p>
        <p>If my v2.0 upgrade encounters issues, this document (along with the physical <code>v1_0_backup.zip</code> file I created) guarantees I have a 100% reliable rollback to my stable state.</p>

        <h2>2. System Architecture and Modules I Used</h2>
        <p>I built the project on a modular Python and JavaScript stack. I isolated the core logic in a shared engine to prevent code duplication across my scripts.</p>
        
        <table>
            <thead>
                <tr>
                    <th>Module / Library</th>
                    <th>Version</th>
                    <th>How I Used It in v1.0</th>
                </tr>
            </thead>
            <tbody>
                <tr><td><code>yfinance</code></td><td>1.5.1</td><td>To fetch live OHLCV price data directly from NSE/Yahoo Finance.</td></tr>
                <tr><td><code>pandas</code> / <code>numpy</code></td><td>2.2.3 / 2.2.6</td><td>For vectorized data manipulation, log returns calculation, and covariance matrix generation.</td></tr>
                <tr><td><code>scipy.optimize</code></td><td>1.14.1</td><td>To utilize the Sequential Least SQuares Programming (SLSQP) algorithm for constrained weight optimization.</td></tr>
                <tr><td><code>scipy.stats</code></td><td>1.14.1</td><td>To calculate Skewness and Excess Kurtosis for my tail-risk analysis.</td></tr>
                <tr><td><code>matplotlib</code></td><td>3.9.4</td><td>To generate my complex 10-page institutional PDF reports and dark-mode png charts.</td></tr>
                <tr><td><code>Vercel Serverless</code></td><td>-</td><td>To host my web UI and run my Python endpoints (<code>api/</code>) via the Vercel Python Runtime.</td></tr>
            </tbody>
        </table>

        <div class="page-break"></div>

        <h2>3. How My Mathematical Model Works</h2>
        <p>I built the core of v1.0 around Harry Markowitz's Modern Portfolio Theory (MPT). My goal was to find the exact percentage weighting of 5 ETFs that maximizes returns for a given level of risk.</p>

        <h3>Step 3.1: Log Returns and Covariance</h3>
        <p>Instead of simple percentage changes, I designed the model to calculate continuous <strong>logarithmic returns</strong> because they are time-additive:</p>
        <div class="math">R_t = ln(P_t / P_{t-1})</div>
        <p>I then compute the <strong>Covariance Matrix (Σ)</strong>, which measures how the 5 ETFs move relative to each other. When I find a negative covariance (like Gold vs Nifty), it means they move in opposite directions, providing my portfolio with a natural hedge.</p>

        <h3>Step 3.2: Portfolio Variance and Return</h3>
        <p>For any given set of weights (W), I calculate my portfolio's expected return and volatility (risk) using matrix algebra:</p>
        <div class="math">Return (μ) = W^T \cdot R_{annual}</div>
        <div class="math">Volatility (σ) = \sqrt{W^T \cdot Σ \cdot W}</div>

        <h3>Step 3.3: The SLSQP Optimizer</h3>
        <p>I use SciPy's <code>minimize</code> function to solve the mathematical optimization problem. Since I want to <em>maximize</em> the Sharpe Ratio, I instruct the optimizer to <em>minimize</em> the negative Sharpe Ratio.</p>
        
        <div class="box">
            <h4>My Optimization Constraints in v1.0:</h4>
            <ul>
                <li><strong>Bounds:</strong> I restricted the algorithm so no asset can hold less than 0% or more than 45% of the portfolio (<code>(0.0, 0.45)</code>).</li>
                <li><strong>Sum Constraint:</strong> I force all weights to sum exactly to 1.0 (100%).</li>
            </ul>
        </div>

        <div class="page-break"></div>

        <h2>4. Step-by-Step Codebase Breakdown</h2>
        
        <h3>4.1 <code>mpt_core.py</code> (My Core Engine)</h3>
        <p>This is the heart of my project. I structured it so every other file imports from this centralized module.</p>
        <ol>
            <li><strong><code>download_data()</code></strong>: Fetches closing prices for my 5 tickers.</li>
            <li><strong><code>detect_and_heal_splits()</code></strong>: I wrote this critical data-engineering function because in Dec 2019, JuniorBees had a 1:10 stock split that Yahoo Finance didn't adjust properly. My function detects the 90% artificial drop and interpolates it so my mathematical models don't break.</li>
            <li><strong><code>compute_portfolio_metrics()</code></strong>: Given an array of weights, I compute Return, Volatility, Sharpe, Sortino (downside deviation), Calmar, Max Drawdown, and CVaR (95% Confidence).</li>
            <li><strong><code>optimize_portfolio()</code></strong>: Sets up my objective function (e.g., negative Sharpe), applies my 45% bound constraint, and executes the SLSQP solver.</li>
            <li><strong><code>run_monte_carlo()</code></strong>: I use the Dirichlet distribution (<code>np.random.dirichlet</code>) to generate 10,000 random valid portfolios. This creates the "cloud" simulation I plot on the Efficient Frontier chart.</li>
        </ol>

        <pre><code># Inside mpt_core.py: My SLSQP Optimization Call
def optimize_portfolio(mean_returns, cov_matrix, risk_free_rate, objective='sharpe'):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    
    # I enforce weights must be between 0% and 45%
    bounds = tuple((0.0, 0.45) for _ in range(num_assets))
    
    # I enforce weights must sum exactly to 1.0
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
    
    # Initial guess: Equal weighting
    init_guess = num_assets * [1. / num_assets]
    
    result = minimize(
        negative_sharpe if objective == 'sharpe' else portfolio_volatility,
        init_guess,
        args=args,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    return result.x</code></pre>

        <h3>4.2 <code>mpt_detailed_report.py</code> (My PDF Generator)</h3>
        <p>I built this script to import the data from <code>mpt_core.py</code> and use <code>matplotlib.backends.backend_pdf.PdfPages</code> to iteratively draw charts onto my multi-page A4 canvas.</p>
        <p>I implemented grids (<code>gridspec</code>), drew tables using <code>plt.table</code>, and looped through my Monte Carlo results to plot the Efficient Frontier scatter plot.</p>

        <h3>4.3 <code>web/</code> (My Full-Stack App)</h3>
        <p>I deployed the web directory as a Vercel-ready serverless application:</p>
        <ul>
            <li><strong><code>index.html</code> and <code>dashboard.html</code>:</strong> The frontend UI I built with HTML/CSS and Chart.js.</li>
            <li><strong><code>api/mpt_generator.py</code>:</strong> A serverless function (extending <code>BaseHTTPRequestHandler</code>) where I run the MPT optimization on Vercel's servers and return the results as JSON.</li>
            <li><strong><code>api/prices.py</code> and <code>api/history.py</code>:</strong> The endpoints I created to fetch live and historical prices via yfinance, formatting them for my frontend sparkline charts.</li>
        </ul>

        <h2>5. My Rollback Protocol (How to reverse from v2.0)</h2>
        <p>If I need to discard v2.0 and return to this exact state, I have two options:</p>
        <ol>
            <li><strong>Using Git:</strong> I can run <code>git reset --hard v1.0-stable</code> in my terminal.</li>
            <li><strong>Using my Zip Backup:</strong> I can unzip the <code>v1_0_backup.zip</code> file which contains the exact pristine code files of my v1.0 implementation.</li>
        </ol>

        <p style="text-align: center; margin-top: 60px; color: #9ca3af; font-size: 14px;">End of My v1.0 Architecture Manual</p>
    </div>
</body>
</html>
"""

V2_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian ETF Quant Engine v2.0 - My Architecture Manual</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700andfamily=Fira+Code:wght@400;500anddisplay=swap" rel="stylesheet">
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
        body { font-family: 'Inter', sans-serif; line-height: 1.6; color: var(--text); background: var(--bg); padding: 40px 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .cover { text-align: center; padding: 100px 20px; border-bottom: 2px solid var(--border); margin-bottom: 40px; }
        .cover h1 { font-size: 42px; font-weight: 800; color: #111827; margin-bottom: 16px; letter-spacing: -0.5px; }
        .cover p { font-size: 18px; color: var(--muted); max-width: 600px; margin: 0 auto; }
        .cover .version { display: inline-block; background: #f59e0b; color: white; padding: 4px 12px; border-radius: 99px; font-weight: 600; font-size: 14px; margin-bottom: 16px; }
        
        h2 { font-size: 28px; font-weight: 700; color: #111827; margin: 40px 0 20px 0; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
        h3 { font-size: 20px; font-weight: 600; color: #374151; margin: 24px 0 12px 0; }
        p { margin-bottom: 16px; }
        ul, ol { margin-bottom: 16px; padding-left: 24px; }
        li { margin-bottom: 8px; }
        
        .box { background: #f8fafc; border-left: 4px solid var(--primary); padding: 16px 20px; margin: 24px 0; border-radius: 0 8px 8px 0; }
        .box h4 { font-size: 16px; margin-bottom: 8px; color: #0f172a; }
        
        pre { background: var(--code-bg); color: var(--code-text); padding: 16px; border-radius: 8px; overflow-x: auto; font-family: 'Fira Code', monospace; font-size: 13px; margin-bottom: 20px; border: 1px solid var(--border); }
        code { font-family: 'Fira Code', monospace; background: var(--code-bg); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; color: #b91c1c; }
        
        .mermaid { background: #f8fafc; padding: 20px; border: 1px solid var(--border); border-radius: 8px; margin: 24px 0; text-align: center; }
        .math { font-family: "Times New Roman", serif; font-size: 18px; font-style: italic; text-align: center; margin: 24px 0; padding: 16px; background: #f9fafb; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="no-print" style="text-align: right; margin-bottom: 20px;">
            <button onclick="window.print()" style="background: #f59e0b; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; font-family: 'Inter', sans-serif;">🖨️ Print to PDF</button>
        </div>

        <div class="cover">
            <span class="version">VERSION 2.0 ADVANCED</span>
            <h1>My Indian ETF Portfolio Quant Engine</h1>
            <p>v2.0 Structural Code Explanation and Time Series Architecture</p>
            <p style="font-size: 14px; margin-top: 24px; color: #9ca3af;">Documenting my Phase 2 and Phase 3 Time-Series Econometrics additions.</p>
        </div>

        <h2>1. Executive Summary</h2>
        <p>I built this v2.0 architecture manual to document the advanced quantitative additions I made to my engine. After completing the static Markowitz MPT model in v1.0, I successfully expanded the universe to 8+ ETFs (including Midcaps, Nasdaq 100, Silver, and G-Secs) and integrated dynamic time-series analysis.</p>

        <h2>2. My New v2.0 Structural Diagram</h2>
        <p>This flowchart illustrates how I structured the data flow in my updated <code>mpt_core.py</code> engine:</p>
        
        <div class="mermaid">
        flowchart TD
            A[Yahoo Finance Data Ingestion] --> B[Data Cleaning and Split Healing]
            B --> C{Select Basket}
            C -->|CLASSIC_5| D[5-ETF DataFrame]
            C -->|ALL_WEATHER_8| D2[8-ETF DataFrame]
            
            D2 --> E(Static MPT Optimisation)
            D2 --> F(Time Series and Econometrics)
            
            E --> E1[Covariance Matrix]
            E --> E2[SLSQP Max Sharpe Solver]
            E --> E3[Dirichlet Monte Carlo]
            
            F --> F1[Rolling Metrics window=252]
            F --> F2[RiskMetrics EWMA Volatility λ=0.94]
            F --> F3[Walk-Forward Backtesting]
            F --> F4[Historical Stress Tester]
            
            E2 --> G[Final Portfolio Weights]
            F3 --> G
            G --> H[Web UI / Vercel Serverless]
        </div>

        <div class="page-break"></div>

        <h2>3. Phase 2: Time Series and Econometrics</h2>
        
        <h3>3.1 EWMA Volatility (RiskMetrics)</h3>
        <p>Static standard deviation assumes volatility is constant over time. In reality, financial markets exhibit <strong>Volatility Clustering</strong> (ARCH effects). To capture this, I implemented the J.P. Morgan RiskMetrics™ Exponentially Weighted Moving Average (EWMA) model.</p>
        <p>I used the standard institutional decay factor of <code>lambda = 0.94</code> for daily returns, assigning higher weight to recent shocks.</p>
        
        <pre><code># My EWMA Volatility Implementation
def compute_ewma_volatility(daily_returns, lambda_decay=0.94):
    ewma_var = daily_returns.ewm(alpha=(1 - lambda_decay)).var()
    ewma_vol = np.sqrt(ewma_var) * np.sqrt(TRADING_DAYS)
    return ewma_vol</code></pre>

        <h3>3.2 Walk-Forward Backtesting (Systematic Rebalancing)</h3>
        <p>In v1.0, the portfolio growth assumed static weights drifting over time. I built a dynamic walk-forward backtester that simulates exactly what an asset manager does: Quarterly Rebalancing.</p>
        <p>My algorithm loops through the daily returns, updating the portfolio EOD value, and on the last trading day of the quarter (<code>frequency='QE'</code>), it systematically resets the asset buckets back to the target optimal weights.</p>
        
        <h2>4. Phase 3: Stress Testing</h2>
        <p>I added a dedicated <code>stress_test_drawdowns()</code> function to evaluate how my optimal portfolios perform during known structural breaks and historical crises. I hardcoded three major events:</p>
        <ul>
            <li><strong>COVID-19 Crash</strong> (Feb-Apr 2020)</li>
            <li><strong>Rate Hike Tech Shock</strong> (Jan-Oct 2022)</li>
            <li><strong>Election Volatility</strong> (Jun 2024)</li>
        </ul>
        <p>My code slices the timezone-naive cumulative growth series across these dates and dynamically calculates the maximum drawdown peak-to-trough (<code>drawdown.min()</code>).</p>

        <p style="text-align: center; margin-top: 60px; color: #9ca3af; font-size: 14px;">End of My v2.0 Architecture Manual</p>
    </div>
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'default' });
    </script>
</body>
</html>
"""

FINAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian ETF Quant Engine v3.0 - Final Architecture Manual</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700andfamily=Fira+Code:wght@400;500anddisplay=swap" rel="stylesheet">
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
            <p>End-to-End System Architecture and Workflow Manual</p>
            <p style="font-size: 14px; margin-top: 24px; color: #9ca3af;">Documenting the full-stack integration: Vercel, SciPy, Matplotlib, and OpenPyxl.</p>
        </div>

        <h2>1. Executive Summary</h2>
        <p>This document outlines the final production architecture of my ETF Portfolio Optimization engine. After building the core Modern Portfolio Theory (MPT) engine in Python, I successfully scaled it into a full-stack, automated <strong>Robo-Advisor</strong>. The platform now features a glassmorphism web interface that connects to a Vercel serverless backend, dynamically generating institutional-grade PDF and Excel reports on the fly.</p>

        <h2>2. Complete System Workflow Diagram</h2>
        <p>This flowchart illustrates the end-to-end data pipeline from user input to final report delivery:</p>
        
        <div class="mermaid">
        flowchart TD
            A[User Browser UI] -->|Selects Strategy and Amount| B[Vercel Serverless Backend]
            
            B -->|GET /api/generate| C1[Matplotlib PDF Engine]
            B -->|GET /api/excel| C2[OpenPyxl Excel Engine]
            
            C1 --> D{yfinance API}
            C2 --> D
            
            D -->|Live Market Data Since 2019| E[Data Cleaning and Alignment]
            
            E --> F[SciPy MPT Optimizer]
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

        <h2>3. Serverless Backend and Dynamic Reporting</h2>
        
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

def generate_v1():
    print("Generating v1.0 Architecture Manual...")
    with open(OUTPUT_DIR / "ETF_Quant_v1_Architecture_Manual.html", "w", encoding="utf-8") as f:
        f.write(V1_HTML)
    print("Done.")

def generate_v2():
    print("Generating v2.0 Architecture Manual...")
    with open(OUTPUT_DIR / "ETF_Quant_v2_Architecture_Manual.html", "w", encoding="utf-8") as f:
        f.write(V2_HTML)
    print("Done.")

def generate_final():
    print("Generating Final (v3.0) Architecture Manual...")
    with open(OUTPUT_DIR / "ETF_Quant_Final_Architecture_Manual.html", "w", encoding="utf-8") as f:
        f.write(FINAL_HTML)
    print("Done.")

def generate_all():
    generate_v1()
    generate_v2()
    generate_final()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Project Documentation")
    parser.add_argument('--version', type=str, choices=['v1', 'v2', 'final', 'all'], default='all',
                        help="Which version of the documentation to generate.")
    
    args = parser.parse_args()
    
    if args.version == 'v1':
        generate_v1()
    elif args.version == 'v2':
        generate_v2()
    elif args.version == 'final':
        generate_final()
    elif args.version == 'all':
        generate_all()
