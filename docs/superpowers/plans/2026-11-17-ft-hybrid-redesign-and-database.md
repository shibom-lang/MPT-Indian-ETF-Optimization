# ETF Optima: FT Editorial Redesign & PostgreSQL Scaling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild ETF Optima's UI/UX using the Financial Times editorial design system merged with Option D's quantitative data depth (actionable share execution schedule + collapsible SLSQP telemetry drawer), preserve all existing live market charts and period filters (1D, 1M, 5Y), and provision the PostgreSQL database schema for multi-user portfolio scaling on Vercel.

**Architecture:** 
- **Frontend Presentation Layer:** Replaces generic "AI glassmorphism" with the Financial Times newsprint palette (`#FFF1E5`, `#FAF0E6`), Oxford Navy (`#0C2340`), serif typography (`Newsreader`), and tabular numbers (`JetBrains Mono`, `tnum`).
- **Data & Charting Layer:** Preserves 100% of the live charts (Cumulative Growth, Drawdown Underwater plot, Efficient Frontier Monte Carlo, 9x9 Correlation Heatmap) while adding Option D's exact share quantity calculations.
- **Persistence & Cloud Layer:** Provisions PostgreSQL relational tables with Row-Level Security (RLS) and mathematical `CHECK` constraints on Supabase, connected to Vercel via environment variables.

**Tech Stack:** HTML5, CSS3, JavaScript (ES6+), Chart.js, PostgreSQL (Supabase), Python 3.11 Serverless (SciPy, Matplotlib, OpenPyxl), Vercel.

**Spec:** `docs/superpowers/specs/2026-11-17-etf-optima-scaling-design.md`

---

## Global Constraints

- **Zero AI-Slop:** No glowing neon gradients, no blurry background orbs, no cartoon emojis; use clean vector SVGs, warm newsprint surfaces, and Oxford Navy borders.
- **Preserve All Live Charts:** Do not remove or break Cumulative Growth (Portfolios / Individual / All Together), Drawdown Analysis, Efficient Frontier, or Correlation Heatmap.
- **Preserve Time Horizon Controls:** Retain all period buttons (`1D`, `5D`, `1M`, `3M`, `6M`, `1Y`, `5Y`) for both short-term market tracking and long-term MPT optimization.
- **Zero Price Jitter:** Enforce `font-variant-numeric: tabular-nums` on all tickers, LTPs, and metric values.
- **Serverless Resilience:** Keep Python serverless endpoints stateless; pass portfolio payloads directly from the frontend to avoid Vercel 10s execution timeouts.

---

## Review Focus

1. **Live Chart Rendering in FT Theme:** Chart.js canvas elements must use matching newsprint backgrounds (`#FAF0E6`) and high-contrast lines (Oxford Navy, Forest Green, Gold, Claret) so charts remain crystal clear.
2. **Mobile Viewport Responsiveness:** Tables and metric grids must collapse gracefully on mobile screens without horizontal overflowing.
3. **Execution Table Math Accuracy:** Share quantities must be floored integers (`Math.floor(allocated_amount / ltp)`), and the uninvested cash remainder must equal `total_capital - sum(shares * ltp)`.
4. **Time Period Consistency:** Toggling between `1M` and `5Y` must correctly update both the charts and the annualization factor (252 trading days).
5. **Vercel Build Compatibility:** All Vite build scripts and asset bundles must compile cleanly without missing CSS classes or undefined references.

---

## Implementation Tasks

### Task 1: Production PostgreSQL Relational Schema & Migration

**Files:**
- Create: `docs/database/schema.sql`
- Test: `tests/test_schema_syntax.py`

**Interfaces:**
- Produces: DDL SQL definitions for `profiles`, `etf_universe`, `portfolios`, `portfolio_holdings`, `backtest_runs`, and Row-Level Security (RLS) policies.

- [ ] **Step 1: Write DDL schema test**
Verify SQL file exists, contains all 5 required tables, foreign keys, `ON DELETE CASCADE`, and check constraints (`weight >= 0 AND weight <= 1`).

- [ ] **Step 2: Create `docs/database/schema.sql`**
Write full PostgreSQL migration script including `profiles`, `etf_universe`, `portfolios`, `portfolio_holdings`, and `backtest_runs` with RLS policies and seed data for 15+ NSE ETFs.

- [ ] **Step 3: Run test to verify SQL validity**
Verify schema file syntax with Python SQL parser or pytest.

- [ ] **Step 4: Commit**
```bash
git add docs/database/schema.sql tests/test_schema_syntax.py
git commit -m "feat(db): Add PostgreSQL relational schema with RLS and check constraints"
```

---

### Task 2: Core Financial Times & Institutional Design System (`web/style.css`)

**Files:**
- Modify: `web/style.css`

**Interfaces:**
- Consumes: Google Fonts (`Newsreader`, `Inter`, `JetBrains Mono`).
- Produces: Global CSS variables (`--ft-paper: #FFF1E5; --ft-paper-card: #FAF0E6; --ft-navy: #0C2340; --ft-green: #00665E; --ft-claret: #990F3D; --ft-border: #D8C7B5;`).

- [ ] **Step 1: Replace neon glassmorphism CSS rules with FT design tokens**
Remove `.glow-orb`, neon shadows, and blurry translucent backdrops. Define the warm newsprint paper canvas, Oxford Navy headers, and high-contrast tabular typography.

