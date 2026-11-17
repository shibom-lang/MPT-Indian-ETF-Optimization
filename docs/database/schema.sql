-- =============================================================================
-- ETF Optima: Production PostgreSQL Relational Schema (Neon Postgres & Supabase)
-- Supports Multi-User Accounts, Multi-Asset Portfolios & Backtest Analytics
-- =============================================================================

-- Enable UUID extension if not already present
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -----------------------------------------------------------------------------
-- Compatibility Layer: Supports Standalone Neon Postgres & Supabase Auth
-- -----------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS auth;
CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 1. Profiles Table (Extends auth.users for multi-tenant isolation)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 2. ETF Universe Catalog (Curated NSE Indian & Global ETFs)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.etf_universe (
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    asset_class TEXT NOT NULL, -- 'Large Cap Equity', 'Mid Cap', 'Next 50', 'US Equity', 'Debt', 'Commodity'
    exchange TEXT DEFAULT 'NSE',
    currency TEXT DEFAULT 'INR',
    expense_ratio NUMERIC(4, 2),
    benchmark TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 3. Portfolios Table (User-Saved Portfolio Models)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    strategy TEXT DEFAULT 'custom', -- 'custom', 'max_sharpe', 'min_vol', 'equal_weight'
    investment_amount NUMERIC(12, 2) DEFAULT 500000.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 4. Portfolio Holdings (Individual Allocations per Portfolio)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES public.portfolios(id) ON DELETE CASCADE,
    ticker TEXT NOT NULL REFERENCES public.etf_universe(ticker),
    weight NUMERIC(5, 4) NOT NULL, -- e.g. 0.2500 for 25%
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT check_weight_bounds CHECK (weight >= 0.0000 AND weight <= 1.0000),
    CONSTRAINT unique_portfolio_holding UNIQUE (portfolio_id, ticker)
);

-- -----------------------------------------------------------------------------
-- 5. Backtest Runs (Analytical & Monte Carlo Execution Snapshots)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.backtest_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES public.portfolios(id) ON DELETE CASCADE,
    expected_return NUMERIC(6, 4) NOT NULL,
    annual_volatility NUMERIC(6, 4) NOT NULL,
    sharpe_ratio NUMERIC(6, 4) NOT NULL,
    sortino_ratio NUMERIC(6, 4),
    max_drawdown NUMERIC(6, 4),
    cvar_95 NUMERIC(6, 4),
    metrics_meta JSONB, -- Simulation distributions, rolling alpha, and covariance matrix
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Row-Level Security (RLS) Multi-Tenant Policies
-- =============================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio_holdings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.backtest_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.etf_universe ENABLE ROW LEVEL SECURITY;

-- ETF Universe is publicly readable by everyone
CREATE POLICY "Public read etf_universe" ON public.etf_universe
    FOR SELECT USING (true);

-- Profiles: Users can view and update their own profile
CREATE POLICY "Users view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Portfolios: Full CRUD isolated to the owning user
CREATE POLICY "Users view own portfolios" ON public.portfolios
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users insert own portfolios" ON public.portfolios
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users update own portfolios" ON public.portfolios
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users delete own portfolios" ON public.portfolios
    FOR DELETE USING (auth.uid() = user_id);

-- Holdings: Inherit access via parent portfolio ownership
CREATE POLICY "Users view own holdings" ON public.portfolio_holdings
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.portfolios WHERE portfolios.id = portfolio_holdings.portfolio_id AND portfolios.user_id = auth.uid())
    );
CREATE POLICY "Users modify own holdings" ON public.portfolio_holdings
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.portfolios WHERE portfolios.id = portfolio_holdings.portfolio_id AND portfolios.user_id = auth.uid())
    );

-- Backtest Runs: Inherit access via parent portfolio ownership
CREATE POLICY "Users view own backtests" ON public.backtest_runs
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.portfolios WHERE portfolios.id = backtest_runs.portfolio_id AND portfolios.user_id = auth.uid())
    );
CREATE POLICY "Users insert own backtests" ON public.backtest_runs
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM public.portfolios WHERE portfolios.id = backtest_runs.portfolio_id AND portfolios.user_id = auth.uid())
    );

-- =============================================================================
-- Seed Catalog: 15+ Core Indian & Global ETFs (All Quoted in INR on NSE)
-- =============================================================================
INSERT INTO public.etf_universe (ticker, name, asset_class, expense_ratio, benchmark) VALUES
('NIFTYBEES.NS', 'Nippon India Nifty 50 BeES', 'Large Cap Equity', 0.04, 'Nifty 50 Index'),
('JUNIORBEES.NS', 'Nippon India Nifty Next 50 Junior BeES', 'Next 50 Equity', 0.12, 'Nifty Next 50 Index'),
('MID150BEES.NS', 'Nippon India Nifty Midcap 150 BeES', 'Mid Cap Equity', 0.20, 'Nifty Midcap 150 Index'),
('BANKBEES.NS', 'Nippon India Nifty Bank BeES', 'Sectoral Banking', 0.16, 'Nifty Bank Index'),
('ITBEES.NS', 'Nippon India Nifty IT BeES', 'Sectoral Technology', 0.22, 'Nifty IT Index'),
('MON100.NS', 'Motilal Oswal Nasdaq 100 ETF', 'US Equity (INR)', 0.58, 'Nasdaq 100 Index'),
('GOLDBEES.NS', 'Nippon India Gold BeES', 'Commodities (Gold)', 0.79, 'Domestic Gold Price'),
('SILVERBEES.NS', 'Nippon India Silver BeES', 'Commodities (Silver)', 0.52, 'Domestic Silver Price'),
('SETF10GILT.NS', 'SBI ETF 10 Year Gilt', 'Sovereign Debt (10Y G-Sec)', 0.05, 'Nifty 10 yr Benchmark G-Sec'),
('LIQUIDBEES.NS', 'Nippon India Liquid BeES', 'Cash Equivalent / Debt', 0.69, 'Nifty 1D Rate Index')
ON CONFLICT (ticker) DO NOTHING;
