# 🐘 Neon Serverless PostgreSQL Integration Guide

## 1. Overview
ETF Optima integrates with **Neon Serverless PostgreSQL** via Vercel Marketplace. Neon provides serverless connection pooling, sub-10ms query latency over HTTP/WebSockets (`@neondatabase/serverless`), branching capabilities, and autoscaling compute.

---

## 2. One-Click Provisioning on Vercel

1. Open your Vercel Dashboard and navigate to the **ETF Optima (`web`)** project.
2. Navigate to the **Storage** tab.
3. Click **Create Database** and select **Neon (Serverless Postgres)**.
4. Select your preferred region (e.g. `ap-southeast-1` or `eu-central-1`) and click **Create**.
5. Vercel automatically binds the following environment variables to all deployment environments (Production, Preview, Development):
   - `DATABASE_URL` (Pooled connection string)
   - `POSTGRES_URL`
   - `POSTGRES_URL_NON_POOLING`
   - `POSTGRES_PRISMA_URL`

---

## 3. Applying the Relational Schema

Copy and paste the contents of [`docs/database/schema.sql`](file:///Users/surajitdas/project%20etf%20analysis/docs/database/schema.sql) directly into the **Neon SQL Editor Console**:

```sql
-- 1. Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Creates auth compatibility, profiles, etf_universe, portfolios, holdings, and backtests
-- See docs/database/schema.sql for the complete DDL definition
```

### Seed Universe Included:
The schema automatically seeds the curated NSE 9-ETF Universe:
- `NIFTYBEES.NS` (Nippon India Nifty 50 BeES - Large Cap)
- `JUNIORBEES.NS` (Nippon India Nifty Next 50 - Large/Mid Cap)
- `MID150BEES.NS` (Nippon India Nifty Midcap 150 - Mid Cap)
- `BANKBEES.NS` (Nippon India Nifty Bank BeES - Banking Sector)
- `GOLDBEES.NS` (Nippon India ETF Gold BeES - Precious Metals)
- `SILVERBEES.NS` (Nippon India ETF Silver BeES - Precious Metals)
- `MON100.NS` (Motilal Oswal Nasdaq 100 ETF - Global Tech)
- `LTGILTBEES.NS` (Nippon India ETF Nifty 8-13 yr G-Sec - Sovereign Debt)
- `LIQUIDBEES.NS` (Nippon India ETF Liquid BeES - Cash Equivalent)

---

## 4. Serverless Edge Architecture (`@neondatabase/serverless`)

Queries execute over stateless HTTP pipelining using the lightweight official Neon client:

```javascript
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL);
const rows = await sql`SELECT * FROM public.etf_universe WHERE is_active = true`;
```

- **Zero Cold Start Penalty**: HTTP transactions avoid TCP handshake roundtrips in serverless Lambdas.
- **Fail-Safe Fallback**: If `DATABASE_URL` is unset, `web/api/portfolios.js` serves in-memory defaults so the UI remains 100% operational.
