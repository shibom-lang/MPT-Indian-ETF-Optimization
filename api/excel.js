/**
 * api/excel.js & web/api/excel.js
 * 
 * Vercel Serverless Endpoint: Dynamic Multi-Sheet Institutional Excel Wealth Model
 * Formatted in Financial Times Editorial Palette (SpreadsheetML / Excel XML 2003)
 * Fully compatible with Microsoft Excel, Apple Numbers, LibreOffice & Google Sheets.
 */

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const query = req.query || {};
  let amount = parseFloat(query.amount);
  if (isNaN(amount) || amount <= 0) amount = 100000;

  const strategyKey = (query.strategy || 'maxsharpe').toLowerCase();

  const ETF_META = {
    'NIFTYBEES.NS': { short: 'NiftyBees', name: 'Nippon India Nifty 50 BeES', assetClass: 'Large Cap Equity', ltp: 289.60, beta: 1.00, divYield: 0.012 },
    'JUNIORBEES.NS': { short: 'JuniorBees', name: 'Nippon India Nifty Next 50 BeES', assetClass: 'Next 50 Large-Mid', ltp: 742.10, beta: 1.15, divYield: 0.009 },
    'BANKBEES.NS': { short: 'BankBees', name: 'Nippon India Nifty Bank BeES', assetClass: 'Banking & Financials', ltp: 54.10, beta: 1.28, divYield: 0.008 },
    'MON100.NS': { short: 'Nasdaq100', name: 'Motilal Oswal Nasdaq 100 ETF', assetClass: 'US Tech & USD Hedge', ltp: 172.50, beta: 0.85, divYield: 0.005 },
    'GOLDBEES.NS': { short: 'GoldBees', name: 'Nippon India ETF Gold BeES', assetClass: 'Physical Gold / Precious Metals', ltp: 68.45, beta: 0.05, divYield: 0.000 },
    'SILVERBEES.NS': { short: 'SilverBees', name: 'Nippon India ETF Silver BeES', assetClass: 'Physical Silver Commodity', ltp: 96.20, beta: 0.35, divYield: 0.000 },
    'GSEC10IETF.NS': { short: 'GSec10Yr', name: 'Nippon India ETF Nifty 10yr Benchmark G-Sec', assetClass: 'Sovereign Government Bonds', ltp: 104.80, beta: -0.05, divYield: 0.068 },
    'LIQUIDBEES.NS': { short: 'LiquidBees', name: 'Nippon India ETF Liquid BeES', assetClass: 'Overnight Cash Equivalent', ltp: 1000.00, beta: 0.00, divYield: 0.064 }
  };

  // Try to fetch live LTP from Yahoo Finance with fallback
  try {
    const liveResults = await Promise.all(
      Object.keys(ETF_META).map(async (ticker) => {
        try {
          const resp = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=2d`, {
            headers: { 'User-Agent': 'Mozilla/5.0' },
            signal: AbortSignal.timeout(1500)
          });
          if (resp.ok) {
            const data = await resp.json();
            const px = data.chart?.result?.[0]?.meta?.regularMarketPrice;
            if (px && px > 0) ETF_META[ticker].ltp = px;
          }
        } catch (_) {}
      })
    );
  } catch (_) {}

  const STRATEGIES = {
    maxsharpe: {
      name: 'Max Sharpe Portfolio',
      desc: 'Optimal risk-adjusted growth enforcing 45% regulatory single-asset cap',
      expectedReturn: 0.2727,
      volatility: 0.1857,
      sharpe: 1.1023,
      sortino: 1.3660,
      maxDrawdown: -0.0395,
      weights: {
        'MON100.NS': 0.3773,
        'GOLDBEES.NS': 0.3413,
        'BANKBEES.NS': 0.1669,
        'SILVERBEES.NS': 0.1146,
        'NIFTYBEES.NS': 0.0000,
        'JUNIORBEES.NS': 0.0000,
        'GSEC10IETF.NS': 0.0000,
        'LIQUIDBEES.NS': 0.0000
      }
    },
    minvol: {
      name: 'Min Volatility Portfolio',
      desc: 'Capital preservation & drawdown protection with high fixed-income weighting',
      expectedReturn: 0.0363,
      volatility: 0.0347,
      sharpe: -0.9130,
      sortino: -1.4780,
      maxDrawdown: -0.0172,
      weights: {
        'LIQUIDBEES.NS': 0.4500,
        'GSEC10IETF.NS': 0.4139,
        'NIFTYBEES.NS': 0.1039,
        'GOLDBEES.NS': 0.0218,
        'MON100.NS': 0.0104,
        'BANKBEES.NS': 0.0000,
        'SILVERBEES.NS': 0.0000,
        'JUNIORBEES.NS': 0.0000
      }
    },
    equal: {
      name: 'Equal Weight Benchmark',
      desc: 'Naive 12.5% per asset benchmark across all 8 liquid asset classes',
      expectedReturn: 0.1679,
      volatility: 0.1221,
      sharpe: 0.8180,
      sortino: 1.0150,
      maxDrawdown: -0.0726,
      weights: {
        'NIFTYBEES.NS': 0.1250,
        'JUNIORBEES.NS': 0.1250,
        'BANKBEES.NS': 0.1250,
        'MON100.NS': 0.1250,
        'GOLDBEES.NS': 0.1250,
        'SILVERBEES.NS': 0.1250,
        'GSEC10IETF.NS': 0.1250,
        'LIQUIDBEES.NS': 0.1250
      }
    }
  };

  const selectedStrat = STRATEGIES[strategyKey] || STRATEGIES.maxsharpe;

  // Build allocation table with Option D integer whole-share logic
  let totalInvested = 0;
  const allocations = [];

  for (const [ticker, weight] of Object.entries(selectedStrat.weights)) {
    const meta = ETF_META[ticker] || { short: ticker, name: ticker, assetClass: 'ETF', ltp: 100, beta: 1, divYield: 0.01 };
    const targetRupees = amount * weight;
    const wholeShares = Math.floor(targetRupees / meta.ltp);
    const actualInvested = wholeShares * meta.ltp;
    totalInvested += actualInvested;

    allocations.push({
      ticker: meta.short,
      fullName: meta.name,
      assetClass: meta.assetClass,
      weightTarget: weight,
      ltp: meta.ltp,
      shares: wholeShares,
      invested: actualInvested,
      divYield: meta.divYield,
      beta: meta.beta
    });
  }

  const cashRemainder = amount - totalInvested;
  const expR = selectedStrat.expectedReturn;
  const vol = selectedStrat.volatility;

  // Generate 10-Year Projections
  const projections = [];
  let curExp = amount;
  let curOpt = amount;
  let curCons = amount;

  for (let yr = 0; yr <= 10; yr++) {
    if (yr === 0) {
      projections.push({
        year: 0,
        label: 'Initial Investment',
        expected: amount,
        optimistic: amount,
        conservative: amount,
        dividendIncome: 0,
        annualGrowth: 0
      });
    } else {
      const expVal = amount * Math.pow(1 + expR, yr);
      const optVal = amount * Math.pow(1 + expR + vol, yr);
      const consVal = amount * Math.pow(Math.max(1.01, 1 + expR - vol), yr);
      const divInc = expVal * 0.018; // ~1.8% portfolio aggregate cash dividend yield
      const growth = expVal - (amount * Math.pow(1 + expR, yr - 1));

      projections.push({
        year: yr,
        label: `End of Year ${yr}`,
        expected: expVal,
        optimistic: optVal,
        conservative: consVal,
        dividendIncome: divInc,
        annualGrowth: growth
      });
    }
  }

  // Generate SpreadsheetML (XML Spreadsheet 2003)
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:x="urn:schemas-microsoft-com:office:excel"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:html="http://www.w3.org/TR/REC-html40">
 <DocumentProperties xmlns="urn:schemas-microsoft-com:office:office">
  <Title>ETF Optima — Institutional Wealth Model</Title>
  <Subject>Modern Portfolio Theory Indian ETF Optimization</Subject>
  <Author>ETF Optima Quantitative Research</Author>
  <Created>${new Date().toISOString()}</Created>
 </DocumentProperties>
 <Styles>
  <Style ss:ID="Default" ss:Name="Normal">
   <Alignment ss:Vertical="Center"/>
   <Borders/>
   <Font ss:FontName="Calibri" x:Family="Swiss" ss:Size="11" ss:Color="#0C2340"/>
   <Interior/>
   <NumberFormat/>
   <Protection/>
  </Style>
  <!-- Headers -->
  <Style ss:ID="TitleStyle">
   <Font ss:FontName="Georgia" ss:Size="16" ss:Bold="1" ss:Color="#0C2340"/>
   <Interior ss:Color="#FFF1E5" ss:Pattern="Solid"/>
  </Style>
  <Style ss:ID="SubTitleStyle">
   <Font ss:FontName="Calibri" ss:Size="10" ss:Italic="1" ss:Color="#555555"/>
   <Interior ss:Color="#FFF1E5" ss:Pattern="Solid"/>
  </Style>
  <Style ss:ID="HeaderStyle">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#FFFFFF"/>
   <Interior ss:Color="#0C2340" ss:Pattern="Solid"/>
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
   <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="2" ss:Color="#000000"/>
   </Borders>
  </Style>
  <Style ss:ID="HeaderGold">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#FFFFFF"/>
   <Interior ss:Color="#C99700" ss:Pattern="Solid"/>
   <Alignment ss:Horizontal="Center" ss:Vertical="Center"/>
  </Style>
  <!-- Data cells -->
  <Style ss:ID="BoldText">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#0C2340"/>
  </Style>
  <Style ss:ID="ZebraText">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Color="#0C2340"/>
   <Interior ss:Color="#FDF7F2" ss:Pattern="Solid"/>
  </Style>
  <Style ss:ID="Currency">
   <Font ss:FontName="Consolas" ss:Size="11" ss:Color="#0C2340"/>
   <NumberFormat ss:Format="&quot;₹&quot;#,##0.00"/>
  </Style>
  <Style ss:ID="CurrencyZebra">
   <Font ss:FontName="Consolas" ss:Size="11" ss:Color="#0C2340"/>
   <Interior ss:Color="#FDF7F2" ss:Pattern="Solid"/>
   <NumberFormat ss:Format="&quot;₹&quot;#,##0.00"/>
  </Style>
  <Style ss:ID="CurrencyBold">
   <Font ss:FontName="Consolas" ss:Size="11" ss:Bold="1" ss:Color="#0C2340"/>
   <NumberFormat ss:Format="&quot;₹&quot;#,##0.00"/>
  </Style>
  <Style ss:ID="Percent">
   <Font ss:FontName="Consolas" ss:Size="11" ss:Color="#0C2340"/>
   <NumberFormat ss:Format="0.00%"/>
  </Style>
  <Style ss:ID="PercentZebra">
   <Font ss:FontName="Consolas" ss:Size="11" ss:Color="#0C2340"/>
   <Interior ss:Color="#FDF7F2" ss:Pattern="Solid"/>
   <NumberFormat ss:Format="0.00%"/>
  </Style>
  <Style ss:ID="Integer">
   <Font ss:FontName="Consolas" ss:Size="11" ss:Color="#0C2340"/>
   <Alignment ss:Horizontal="Right"/>
   <NumberFormat ss:Format="#,##0"/>
  </Style>
  <Style ss:ID="IntegerZebra">
   <Font ss:FontName="Consolas" ss:Size="11" ss:Color="#0C2340"/>
   <Alignment ss:Horizontal="Right"/>
   <Interior ss:Color="#FDF7F2" ss:Pattern="Solid"/>
   <NumberFormat ss:Format="#,##0"/>
  </Style>
  <Style ss:ID="TotalRow">
   <Font ss:FontName="Calibri" ss:Size="11" ss:Bold="1" ss:Color="#0C2340"/>
   <Interior ss:Color="#EBF3FC" ss:Pattern="Solid"/>
   <Borders>
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#0C2340"/>
    <Border ss:Position="Bottom" ss:LineStyle="Double" ss:Weight="3" ss:Color="#0C2340"/>
   </Borders>
  </Style>
  <Style ss:ID="TotalCurrency">
   <Font ss:FontName="Consolas" ss:Size="11" ss:Bold="1" ss:Color="#0C2340"/>
   <Interior ss:Color="#EBF3FC" ss:Pattern="Solid"/>
   <NumberFormat ss:Format="&quot;₹&quot;#,##0.00"/>
   <Borders>
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" ss:Color="#0C2340"/>
    <Border ss:Position="Bottom" ss:LineStyle="Double" ss:Weight="3" ss:Color="#0C2340"/>
   </Borders>
  </Style>
 </Styles>

 <!-- SHEET 1: OPTIMAL PORTFOLIO ALLOCATION -->
 <Worksheet ss:Name="1. Portfolio Allocation">
  <Table ss:DefaultColumnWidth="110">
   <Column ss:Width="90"/>
   <Column ss:Width="220"/>
   <Column ss:Width="170"/>
   <Column ss:Width="90"/>
   <Column ss:Width="90"/>
   <Column ss:Width="90"/>
   <Column ss:Width="120"/>
   <Column ss:Width="90"/>
   <Column ss:Width="80"/>

   <Row ss:Height="30">
    <Cell ss:MergeAcross="8" ss:StyleID="TitleStyle"><Data ss:Type="String">ETF OPTIMA — ${selectedStrat.name.toUpperCase()}</Data></Cell>
   </Row>
   <Row ss:Height="20">
    <Cell ss:MergeAcross="8" ss:StyleID="SubTitleStyle"><Data ss:Type="String">Capital: ₹${amount.toLocaleString('en-IN')} | Target Expected Return: ${(expR * 100).toFixed(2)}% p.a. | Volatility: ${(vol * 100).toFixed(2)}% | Sharpe: ${selectedStrat.sharpe.toFixed(3)}</Data></Cell>
   </Row>
   <Row ss:Height="8"/>

   <Row ss:Height="24">
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Ticker</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Instrument Name</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Asset Class</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Target %</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">LTP (₹)</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Whole Shares</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Actual Invested</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Div Yield</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Beta (NSE)</Data></Cell>
   </Row>

   ${allocations.map((a, idx) => {
     const zebra = idx % 2 === 1;
     const textStyle = zebra ? 'ZebraText' : 'Default';
     const currStyle = zebra ? 'CurrencyZebra' : 'Currency';
     const pctStyle = zebra ? 'PercentZebra' : 'Percent';
     const intStyle = zebra ? 'IntegerZebra' : 'Integer';
     return `
   <Row ss:Height="20">
    <Cell ss:StyleID="${textStyle}"><Data ss:Type="String">${a.ticker}</Data></Cell>
    <Cell ss:StyleID="${textStyle}"><Data ss:Type="String">${a.fullName}</Data></Cell>
    <Cell ss:StyleID="${textStyle}"><Data ss:Type="String">${a.assetClass}</Data></Cell>
    <Cell ss:StyleID="${pctStyle}"><Data ss:Type="Number">${a.weightTarget}</Data></Cell>
    <Cell ss:StyleID="${currStyle}"><Data ss:Type="Number">${a.ltp}</Data></Cell>
    <Cell ss:StyleID="${intStyle}"><Data ss:Type="Number">${a.shares}</Data></Cell>
    <Cell ss:StyleID="${currStyle}"><Data ss:Type="Number">${a.invested}</Data></Cell>
    <Cell ss:StyleID="${pctStyle}"><Data ss:Type="Number">${a.divYield}</Data></Cell>
    <Cell ss:StyleID="${textStyle}"><Data ss:Type="Number">${a.beta}</Data></Cell>
   </Row>`;
   }).join('')}

   <Row ss:Height="22">
    <Cell ss:StyleID="TotalRow"><Data ss:Type="String">TOTAL ALLOCATED</Data></Cell>
    <Cell ss:StyleID="TotalRow"><Data ss:Type="String"></Data></Cell>
    <Cell ss:StyleID="TotalRow"><Data ss:Type="String"></Data></Cell>
    <Cell ss:StyleID="TotalRow"><Data ss:Type="String">100.00%</Data></Cell>
    <Cell ss:StyleID="TotalRow"><Data ss:Type="String"></Data></Cell>
    <Cell ss:StyleID="TotalRow"><Data ss:Type="Number">${allocations.reduce((sum, a) => sum + a.shares, 0)}</Data></Cell>
    <Cell ss:StyleID="TotalCurrency"><Data ss:Type="Number">${totalInvested}</Data></Cell>
    <Cell ss:StyleID="TotalRow"><Data ss:Type="String"></Data></Cell>
    <Cell ss:StyleID="TotalRow"><Data ss:Type="String"></Data></Cell>
   </Row>

   <Row ss:Height="20">
    <Cell ss:StyleID="BoldText"><Data ss:Type="String">CASH REMAINDER</Data></Cell>
    <Cell ss:MergeAcross="4" ss:StyleID="Default"><Data ss:Type="String">Unallocated cash retained in trading account due to whole-share integer boundary constraints</Data></Cell>
    <Cell ss:StyleID="CurrencyBold"><Data ss:Type="Number">${cashRemainder.toFixed(2)}</Data></Cell>
    <Cell ss:MergeAcross="1" ss:StyleID="Default"><Data ss:Type="String"></Data></Cell>
   </Row>
  </Table>
 </Worksheet>

 <!-- SHEET 2: 10-YEAR WEALTH COMPOUNDING -->
 <Worksheet ss:Name="2. 10-Year Compounding">
  <Table ss:DefaultColumnWidth="140">
   <Column ss:Width="80"/>
   <Column ss:Width="160"/>
   <Column ss:Width="150"/>
   <Column ss:Width="150"/>
   <Column ss:Width="150"/>
   <Column ss:Width="140"/>

   <Row ss:Height="30">
    <Cell ss:MergeAcross="5" ss:StyleID="TitleStyle"><Data ss:Type="String">10-YEAR WEALTH ACCUMULATION SCHEDULE</Data></Cell>
   </Row>
   <Row ss:Height="20">
    <Cell ss:MergeAcross="5" ss:StyleID="SubTitleStyle"><Data ss:Type="String">Projected compound growth based on MPT expected return (${(expR * 100).toFixed(2)}%) and volatility band (±${(vol * 100).toFixed(2)}%)</Data></Cell>
   </Row>
   <Row ss:Height="8"/>

   <Row ss:Height="24">
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Year</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Milestone</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Expected Value (₹)</Data></Cell>
    <Cell ss:StyleID="HeaderGold"><Data ss:Type="String">Optimistic (+1σ) (₹)</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Conservative (-1σ) (₹)</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Annual Gain (₹)</Data></Cell>
   </Row>

   ${projections.map((p, idx) => {
     const zebra = idx % 2 === 1;
     const textStyle = zebra ? 'ZebraText' : 'Default';
     const currStyle = zebra ? 'CurrencyZebra' : 'Currency';
     return `
   <Row ss:Height="20">
    <Cell ss:StyleID="${textStyle}"><Data ss:Type="Number">${p.year}</Data></Cell>
    <Cell ss:StyleID="${textStyle}"><Data ss:Type="String">${p.label}</Data></Cell>
    <Cell ss:StyleID="${currStyle}"><Data ss:Type="Number">${p.expected.toFixed(2)}</Data></Cell>
    <Cell ss:StyleID="${currStyle}"><Data ss:Type="Number">${p.optimistic.toFixed(2)}</Data></Cell>
    <Cell ss:StyleID="${currStyle}"><Data ss:Type="Number">${p.conservative.toFixed(2)}</Data></Cell>
    <Cell ss:StyleID="${currStyle}"><Data ss:Type="Number">${p.annualGrowth.toFixed(2)}</Data></Cell>
   </Row>`;
   }).join('')}
  </Table>
 </Worksheet>

 <!-- SHEET 3: ANNUAL CASH FLOW & DIVIDENDS -->
 <Worksheet ss:Name="3. Dividend Cash Flows">
  <Table ss:DefaultColumnWidth="140">
   <Column ss:Width="80"/>
   <Column ss:Width="160"/>
   <Column ss:Width="160"/>
   <Column ss:Width="160"/>
   <Column ss:Width="160"/>

   <Row ss:Height="30">
    <Cell ss:MergeAcross="4" ss:StyleID="TitleStyle"><Data ss:Type="String">ESTIMATED ANNUAL CASH FLOWS &amp; DIVIDEND YIELDS</Data></Cell>
   </Row>
   <Row ss:Height="20">
    <Cell ss:MergeAcross="4" ss:StyleID="SubTitleStyle"><Data ss:Type="String">Projected cash inflows from sovereign bonds, cash equivalents, and corporate dividend yields</Data></Cell>
   </Row>
   <Row ss:Height="8"/>

   <Row ss:Height="24">
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Year</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Portfolio Value</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Est. Dividend Yield</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Annual Cash Flow (₹)</Data></Cell>
    <Cell ss:StyleID="HeaderStyle"><Data ss:Type="String">Monthly Passive Cash (₹)</Data></Cell>
   </Row>

   ${projections.filter(p => p.year > 0).map((p, idx) => {
     const zebra = idx % 2 === 1;
     const textStyle = zebra ? 'ZebraText' : 'Default';
     const currStyle = zebra ? 'CurrencyZebra' : 'Currency';
     return `
   <Row ss:Height="20">
    <Cell ss:StyleID="${textStyle}"><Data ss:Type="Number">${p.year}</Data></Cell>
    <Cell ss:StyleID="${currStyle}"><Data ss:Type="Number">${p.expected.toFixed(2)}</Data></Cell>
    <Cell ss:StyleID="${zebra ? 'PercentZebra' : 'Percent'}"><Data ss:Type="Number">0.018</Data></Cell>
    <Cell ss:StyleID="${currStyle}"><Data ss:Type="Number">${p.dividendIncome.toFixed(2)}</Data></Cell>
    <Cell ss:StyleID="${currStyle}"><Data ss:Type="Number">${(p.dividendIncome / 12).toFixed(2)}</Data></Cell>
   </Row>`;
   }).join('')}
  </Table>
 </Worksheet>
</Workbook>`;

  res.setHeader('Content-Type', 'application/vnd.ms-excel; charset=utf-8');
  res.setHeader('Content-Disposition', `attachment; filename="Portfolio_Wealth_Model_${strategyKey}.xls"`);
  return res.status(200).send(xml);
}
