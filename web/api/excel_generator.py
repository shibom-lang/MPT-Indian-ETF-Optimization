import yfinance as yf
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import os
import datetime

TICKERS = {
    'NIFTYBEES.NS': 'Nifty 50 BeES',
    'JUNIORBEES.NS': 'Junior BeES',
    'BANKBEES.NS': 'Bank BeES',
    'MID150BEES.NS': 'Midcap 150 BeES',
    'MON100.NS': 'Motilal Nasdaq 100',
    'GOLDBEES.NS': 'Gold BeES',
    'SILVERBEES.NS': 'Silver BeES',
    'SETF10GILT.NS': '10-Yr G-Sec ETF',
    'LIQUIDBEES.NS': 'Liquid BeES'
}

STRATEGY_STATS = {
    'maxsharpe': {'name': 'Max Sharpe Portfolio', 'return': 0.1944, 'volatility': 0.1302, 'weights': {
        'GOLDBEES.NS': 0.25, 'MID150BEES.NS': 0.25, 'MON100.NS': 0.25, 'JUNIORBEES.NS': 0.15, 'NIFTYBEES.NS': 0.10
    }},
    'minvol': {'name': 'Min Volatility Portfolio', 'return': 0.0821, 'volatility': 0.0520, 'weights': {
        'LIQUIDBEES.NS': 0.45, 'SETF10GILT.NS': 0.30, 'GOLDBEES.NS': 0.15, 'NIFTYBEES.NS': 0.10
    }},
    'equal': {'name': 'Equal Weight Portfolio', 'return': 0.1420, 'volatility': 0.1150, 'weights': {
        t: 1.0/9.0 for t in TICKERS.keys()
    }}
}

def fetch_data():
    raw = yf.download(list(TICKERS.keys()), period='5y', auto_adjust=True, progress=False, group_by='column')
    closes = raw['Close'].copy() if isinstance(raw.columns, pd.MultiIndex) else raw.copy()
    closes.dropna(how='all', inplace=True)
    closes.ffill(inplace=True)
    
    benchmark = closes['NIFTYBEES.NS']
    benchmark_ret = benchmark.pct_change().dropna()
    
    stats = {}
    for t in TICKERS.keys():
        prices = closes[t].dropna()
        if len(prices) == 0:
            prices = pd.Series([100]*len(benchmark), index=benchmark.index)
        
        current_price = float(prices.iloc[-1])
        ret = prices.pct_change().dropna()
        
        align_ret, align_bench = ret.align(benchmark_ret, join='inner')
        cov = align_ret.cov(align_bench)
        var = align_bench.var()
        beta = cov / var if var != 0 else 1.0
        
        div_yield = 0.015 if 'LIQUID' not in t and 'GSEC' not in t else 0.06
        if 'GOLD' in t or 'SILVER' in t:
            div_yield = 0.0
            
        stats[t] = {
            'price': current_price,
            'beta': beta,
            'div_yield': div_yield
        }
    return stats

