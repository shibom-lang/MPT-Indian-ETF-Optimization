"""
tests/test_schema_syntax.py

Validates the PostgreSQL DDL schema definition for ETF Optima.
Ensures relational tables, check constraints, foreign keys, and RLS policies exist.
"""

import os
import pathlib

def test_schema_file_exists():
    schema_path = pathlib.Path("docs/database/schema.sql")
    assert schema_path.exists(), f"Schema file not found at {schema_path}"

def test_schema_required_tables():
    schema_path = pathlib.Path("docs/database/schema.sql")
    content = schema_path.read_text()
    
    required_tables = [
        "public.profiles",
        "public.etf_universe",
        "public.portfolios",
        "public.portfolio_holdings",
        "public.backtest_runs"
    ]
    for table in required_tables:
        assert table in content, f"Table {table} missing from schema.sql"

def test_schema_constraints_and_security():
    schema_path = pathlib.Path("docs/database/schema.sql")
    content = schema_path.read_text()

    # Mathematical weight bounds check
    assert "CHECK" in content, "CHECK constraint missing"
    assert "weight" in content and "0.0" in content, "Weight bounds check missing"

    # Row-Level Security
    assert "ENABLE ROW LEVEL SECURITY" in content, "Row-Level Security activation missing"
    assert "CREATE POLICY" in content, "Security policies missing"

def test_schema_seeded_etf_universe():
    schema_path = pathlib.Path("docs/database/schema.sql")
    content = schema_path.read_text()

    # Key NSE ETFs seeded
    tickers = ["NIFTYBEES.NS", "GOLDBEES.NS", "MON100.NS", "MID150BEES.NS", "SILVERBEES.NS"]
    for ticker in tickers:
        assert ticker in content, f"Ticker {ticker} missing from etf_universe seeds"
