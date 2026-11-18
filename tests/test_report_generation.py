import os
import pathlib
import pytest

def test_detailed_report_pdf_exists():
    paths = [
        pathlib.Path("src/output/MPT_Indian_ETF_Detailed_Report.pdf"),
        pathlib.Path("web/public/MPT_Indian_ETF_Detailed_Report.pdf"),
        pathlib.Path("dist/MPT_Indian_ETF_Detailed_Report.pdf"),
    ]
    for p in paths:
        assert p.exists(), f"Expected {p} to exist"
        assert p.stat().st_size > 100_000, f"Expected {p} to be > 100KB, got {p.stat().st_size}"

def test_dashboard_white_pdf_exists():
    p = pathlib.Path("src/output/MPT_Indian_ETF_Dashboard_WHITE.pdf")
    assert p.exists(), f"Expected {p} to exist"
    assert p.stat().st_size > 50_000, f"Expected {p} to be > 50KB"

def test_dashboard_a4_pdf_exists():
    p = pathlib.Path("src/output/MPT_Indian_ETF_Dashboard_A4.pdf")
    assert p.exists(), f"Expected {p} to exist"
    assert p.stat().st_size > 50_000, f"Expected {p} to be > 50KB"

def test_core_parameters():
    from src.mpt_core import RISK_FREE_RATE, MAX_WEIGHT, N_MC, TRADING_DAYS, TICKERS
    assert RISK_FREE_RATE == 0.068, "Risk-free rate must be 6.80% (10-Yr G-Sec)"
    assert MAX_WEIGHT == 0.45, "Max single asset weight cap must be 45%"
    assert N_MC >= 10_000, "Monte Carlo simulations must be at least 10,000"
    assert TRADING_DAYS == 252, "Annual trading days must be 252"
    assert len(TICKERS) in (9, 11), "Universe must cover 9 or 11 Indian ETFs"