- [ ] **Step 2: Add styles for Actionable Table and Collapsible Quant Drawer**
Style `.ft-table`, `.ft-stack-bar`, `.quant-drawer`, and clean vector SVG icons.

- [ ] **Step 3: Add responsive media queries**
Ensure cards, metric grids, and tables reflow smoothly on mobile (iOS Safari / Android Chrome).

- [ ] **Step 4: Commit**
```bash
git add web/style.css
git commit -m "feat(ui): Implement Financial Times newsprint and Oxford Navy design system"
```

---

### Task 3: Homepage Optimizer Redesign with Option D Execution Schedule & Quant Drawer

**Files:**
- Modify: `web/index.html`
- Modify: `web/main.js`

**Interfaces:**
- Consumes: Live NSE price feed from `/api/prices` or Yahoo Finance.
- Produces: Dynamic share quantity calculations, allocation bar, and toggleable SLSQP solver telemetry.

- [ ] **Step 1: Update `web/index.html` markup**
Refactor the homepage hero, masthead, 4 KPI cards (Return, Volatility, Sharpe, Drawdown), and add Option D's Actionable Share Execution Schedule and Quant Solver Drawer.

- [ ] **Step 2: Update `web/main.js` calculation engine**
Implement `updateExecutionSchedule(capital, allocations, prices)`:
- Computes exact share quantity: `shares = Math.floor((capital * weight) / price)`.
- Computes exact invested value: `shares * price`.
- Computes uninvested cash remainder: `capital - totalInvested`.
- Implements `toggleQuantDrawer()` for interactive telemetry display.

- [ ] **Step 3: Verify execution schedule math in browser**
Test with ₹5,00,000 capital: verify sum of holdings + cash remainder equals ₹5,00,000 exactly.

- [ ] **Step 4: Commit**
```bash
git add web/index.html web/main.js
git commit -m "feat(optimizer): Integrate Option D execution schedule and quant telemetry drawer in FT theme"
```

---

### Task 4: Live Dashboard & Period Filter Integration (`web/dashboard.html`)

**Files:**
- Modify: `web/dashboard.html`

**Interfaces:**
- Consumes: `/api/history?period=1mo` (and `1d`, `5d`, `1mo`, `3mo`, `1y`, `5y`).
- Produces: Cumulative Growth, Drawdown Analysis, and Monte Carlo Efficient Frontier charts styled in the FT palette.

- [ ] **Step 1: Update `web/dashboard.html` layout**
Apply the Financial Times newsprint container, editorial masthead, and ensure period buttons (`1D`, `5D`, `1M`, `3M`, `1Y`, `5Y`) are prominently styled.

- [ ] **Step 2: Update Chart.js color themes**
Configure Chart.js datasets:
- Max Sharpe: Oxford Navy (`#0C2340`) with thick solid line.
- Min Volatility: Forest Green (`#00665E`) with solid line.
- Equal Weight: Claret (`#990F3D`) with dashed line.
- Chart canvas grid lines: Warm sand (`#E9D5C3`).

- [ ] **Step 3: Test period switching (`1M` vs `1D` vs `1Y`)**
Verify switching periods fetches `/api/history` and re-renders the charts without errors.

- [ ] **Step 4: Commit**
```bash
git add web/dashboard.html
git commit -m "feat(dashboard): Restyle live market dashboard and charts with FT theme and active period filters"
```

---

### Task 5: Head-to-Head Compare Studio & 9x9 Correlation Heatmap Redesign (`web/compare.html`)

**Files:**
- Modify: `web/compare.html`

**Interfaces:**
- Consumes: Historical correlation matrix and comparative risk metrics.
- Produces: 9x9 Correlation Heatmap and Head-to-Head Comparison Table in FT styling.

- [ ] **Step 1: Refactor `web/compare.html` masthead and containers**
Align with the unified Financial Times newsprint layout and Oxford Navy typography.

- [ ] **Step 2: Style the 9x9 Correlation Heatmap**
Use high-contrast financial colors:
- Positive correlation: Warm Racing Green (`#00665E` tints).
- Negative correlation / hedge: Claret (`#990F3D` tints).
- Zero/low correlation: Warm cream (`#FAF0E6`).

- [ ] **Step 3: Restyle Head-to-Head Metrics Table**
Format metrics (Return, Volatility, Sharpe, Sortino, Drawdown, Calmar, CVaR 95%) with bold values, checkmarks for top performers, and tabular numbers.

- [ ] **Step 4: Commit**
```bash
git add web/compare.html
git commit -m "feat(compare): Modernize compare studio and 9x9 correlation heatmap in FT palette"
```

---

### Task 6: End-to-End Build, Verification, & Vercel Deployment Check

**Files:**
- Modify: `package.json` (if needed for build scripts)
- Test: Full Vite build and serverless endpoint verification.

- [ ] **Step 1: Run Vite production build locally**
Run: `cd web && npm run build`
Expected: SUCCESS with zero CSS/JS bundle errors.

- [ ] **Step 2: Verify all 3 pages (`index.html`, `dashboard.html`, `compare.html`)**
Ensure links, export buttons (PDF & Excel), and responsive navigation work across all pages.

- [ ] **Step 3: Final commit and push to Vercel**
```bash
git add .
git commit -m "feat(release): Deploy FT institutional hybrid redesign with preserved live charts and period filters"
git push origin main
```
Verify live deployment at `https://web-six-zeta-72.vercel.app`.