def generate_excel(amount, strategy_id):
    stats = fetch_data()
    strategy = STRATEGY_STATS.get(strategy_id, STRATEGY_STATS['maxsharpe'])
    weights = strategy['weights']
    
    wb = openpyxl.Workbook()
    
    # ---------------------------------------------------------
    # SHEET 1: Portfolio Beta Calculator
    # ---------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Portfolio Beta Calculator"
    
    ws1.append(["Portfolio Beta Calculator - " + strategy['name']])
    ws1.cell(row=1, column=1).font = Font(size=14, bold=True)
    ws1.append([])
    
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    
    headers = ["Ticker Symbol", "Company Name", "Shares Held", "Share Price", "Portfolio Value", "Weight", "5Y Beta", "Weighted Beta"]
    ws1.append(headers)
    for col in range(1, len(headers)+1):
        cell = ws1.cell(row=3, column=col)
        cell.fill = header_fill
        cell.font = header_font
        ws1.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 18
        
    total_val = 0
    total_beta = 0
    row_idx = 4
    for t, w in weights.items():
        if w > 0:
            val = amount * w
            price = stats[t]['price']
            shares = int(val / price)
            actual_val = shares * price
            beta = stats[t]['beta']
            w_beta = beta * w
            
            ws1.append([t, TICKERS[t], shares, price, actual_val, w, beta, w_beta])
            
            ws1.cell(row=row_idx, column=3).number_format = '#,##0'
            ws1.cell(row=row_idx, column=4).number_format = '₹#,##0.00'
            ws1.cell(row=row_idx, column=5).number_format = '₹#,##0.00'
            ws1.cell(row=row_idx, column=6).number_format = '0.00%'
            ws1.cell(row=row_idx, column=7).number_format = '0.00'
            ws1.cell(row=row_idx, column=8).number_format = '0.000'
            
            total_val += actual_val
            total_beta += w_beta
            row_idx += 1
            
    ws1.append(["", "TOTAL", "", "", total_val, 1.0, "", total_beta])
    for col in range(1, len(headers)+1):
        ws1.cell(row=row_idx, column=col).font = Font(bold=True)
    ws1.cell(row=row_idx, column=5).number_format = '₹#,##0.00'
    ws1.cell(row=row_idx, column=6).number_format = '0.00%'
    ws1.cell(row=row_idx, column=8).number_format = '0.000'
    
    # ---------------------------------------------------------
    # SHEET 2: Portfolio Projection Schedule
    # ---------------------------------------------------------
    ws2 = wb.create_sheet(title="Portfolio Projection")
    
    ws2.append(["Portfolio Projection Schedule (10 Years) - " + strategy['name']])
    ws2.cell(row=1, column=1).font = Font(size=14, bold=True)
    ws2.append([])
    
    proj_headers = ["Year", "Beginning Value", "Expected Capital Return", "Expected Dividend", "Ending Value"]
    ws2.append(proj_headers)
    for col in range(1, len(proj_headers)+1):
        cell = ws2.cell(row=3, column=col)
        cell.fill = header_fill
        cell.font = header_font
        ws2.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 22
        
    exp_ret = strategy['return']
    avg_div = sum(stats[t]['div_yield'] * w for t, w in weights.items() if w > 0)
    cap_ret = exp_ret - avg_div
    
    current_val = total_val
    for year in range(1, 11):
        cap_gain = current_val * cap_ret
        div_inc = current_val * avg_div
        end_val = current_val + cap_gain + div_inc
        
        ws2.append([f"Year {year}", current_val, cap_gain, div_inc, end_val])
        row_idx = year + 3
        for col in range(2, 6):
            ws2.cell(row=row_idx, column=col).number_format = '₹#,##0.00'
            
        current_val = end_val
        
    # ---------------------------------------------------------
    # SHEET 3: Cash Flow & Dividend Schedule
    # ---------------------------------------------------------
    ws3 = wb.create_sheet(title="Cash Flow Schedule")
    ws3.append(["Cash Flow & Dividend Schedule - " + strategy['name']])
    ws3.cell(row=1, column=1).font = Font(size=14, bold=True)
    ws3.append([])
    
    cf_headers = ["ETF", "Shares", "Current Price", "Value", "Expected Div Yield", "Annual Dividend Income"]
    ws3.append(cf_headers)
    for col in range(1, len(cf_headers)+1):
        cell = ws3.cell(row=3, column=col)
        cell.fill = header_fill
        cell.font = header_font
        ws3.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20
        
    total_div = 0
    row_idx = 4
    for t, w in weights.items():
        if w > 0:
            val = amount * w
            price = stats[t]['price']
            shares = int(val / price)
            actual_val = shares * price
            div_y = stats[t]['div_yield']
            div_inc = actual_val * div_y
            
            ws3.append([TICKERS[t], shares, price, actual_val, div_y, div_inc])
            ws3.cell(row=row_idx, column=2).number_format = '#,##0'
            ws3.cell(row=row_idx, column=3).number_format = '₹#,##0.00'
            ws3.cell(row=row_idx, column=4).number_format = '₹#,##0.00'
            ws3.cell(row=row_idx, column=5).number_format = '0.00%'
            ws3.cell(row=row_idx, column=6).number_format = '₹#,##0.00'
            total_div += div_inc
            row_idx += 1
            
    ws3.append(["TOTAL", "", "", total_val, "", total_div])
    for col in range(1, len(cf_headers)+1):
        ws3.cell(row=row_idx, column=col).font = Font(bold=True)
    ws3.cell(row=row_idx, column=4).number_format = '₹#,##0.00'
    ws3.cell(row=row_idx, column=6).number_format = '₹#,##0.00'
    
    path = f"/tmp/Portfolio_Wealth_Model_{strategy_id}.xlsx"
    wb.save(path)
    return path
