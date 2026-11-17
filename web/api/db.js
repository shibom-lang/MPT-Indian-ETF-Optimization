/**
 * web/api/db.js
 * 
 * Production Neon Serverless PostgreSQL Database Client
 * Uses @neondatabase/serverless over HTTP for instant queries with zero connection pooling lag.
 * Fully compatible with Vercel Marketplace Neon Postgres and Supabase.
 */

import { neon, neonConfig } from '@neondatabase/serverless';

// Cache client across hot Lambda invocations
let sqlClient = null;

export function getDb() {
  const connectionString = 
    process.env.DATABASE_URL || 
    process.env.POSTGRES_URL || 
    process.env.POSTGRES_PRISMA_URL;

  if (!connectionString) {
    return null;
  }

  if (!sqlClient) {
    // Config HTTP pipelining for low latency
    sqlClient = neon(connectionString);
  }

  return sqlClient;
}

export async function query(queryText, params = []) {
  const sql = getDb();
  if (!sql) {
    return {
      connected: false,
      error: 'DATABASE_URL not configured. Add Neon Postgres in Vercel Storage tab.',
      rows: []
    };
  }

  try {
    const rows = await sql(queryText, params);
    return { connected: true, rows };
  } catch (err) {
    console.error('Neon DB Query Error:', err);
    return { connected: false, error: err.message, rows: [] };
  }
}
