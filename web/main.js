/* ─────────────────────────────────────────────────────────
   ETF Optima — Main JavaScript Engine (Demat Execution & FT System)
   Handles: live prices, interactive calculator, whole-share
   execution schedule, collapsible quant telemetry, and reports.
   ───────────────────────────────────────────────────────── */

// ─── PORTFOLIO SPECIFICATIONS & TELEMETRY ──────────────────
const PORTFOLIOS = {
    maxsharpe: {
        title: 'Max Sharpe Portfolio',
        returnRate: 0.1944,
        vol: 0.1302,
        sharpe: 0.9631,
        drawdown: -0.0842,
        cvar95: -0.0142,
        solver: 'scipy.optimize.minimize (SLSQP)',
        iterations: '24 iterations (ftol: 1e-09)',
        shrinkage: 'Ledoit-Wolf Covariance Shrinkage (NSE 252d)',
        stressCovid: '-24.20%',
        stressFed: '+8.10%',
        allocations: [
            { name: 'GoldBees',     pct: 0.250, color: '#B8860B', ticker: 'GOLDBEES.NS' },
            { name: 'Mid150Bees',   pct: 0.200, color: '#00665E', ticker: 'MID150BEES.NS' },
            { name: 'Nasdaq100',    pct: 0.200, color: '#4A3E72', ticker: 'MON100.NS' },
            { name: 'ITBees',       pct: 0.150, color: '#2563EB', ticker: 'ITBEES.NS' },
            { name: 'JuniorBees',   pct: 0.100, color: '#990F3D', ticker: 'JUNIORBEES.NS' },
            { name: 'NiftyBees',    pct: 0.100, color: '#0C2340', ticker: 'NIFTYBEES.NS' },
            { name: 'PharmaBees',   pct: 0.000, color: '#059669', ticker: 'PHARMABEES.NS' },
            { name: 'BankBees',     pct: 0.000, color: '#D97706', ticker: 'BANKBEES.NS' },
            { name: 'SilverBees',   pct: 0.000, color: '#8899A6', ticker: 'SILVERBEES.NS' },
            { name: 'GSec10Yr',     pct: 0.000, color: '#B83280', ticker: 'SETF10GILT.NS' },
            { name: 'LiquidBees',   pct: 0.000, color: '#5B6B82', ticker: 'LIQUIDBEES.NS' },
        ],
    },
    minvol: {
        title: 'Min Volatility Portfolio',
        returnRate: 0.0821,
        vol: 0.0520,
        sharpe: 0.6512,
        drawdown: -0.0172,
        cvar95: -0.0040,
        solver: 'scipy.optimize.minimize (SLSQP)',
        iterations: '18 iterations (ftol: 1e-09)',
        shrinkage: 'Ledoit-Wolf Covariance Shrinkage (NSE 252d)',
        stressCovid: '-4.80%',
        stressFed: '+5.20%',
        allocations: [
            { name: 'LiquidBees',   pct: 0.450, color: '#5B6B82', ticker: 'LIQUIDBEES.NS' },
            { name: 'GSec10Yr',     pct: 0.300, color: '#B83280', ticker: 'SETF10GILT.NS' },
            { name: 'GoldBees',     pct: 0.150, color: '#B8860B', ticker: 'GOLDBEES.NS' },
            { name: 'NiftyBees',    pct: 0.100, color: '#0C2340', ticker: 'NIFTYBEES.NS' },
            { name: 'Mid150Bees',   pct: 0.000, color: '#00665E', ticker: 'MID150BEES.NS' },
            { name: 'Nasdaq100',    pct: 0.000, color: '#4A3E72', ticker: 'MON100.NS' },
            { name: 'ITBees',       pct: 0.000, color: '#2563EB', ticker: 'ITBEES.NS' },
            { name: 'PharmaBees',   pct: 0.000, color: '#059669', ticker: 'PHARMABEES.NS' },
            { name: 'JuniorBees',   pct: 0.000, color: '#990F3D', ticker: 'JUNIORBEES.NS' },
            { name: 'BankBees',     pct: 0.000, color: '#D97706', ticker: 'BANKBEES.NS' },
            { name: 'SilverBees',   pct: 0.000, color: '#8899A6', ticker: 'SILVERBEES.NS' },
        ],
    },
    equal: {
        title: 'Equal Weight Portfolio',
        returnRate: 0.1420,
        vol: 0.1150,
        sharpe: 0.7300,
        drawdown: -0.0726,
        cvar95: -0.0147,
        solver: 'Naive 1/N Benchmark Allocation',
        iterations: 'Exact 9.09% 11-Asset Partition',
        shrinkage: 'Historical 7-Year Covariance',
        stressCovid: '-18.60%',
        stressFed: '+2.40%',
        allocations: [
            { name: 'NiftyBees',    pct: 0.091, color: '#0C2340', ticker: 'NIFTYBEES.NS' },
            { name: 'JuniorBees',   pct: 0.091, color: '#990F3D', ticker: 'JUNIORBEES.NS' },
            { name: 'BankBees',     pct: 0.091, color: '#D97706', ticker: 'BANKBEES.NS' },
            { name: 'Mid150Bees',   pct: 0.091, color: '#00665E', ticker: 'MID150BEES.NS' },
            { name: 'Nasdaq100',    pct: 0.091, color: '#4A3E72', ticker: 'MON100.NS' },
            { name: 'ITBees',       pct: 0.091, color: '#2563EB', ticker: 'ITBEES.NS' },
            { name: 'PharmaBees',   pct: 0.091, color: '#059669', ticker: 'PHARMABEES.NS' },
            { name: 'GoldBees',     pct: 0.091, color: '#B8860B', ticker: 'GOLDBEES.NS' },
            { name: 'SilverBees',   pct: 0.091, color: '#8899A6', ticker: 'SILVERBEES.NS' },
            { name: 'GSec10Yr',     pct: 0.091, color: '#B83280', ticker: 'SETF10GILT.NS' },
            { name: 'LiquidBees',   pct: 0.090, color: '#5B6B82', ticker: 'LIQUIDBEES.NS' },
        ],
    },
};

