export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'public, max-age=3600');

  const meta = {
    start: '2019-01-01',
    end: new Date().toISOString().split('T')[0],
    n_days: 1420,
    rf: 6.8,
  };

  const portfolios = {
    maxsharpe: {
      name: 'Max Sharpe',
      icon: '⭐',
      weights: {
        GoldBees: 0.25,
        Mid150Bees: 0.25,
        Nasdaq100: 0.25,
        JuniorBees: 0.15,
        NiftyBees: 0.10,
        BankBees: 0.0,
        SilverBees: 0.0,
        GSec10Yr: 0.0,
        LiquidBees: 0.0,
      },
      metrics: {
        return: 19.44,
        vol: 13.02,
        sharpe: 0.9631,
        sortino: 1.482,
        max_dd: -8.42,
        cvar95: -1.42,
        calmar: 2.308,
      },
    },
    minvol: {
      name: 'Min Volatility',
      icon: '🛡️',
      weights: {
        LiquidBees: 0.45,
        GSec10Yr: 0.45,
        Mid150Bees: 0.086,
        Nasdaq100: 0.012,
        JuniorBees: 0.002,
        NiftyBees: 0.0,
        BankBees: 0.0,
        GoldBees: 0.0,
        SilverBees: 0.0,
      },
      metrics: {
        return: 8.12,
        vol: 4.88,
        sharpe: 0.2705,
        sortino: 0.412,
        max_dd: -3.15,
        cvar95: -0.48,
        calmar: 2.578,
      },
    },
    equal: {
      name: 'Equal Weight',
      icon: '⚖️',
      weights: {
        NiftyBees: 0.111,
        JuniorBees: 0.111,
        BankBees: 0.111,
        Mid150Bees: 0.111,
        Nasdaq100: 0.111,
        GoldBees: 0.111,
        SilverBees: 0.111,
        GSec10Yr: 0.111,
        LiquidBees: 0.111,
      },
      metrics: {
        return: 14.85,
        vol: 11.20,
        sharpe: 0.7188,
        sortino: 1.092,
        max_dd: -11.85,
        cvar95: -1.25,
        calmar: 1.253,
      },
    },
  };

  // Generate synthetic sample growth curves for visual charts
  const dates = [];
  const sh_curve = [];
  const mv_curve = [];
  const eq_curve = [];
  let sh_val = 100, mv_val = 100, eq_val = 100;
  const now = new Date();
  for (let i = 60; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 86400000 * 2);
    dates.push(d.toISOString().split('T')[0]);
    sh_val *= 1 + (0.0006 + (Math.sin(i / 5) * 0.005));
    mv_val *= 1 + (0.0003 + (Math.sin(i / 7) * 0.002));
    eq_val *= 1 + (0.00045 + (Math.sin(i / 6) * 0.004));
    sh_curve.push(Number(sh_val.toFixed(2)));
    mv_curve.push(Number(mv_val.toFixed(2)));
    eq_curve.push(Number(eq_val.toFixed(2)));
  }

  // Drawdown series
  const dd_sh = sh_curve.map((v, i) => {
    const peak = Math.max(...sh_curve.slice(0, i + 1));
    return Number((((v - peak) / peak) * 100).toFixed(2));
  });
  const dd_mv = mv_curve.map((v, i) => {
    const peak = Math.max(...mv_curve.slice(0, i + 1));
    return Number((((v - peak) / peak) * 100).toFixed(2));
  });
  const dd_eq = eq_curve.map((v, i) => {
    const peak = Math.max(...eq_curve.slice(0, i + 1));
    return Number((((v - peak) / peak) * 100).toFixed(2));
  });

  // Correlation matrix
  const matrix = [
    [1.00, 0.69, 0.85, 0.58, 0.39, 0.32, 0.30, 0.41, -0.02],
    [0.69, 1.00, 0.69, 0.40, 0.58, 0.38, 0.49, 0.23, -0.18],
    [0.85, 0.69, 1.00, 0.47, 0.27, 0.32, 0.26, 0.43,  0.02],
    [0.58, 0.40, 0.47, 1.00, 0.52, 0.44, 0.29, 0.20,  0.18],
    [0.39, 0.58, 0.27, 0.52, 1.00, 0.50, 0.59,-0.10, -0.17],
    [0.32, 0.38, 0.32, 0.44, 0.50, 1.00, 0.79, 0.29, -0.31],
    [0.30, 0.49, 0.26, 0.29, 0.59, 0.79, 1.00, 0.09, -0.49],
    [0.41, 0.23, 0.43, 0.20,-0.10, 0.29, 0.09, 1.00,  0.03],
    [-0.02,-0.18, 0.02, 0.18,-0.17,-0.31,-0.49, 0.03,  1.00]
  ];

  // Efficient frontier 200 random points
  const frontier = [];
  for (let i = 0; i < 200; i++) {
    const vol = 5.0 + Math.random() * 15.0;
    const ret = 7.0 + Math.sqrt(vol) * 3.5 + (Math.random() - 0.5) * 3.0;
    const sharpe = (ret - 6.8) / vol;
    frontier.push({ vol: Number(vol.toFixed(2)), return: Number(ret.toFixed(2)), sharpe: Number(sharpe.toFixed(2)) });
  }

  return res.status(200).json({
    meta,
    portfolios,
    series: {
      dates,
      growth: {
        maxsharpe: sh_curve,
        minvol: mv_curve,
        equal: eq_curve,
      },
      drawdown: {
        maxsharpe: dd_sh,
        minvol: dd_mv,
        equal: dd_eq,
      },
    },
    correlation: {
      assets: ['Nifty', 'Junior', 'Bank', 'Mid150', 'Nasdaq', 'Gold', 'Silver', 'GSec10Yr', 'Liquid'],
      matrix,
    },
    frontier,
  });
}
