/**
 * web/api/db.js
 * 
 * Production Neon Serverless PostgreSQL Database Client
 * Uses @neondatabase/serverless with dynamic import for zero-crash fallback across all Node.js runtimes.
 * Fully compatible with Vercel Marketplace Neon Postgres and Supabase.
 */

let sqlClient = null;

export async function getDb() {
  const connectionString = 
    process.env.DATABASE_URL || 
    process.env.POSTGRES_URL || 
    process.env.POSTGRES_PRISMA_URL;

  if (!connectionString) {
    return null;
  }

  if (!sqlClient) {
    try {
      const { neon } = await import('@neondatabase/serverless');
      sqlClient = neon(connectionString);
    } catch (e) {
      console.warn('Neon serverless driver dynamic import fallback:', e.message);
      return null;
    }
  }

  return sqlClient;
}

export async function query(queryText, params = []) {
  try {
    const sql = await getDb();
    if (!sql) {
      return {
        connected: false,
        error: 'DATABASE_URL not configured. Add Neon Postgres in Vercel Storage tab.',
        rows: []
      };
    }

    const rows = await sql(queryText, params);
    return { connected: true, rows };
  } catch (err) {
    console.error('Neon DB Query Error:', err);
    return { connected: false, error: err.message, rows: [] };
  }
}