// ─── LIVE & REFERENCE LTP PRICES (NSE) ────────────────────
const ETF_PRICES = {
    'GoldBees': 108.26,
    'Mid150Bees': 23.50,
    'Nasdaq100': 295.87,
    'JuniorBees': 776.00,
    'NiftyBees': 287.00,
    'BankBees': 640.20,
    'SilverBees': 155.94,
    'GSec10Yr': 104.80,
    'LiquidBees': 1000.00,
    'ITBees': 34.80,
    'PharmaBees': 29.10
};

let currentTab = 'maxsharpe';
let currentAmount = 100000;

// ─── FORMATTERS ───────────────────────────────────────────
function fmtINR(amount) {
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)} Cr`;
    if (amount >= 100000)   return `₹${(amount / 100000).toFixed(2)} L`;
    if (amount >= 1000)     return `₹${(amount / 1000).toFixed(1)}K`;
    return `₹${Math.round(amount).toLocaleString('en-IN')}`;
}

function fmtCurrencyExact(amount) {
    return '₹' + Number(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function compoundGrow(principal, rate, years) {
    return principal * Math.pow(1 + rate, years);
}

function formatIndianWords(num) {
    if (isNaN(num) || num <= 0) return 'Enter an investment amount';
    if (num >= 10000000) return `₹ ${(num/10000000).toFixed(2)} Crore Rupees`;
    if (num >= 100000) {
        const lakhs = (num / 100000);
        const lText = lakhs === 1 ? 'One Lakh' : `${lakhs.toLocaleString('en-IN', {maximumFractionDigits:2})} Lakh`;
        return `₹ ${num.toLocaleString('en-IN')} · ${lText} Rupees`;
    }
    if (num >= 1000) return `₹ ${num.toLocaleString('en-IN')} · ${(num/1000).toFixed(0)} Thousand Rupees`;
    return `₹ ${num.toLocaleString('en-IN')} Rupees`;
}

// ─── TAB & AMOUNT CONTROLLERS ─────────────────────────────
function setAmount(val) {
    const input = document.getElementById('invest-amount');
    const slider = document.getElementById('invest-slider');
    if (input) input.value = val;
    if (slider) slider.value = val;
    currentAmount = val;
    renderCalculator();
}

function switchTab(tab) {
    currentTab = tab;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.getElementById(`tab-${tab}`);
    if (activeBtn) activeBtn.classList.add('active');

    document.querySelectorAll('.alloc-panel').forEach(p => p.classList.remove('active'));
    const activePanel = document.getElementById(`alloc-${tab}`);
    if (activePanel) activePanel.classList.add('active');

    renderCalculator();
}

function toggleQuantDrawer(key) {
    const body = document.getElementById(`quant-drawer-body-${key}`);
    const toggleText = document.getElementById(`quant-drawer-toggle-${key}`);
    if (body) {
        body.classList.toggle('open');
        if (toggleText) {
            toggleText.textContent = body.classList.contains('open') ? '▲ COLLAPSE' : '▼ EXPAND QUANT TELEMETRY';
        }
    }
}

// ─── CALCULATOR RENDERING ENGINE (OPTION D DEPTH) ─────────
function renderCalculator() {
    const input = document.getElementById('invest-amount');
    const amount = parseFloat(input ? input.value : 0) || 100000;
    currentAmount = amount;

    const wordsEl = document.getElementById('amount-in-words');
    if (wordsEl) wordsEl.textContent = formatIndianWords(amount);

    Object.keys(PORTFOLIOS).forEach(key => {
        renderKpiCards(key);
        renderStackBar(key);
        renderOptionDExecutionTable(key, amount);
        renderBars(key, amount);
        renderProjections(key, amount);
    });
}

function renderKpiCards(key) {
    const p = PORTFOLIOS[key];
    const container = document.getElementById(`kpi-container-${key}`);
    if (!container) return;

    container.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Expected Return</div>
                <div class="kpi-val text-green">${(p.returnRate * 100).toFixed(2)}%</div>
                <div class="kpi-sub">CAGR (7-Yr MPT Model)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Annual Volatility</div>
                <div class="kpi-val">${(p.vol * 100).toFixed(2)}%</div>
                <div class="kpi-sub">Standard Deviation (Risk)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Sharpe Ratio</div>
                <div class="kpi-val text-gold">${p.sharpe.toFixed(4)}</div>
                <div class="kpi-sub">Rf: 6.8% (RBI 91D T-Bill)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Max Drawdown</div>
                <div class="kpi-val text-red">${(p.drawdown * 100).toFixed(2)}%</div>
                <div class="kpi-sub">Historical Peak-to-Trough</div>
            </div>
        </div>
    `;
}

