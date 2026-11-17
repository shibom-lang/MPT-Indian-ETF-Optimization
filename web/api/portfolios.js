/**
 * web/api/portfolios.js
 * 
 * Vercel Serverless Endpoint: Save & Fetch ETF Portfolios
 * Backed by Neon Serverless PostgreSQL with HTTP pipelining
 */

import { query } from './db.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Health / Catalog check
  if (req.method === 'GET') {
    const dbResult = await query('SELECT ticker, name, asset_class, expense_ratio FROM public.etf_universe WHERE is_active = true ORDER BY ticker ASC');
    
    if (!dbResult.connected) {
      // Graceful fallback when Neon DB is not yet provisioned in Vercel
      return res.status(200).json({
        database: 'offline',
        provider: 'Neon Serverless Postgres',
        message: 'Neon database integration ready. Set DATABASE_URL in Vercel environment variables to persist custom portfolios.',
        catalog_sample: [
          { ticker: 'NIFTYBEES.NS', name: 'Nippon India Nifty 50 BeES', asset_class: 'Large Cap Equity' },
          { ticker: 'JUNIORBEES.NS', name: 'Nippon India Nifty Next 50 Junior BeES', asset_class: 'Next 50 Equity' },
          { ticker: 'GOLDBEES.NS', name: 'Nippon India ETF Gold BeES', asset_class: 'Precious Metals' },
          { ticker: 'MON100.NS', name: 'Motilal Oswal Nasdaq 100 ETF', asset_class: 'US Technology' }
        ]
      });
    }

    return res.status(200).json({
      database: 'connected',
      provider: 'Neon Serverless Postgres',
      etfs: dbResult.rows
    });
  }

  // Save portfolio
  if (req.method === 'POST') {
    try {
      const { name, strategy, investment_amount, holdings } = req.body || {};
      if (!name || !holdings) {
        return res.status(400).json({ error: 'Missing portfolio name or holdings array' });
      }

      const dbResult = await query(
        `INSERT INTO public.portfolios (name, strategy, investment_amount) 
         VALUES ($1, $2, $3) RETURNING id, name, created_at`,
        [name, strategy || 'custom', investment_amount || 500000]
      );

      return res.status(201).json({
        success: true,
        portfolio: dbResult.rows[0]
      });
    } catch (e) {
      return res.status(500).json({ error: e.message });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