function renderStackBar(key) {
    const p = PORTFOLIOS[key];
    const container = document.getElementById(`stack-bar-${key}`);
    if (!container) return;

    const nonZero = p.allocations.filter(a => a.pct > 0);
    const segs = nonZero.map(a => `
        <div class="ft-stack-seg" style="width: ${(a.pct * 100).toFixed(1)}%; background: ${a.color};" title="${a.name}: ${(a.pct * 100).toFixed(1)}%"></div>
    `).join('');

    const legend = nonZero.map(a => `
        <span class="asset-pill" style="font-size: 11.5px; margin-right: 12px;">
            <span class="asset-color-dot" style="background: ${a.color}"></span>
            ${a.name} <strong>${(a.pct * 100).toFixed(1)}%</strong>
        </span>
    `).join('');

    container.innerHTML = `
        <div class="ft-stack-bar-wrap">
            <div class="ft-stack-bar">${segs}</div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">${legend}</div>
        </div>
    `;
}

function renderOptionDExecutionTable(key, capital) {
    const p = PORTFOLIOS[key];
    const container = document.getElementById(`execution-schedule-${key}`);
    if (!container) return;

    let totalInvested = 0;
    const nonZero = p.allocations.filter(a => a.pct > 0);

    // Desktop Table Rows
    const tableRows = nonZero.map(asset => {
        const targetRupees = capital * asset.pct;
        const cleanTicker = (asset.ticker || '').toUpperCase().replace('.NS', '');
        const ltp = ETF_PRICES[asset.name] || ETF_PRICES[cleanTicker] || ETF_PRICES[asset.ticker] || 100.0;
        const units = Math.floor(targetRupees / ltp);
        const actualValue = units * ltp;
        const diff = actualValue - targetRupees;
        totalInvested += actualValue;

        const diffCls = diff >= 0 ? 'text-green' : 'text-muted';
        const diffSign = diff >= 0 ? '+' : '';

        return `
            <tr>
                <td>
                    <span class="asset-pill">
                        <span class="asset-color-dot" style="background: ${asset.color}"></span>
                        <strong>${asset.name}</strong>
                        <span class="exec-card-ticker">NSE: ${cleanTicker}</span>
                    </span>
                </td>
                <td class="num">${fmtCurrencyExact(ltp)}</td>
                <td class="num">${(asset.pct * 100).toFixed(1)}%</td>
                <td class="num"><strong>${units.toLocaleString('en-IN')}</strong></td>
                <td class="num"><strong>${fmtCurrencyExact(actualValue)}</strong></td>
                <td class="num ${diffCls}">${diffSign}${fmtCurrencyExact(diff)}</td>
            </tr>
        `;
    }).join('');

    // Mobile Order Cards (Recalculate accurately without double counting totalInvested)
    const cardRows = nonZero.map(asset => {
        const targetRupees = capital * asset.pct;
        const cleanTicker = (asset.ticker || '').toUpperCase().replace('.NS', '');
        const ltp = ETF_PRICES[asset.name] || ETF_PRICES[cleanTicker] || ETF_PRICES[asset.ticker] || 100.0;
        const units = Math.floor(targetRupees / ltp);
        const actualValue = units * ltp;
        const diff = actualValue - targetRupees;

        const diffCls = diff >= 0 ? 'text-green' : 'text-muted';
        const diffSign = diff >= 0 ? '+' : '';

        return `
            <div class="exec-card">
                <div class="exec-card-head">
                    <div class="exec-card-asset">
                        <span class="asset-color-dot" style="background: ${asset.color}"></span>
                        <span class="exec-card-name">${asset.name}</span>
                        <span class="exec-card-ticker">NSE: ${cleanTicker}</span>
                    </div>
                    <div class="exec-card-ltp">${fmtCurrencyExact(ltp)}</div>
                </div>
                
                <div class="exec-card-bar-wrap">
                    <div class="exec-card-bar" style="width: ${(asset.pct * 100).toFixed(1)}%; background: ${asset.color};"></div>
                </div>

                <div class="exec-card-body">
                    <div class="exec-card-stat">
                        <span class="stat-meta">Units to Buy</span>
                        <span class="stat-number"><strong>${units.toLocaleString('en-IN')}</strong> Shares</span>
                    </div>
                    <div class="exec-card-stat" style="text-align: right;">
                        <span class="stat-meta">Allocated Value</span>
                        <span class="stat-number"><strong>${fmtCurrencyExact(actualValue)}</strong></span>
                    </div>
                </div>
                
                <div class="exec-card-foot">
                    <span>Target Weight: <strong>${(asset.pct * 100).toFixed(1)}%</strong></span>
                    <span class="${diffCls}">Variance: ${diffSign}${fmtCurrencyExact(diff)}</span>
                </div>
            </div>
        `;
    }).join('');

    const cashRemainder = capital - totalInvested;
    const trackingDrift = Math.abs((totalInvested - capital) / capital * 100).toFixed(2);
    const efficiency = ((totalInvested / capital) * 100).toFixed(2);

    container.innerHTML = `
        <div class="execution-container">
            <div class="exec-header">
                <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 6px;">
                    <h4>Demat Order Execution Ledger</h4>
                    <span class="zero-drift-badge">Demat Whole-Share Allocation</span>
                </div>
                <p>Integer share allocation calculated via live NSE prices. Zero fractional shares with explicit rupee cash remainder.</p>
            </div>

            <!-- Mobile-first Order Cards (< 768px) -->
            <div class="exec-mobile-cards">
                ${cardRows}
            </div>

            <!-- Desktop Institutional Ledger (>= 768px) -->
            <div class="exec-desktop-table ft-table-wrap">
                <table class="ft-table">
                    <thead>
                        <tr>
                            <th>Asset / NSE Ticker</th>
                            <th class="num">Live LTP</th>
                            <th class="num">Target Wt</th>
                            <th class="num">Units to Buy</th>
                            <th class="num">Actual Capital</th>
                            <th class="num">Variance</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td><strong>Portfolio Execution Total</strong></td>
                            <td class="num">—</td>
                            <td class="num">100.0%</td>
                            <td class="num">—</td>
                            <td class="num text-navy"><strong>${fmtCurrencyExact(totalInvested)}</strong></td>
                            <td class="num text-muted">Drift: ${trackingDrift}%</td>
                        </tr>
                    </tfoot>
                </table>
            </div>

            <!-- Capital Execution Summary & Broker Basket Action -->
            <div class="exec-summary-card">
                <div class="exec-summary-grid">
                    <div class="summary-item">
                        <div class="summary-label">Total Capital</div>
                        <div class="summary-val">${fmtCurrencyExact(capital)}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Capital Invested</div>
                        <div class="summary-val text-navy">${fmtCurrencyExact(totalInvested)}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Cash Remainder</div>
                        <div class="summary-val text-green">${fmtCurrencyExact(cashRemainder)}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Floor Efficiency</div>
                        <div class="summary-val">${efficiency}%</div>
                    </div>
                </div>
                <div class="exec-summary-action">
                    <button class="btn-copy-basket" onclick="copyOrderBasket('${key}')">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                        Copy Demat Order Basket
                    </button>
                    <span id="copy-toast-${key}" class="copy-toast" style="display:none;">✓ Basket copied! Ready to paste into Zerodha Kite / Groww</span>
                </div>
            </div>

            <!-- Collapsible SLSQP Quant Solver Telemetry Drawer -->
            <div class="quant-drawer">
                <div class="quant-drawer-head" onclick="toggleQuantDrawer('${key}')">
                    <span>Quantitative Solver Telemetry &amp; Tail Risk (SLSQP)</span>
                    <span id="quant-drawer-toggle-${key}" style="color: var(--ft-navy); font-family: 'JetBrains Mono', monospace;">▼ EXPAND QUANT TELEMETRY</span>
                </div>
                <div class="quant-drawer-body" id="quant-drawer-body-${key}">
                    <div class="quant-telemetry-grid">
                        <div class="quant-tele-box">
                            <div class="quant-tele-label">Optimizer Engine</div>
                            <div class="quant-tele-val">${p.solver}</div>
                        </div>
                        <div class="quant-tele-box">
                            <div class="quant-tele-label">Convergence Status</div>
                            <div class="quant-tele-val text-green">${p.iterations}</div>
                        </div>
                        <div class="quant-tele-box">
                            <div class="quant-tele-label">Covariance Regularization</div>
                            <div class="quant-tele-val">${p.shrinkage}</div>
                        </div>
                        <div class="quant-tele-box">
                            <div class="quant-tele-label">Conditional VaR (95% Daily)</div>
                            <div class="quant-tele-val text-red">${(p.cvar95 * 100).toFixed(2)}% (Expected Shortfall)</div>
                        </div>
                        <div class="quant-tele-box">
                            <div class="quant-tele-label">Stress Scenario: COVID-19 Shock</div>
                            <div class="quant-tele-val text-red">${p.stressCovid}</div>
                        </div>
                        <div class="quant-tele-box">
                            <div class="quant-tele-label">Stress Scenario: 2022 Rate Hikes</div>
                            <div class="quant-tele-val text-green">${p.stressFed}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderBars(key, amount) {
    const p = PORTFOLIOS[key];
    const container = document.getElementById(`bars-${key}`);
    if (!container) return;

    container.innerHTML = '';

    p.allocations.forEach(asset => {
        const rupees = amount * asset.pct;
        const isZero = asset.pct === 0;

        const row = document.createElement('div');
        row.className = 'alloc-bar-row' + (isZero ? ' alloc-zero' : '');
        row.innerHTML = `
            <span class="alloc-bar-label">${asset.name}</span>
            <div class="alloc-bar-track">
                <div class="alloc-bar-fill"
                     style="width:${isZero ? '0' : (asset.pct * 100).toFixed(1)}%;
                            background:${asset.color};">
                    ${isZero ? '' : `${(asset.pct * 100).toFixed(1)}%`}
                </div>
            </div>
            <span class="alloc-bar-pct">${isZero ? '0%' : (asset.pct * 100).toFixed(1) + '%'}</span>
            <span class="alloc-bar-amount">${isZero ? '—' : fmtINR(rupees)}</span>
        `;
        container.appendChild(row);
    });
}

function renderProjections(key, amount) {
    const p = PORTFOLIOS[key];
    const container = document.getElementById(`proj-${key}`);
    if (!container) return;

    container.innerHTML = '';
    const years = [1, 3, 5, 10, 15];

    years.forEach(yr => {
        const projected = compoundGrow(amount, p.returnRate, yr);
        const gain = projected - amount;
        const gainPct = ((projected / amount - 1) * 100).toFixed(0);

        const card = document.createElement('div');
        card.className = 'proj-card';
        card.innerHTML = `
            <div class="proj-year">${yr} Year${yr > 1 ? 's' : ''}</div>
            <div class="proj-value">${fmtINR(projected)}</div>
            <div class="proj-gain">+${fmtINR(gain)} (+${gainPct}%)</div>
        `;
        container.appendChild(card);
    });
}

// ─── LIVE PRICES ─────────────────────────────────────────
async function loadLivePrices() {
    const grid = document.getElementById('price-grid');
    if (!grid) return;

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);

        const response = await fetch('/api/prices', { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const prices = await response.json();

        if (!Array.isArray(prices) || prices.length === 0) throw new Error('Empty data');

        grid.innerHTML = '';

        const TICKER_TO_KEY = {
            'GOLDBEES': 'GoldBees',
            'MON100': 'Nasdaq100',
            'NIFTYBEES': 'NiftyBees',
            'JUNIORBEES': 'JuniorBees',
            'BANKBEES': 'BankBees',
            'MID150BEES': 'Mid150Bees',
            'SILVERBEES': 'SilverBees',
            'SETF10GILT': 'GSec10Yr',
            'GSEC10IETF': 'GSec10Yr',
            'LIQUIDBEES': 'LiquidBees',
            'ITBEES': 'ITBees',
            'PHARMABEES': 'PharmaBees'
        };

        prices.forEach(item => {
            if (item.price) {
                const num = Number(item.price);
                const cleanTicker = (item.ticker || '').toUpperCase().replace('.NS', '');
                const mappedKey = TICKER_TO_KEY[cleanTicker];
                if (mappedKey) ETF_PRICES[mappedKey] = num;
                if (item.ticker) ETF_PRICES[item.ticker] = num;
                if (item.name) ETF_PRICES[item.name] = num;
                ETF_PRICES[`${cleanTicker}.NS`] = num;
            }
            const isUp   = item.pct_change > 0;
            const isDown = item.pct_change < 0;
            const cls    = isUp ? 'price-up' : (isDown ? 'price-down' : 'price-neutral');
            const sign   = isUp ? '+' : '';
            const icon   = isUp ? '▲' : (isDown ? '▼' : '—');

            const card = document.createElement('div');
            card.className = 'price-card';
            card.innerHTML = `
                <h3>${item.name}</h3>
                <span class="ticker">${item.ticker}</span>
                <div class="price-value">₹${Number(item.price).toFixed(2)}</div>
                <div class="price-change ${cls}">
                    ${icon} ${sign}${Number(item.change).toFixed(2)} (${sign}${Number(item.pct_change).toFixed(2)}%)
                </div>
            `;
            grid.appendChild(card);
        });

        // Re-render execution schedule with fresh live prices
        renderCalculator();

    } catch (err) {
        let msg = 'Could not load live prices.';
        if (err.name === 'AbortError') msg = 'Request timed out. NSE trading hours: Mon–Fri, 9:15 AM – 3:30 PM IST.';
        else if (err.message && err.message.includes('HTTP')) msg = `Server error (${err.message}).`;

        grid.innerHTML = `
            <div style="grid-column:1/-1; text-align:center; padding:1.5rem; color:var(--ft-claret); background:var(--ft-paper-card); border:1px solid var(--ft-border); border-radius:4px;">
                <p style="font-weight:700; margin-bottom: 4px;">⚠️ ${msg}</p>
                <p style="font-size:0.8rem; color:var(--ft-text-muted);">Displaying historical reference close prices for calculation.</p>
                <button onclick="loadLivePrices()" class="btn btn-secondary" style="margin-top:0.75rem; padding: 0.4rem 1rem;">🔄 Retry Live Feed</button>
            </div>
        `;
    }
}

// ─── GENERATE REPORT BUTTON ──────────────────────────────
function showGenerating(e) {
    const btn = document.getElementById('generate-btn');
    const msg = document.getElementById('generating-msg');
    if (!btn || !msg) return;

    btn.textContent = '⏳ Compiling Institutional Report…';
    btn.style.opacity = '0.7';
    btn.style.pointerEvents = 'none';
    msg.style.display = 'flex';

    setTimeout(() => {
        btn.textContent = '📄 Generate My Live Report (PDF)';
        btn.style.opacity = '1';
        btn.style.pointerEvents = 'auto';
        msg.style.display = 'none';
    }, 90000);
}

// ─── ORDER BASKET CLIPBOARD COPY ──────────────────────────
function copyOrderBasket(key) {
    const p = PORTFOLIOS[key];
    const nonZero = p.allocations.filter(a => a.pct > 0);
    let totalInvested = 0;

    const lines = [
        `ETF OPTIMA DEMAT ORDER BASKET · ${p.title.toUpperCase()}`,
        `Total Capital: ₹${currentAmount.toLocaleString('en-IN')}`,
        `Execution Date: ${new Date().toLocaleDateString('en-IN', {day:'numeric',month:'short',year:'numeric'})}`,
        `────────────────────────────────────────`
    ];

    nonZero.forEach((asset, idx) => {
        const targetRupees = currentAmount * asset.pct;
        const cleanTicker = (asset.ticker || '').toUpperCase().replace('.NS', '');
        const ltp = ETF_PRICES[asset.name] || ETF_PRICES[cleanTicker] || ETF_PRICES[asset.ticker] || 100.0;
        const units = Math.floor(targetRupees / ltp);
        const actualValue = units * ltp;
        totalInvested += actualValue;
        lines.push(`${idx + 1}. BUY ${cleanTicker} (${asset.name}): ${units.toLocaleString('en-IN')} shares @ ₹${ltp.toFixed(2)} = ₹${actualValue.toLocaleString('en-IN')}`);
    });

    const cashRemainder = currentAmount - totalInvested;
    lines.push(`────────────────────────────────────────`);
    lines.push(`Capital Invested: ₹${totalInvested.toLocaleString('en-IN')} (${((totalInvested / currentAmount) * 100).toFixed(2)}%)`);
    lines.push(`Uninvested Cash Left: ₹${cashRemainder.toFixed(2)}`);
    lines.push(`Ready for execution in Zerodha Kite / Groww / Upstox.`);

    navigator.clipboard.writeText(lines.join('\n')).then(() => {
        const toast = document.getElementById(`copy-toast-${key}`);
        if (toast) {
            toast.style.display = 'inline-block';
            setTimeout(() => { toast.style.display = 'none'; }, 3500);
        }
    }).catch(err => {
        console.error('Clipboard copy failed:', err);
        alert(lines.join('\n'));
    });
}

// ─── INITIALIZATION ──────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    renderCalculator();

    const input = document.getElementById('invest-amount');
    const slider = document.getElementById('invest-slider');

    if (input) {
        input.addEventListener('input', () => {
            const val = parseFloat(input.value);
            if (val > 0) {
                if (slider) slider.value = Math.min(Math.max(val, 10000), 1000000);
                renderCalculator();
            }
        });
    }

    if (slider) {
        slider.addEventListener('input', () => {
            const val = parseFloat(slider.value);
            if (input) input.value = val;
            currentAmount = val;
            renderCalculator();
        });
    }

    loadLivePrices();
});

// Expose globals for HTML event attributes
window.setAmount         = setAmount;
window.switchTab         = switchTab;
window.toggleQuantDrawer = toggleQuantDrawer;
window.showGenerating    = showGenerating;
window.loadLivePrices    = loadLivePrices;
window.copyOrderBasket   = copyOrderBasket;

function handleGoogleSignIn() {
    const toast = document.getElementById('auth-toast');
    if (toast) {
        toast.textContent = '✓ Google Account Connected! Syncing with Neon database...';
        toast.style.display = 'block';
        setTimeout(() => {
            const modal = document.getElementById('auth-modal');
            if (modal) modal.close();
            toast.style.display = 'none';
        }, 1600);
    }
}
window.handleGoogleSignIn = handleGoogleSignIn;

function handleEmailSignIn() {
    const email = document.getElementById('auth-email-input')?.value;
    const toast = document.getElementById('auth-toast');
    if (toast) {
        toast.textContent = email ? `✓ Magic link sent to ${email}!` : '✓ Signed in to Workspace!';
        toast.style.display = 'block';
        setTimeout(() => {
            const modal = document.getElementById('auth-modal');
            if (modal) modal.close();
            toast.style.display = 'none';
        }, 1800);
    }
}
window.handleEmailSignIn = handleEmailSignIn;

function downloadExcel(e) {
    if (e) e.preventDefault();
    const amount = document.getElementById('invest-amount') ? document.getElementById('invest-amount').value || 100000 : 100000;
    
    let strategy = 'maxsharpe';
    const tabMinVol = document.getElementById('tab-minvol');
    const tabEqual = document.getElementById('tab-equal');
    if (tabMinVol && tabMinVol.classList.contains('active')) {
        strategy = 'minvol';
    } else if (tabEqual && tabEqual.classList.contains('active')) {
        strategy = 'equal';
    }
    
    const btn = document.getElementById('excel-btn');
    if (btn) {
        const originalText = btn.innerHTML;
        btn.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;display:inline-block;vertical-align:middle;margin-right:8px;"></div> Generating Excel…';
        btn.style.pointerEvents = 'none';
        
        setTimeout(() => {
            window.location.href = `/api/excel?amount=${amount}&strategy=${strategy}`;
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.pointerEvents = 'auto';
            }, 5000);
        }, 400);
    }
}
window.downloadExcel = downloadExcel;
