/* ─────────────────────────────────────────────────────────
   ETF Optima — Main JavaScript
   Handles: live prices, reveal animations, investment calculator
   ───────────────────────────────────────────────────────── */

// ─── PORTFOLIO DATA ───────────────────────────────────────
const PORTFOLIOS = {
    maxsharpe: {
        returnRate: 0.1722,
        vol: 0.1208,
        sharpe: 0.8626,
        allocations: [
            { name: 'GoldBees',     pct: 0.450, color: '#fbbf24' },
            { name: 'JuniorBees',   pct: 0.334, color: '#ef4444' },
            { name: 'NiftyBees',    pct: 0.216, color: '#60a5fa' },
            { name: 'BankBees',     pct: 0.000, color: '#f59e0b' },
            { name: 'LiquidBees',   pct: 0.000, color: '#a78bfa' },
        ],
    },
    minvol: {
        returnRate: 0.1066,
        vol: 0.0651,
        sharpe: 0.5930,
        allocations: [
            { name: 'LiquidBees',   pct: 0.450, color: '#a78bfa' },
            { name: 'GoldBees',     pct: 0.421, color: '#fbbf24' },
            { name: 'NiftyBees',    pct: 0.129, color: '#60a5fa' },
            { name: 'BankBees',     pct: 0.000, color: '#f59e0b' },
            { name: 'JuniorBees',   pct: 0.000, color: '#ef4444' },
        ],
    },
    equal: {
        returnRate: 0.1228,
        vol: 0.0966,
        sharpe: 0.5672,
        allocations: [
            { name: 'NiftyBees',    pct: 0.20, color: '#60a5fa' },
            { name: 'JuniorBees',   pct: 0.20, color: '#ef4444' },
            { name: 'BankBees',     pct: 0.20, color: '#f59e0b' },
            { name: 'GoldBees',     pct: 0.20, color: '#fbbf24' },
            { name: 'LiquidBees',   pct: 0.20, color: '#a78bfa' },
        ],
    },
};

let currentTab = 'maxsharpe';
let currentAmount = 100000;

// ─── FORMATTER HELPERS ───────────────────────────────────
function fmtINR(amount) {
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)} Cr`;
    if (amount >= 100000)   return `₹${(amount / 100000).toFixed(2)} L`;
    if (amount >= 1000)     return `₹${(amount / 1000).toFixed(1)}K`;
    return `₹${amount.toFixed(0)}`;
}

function compoundGrow(principal, rate, years) {
    return principal * Math.pow(1 + rate, years);
}

// ─── CALCULATOR ──────────────────────────────────────────
function setAmount(val) {
    document.getElementById('invest-amount').value = val;
    currentAmount = val;
    renderCalculator();
}

function switchTab(tab) {
    currentTab = tab;
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');
    // Update panels
    document.querySelectorAll('.alloc-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`alloc-${tab}`).classList.add('active');
    renderCalculator();
}

function renderCalculator() {
    const amount = parseFloat(document.getElementById('invest-amount').value) || 0;
    currentAmount = amount;

    Object.keys(PORTFOLIOS).forEach(key => {
        renderBars(key, amount);
        renderProjections(key, amount);
    });
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
                            background:linear-gradient(90deg, ${asset.color}cc, ${asset.color});">
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
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout

        const response = await fetch('/api/prices', { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const prices = await response.json();

        if (!Array.isArray(prices) || prices.length === 0) throw new Error('Empty data');

        grid.innerHTML = '';

        prices.forEach(item => {
            const isUp   = item.pct_change > 0;
            const isDown = item.pct_change < 0;
            const cls    = isUp ? 'price-up' : (isDown ? 'price-down' : 'price-neutral');
            const sign   = isUp ? '+' : '';
            const icon   = isUp ? '▲' : (isDown ? '▼' : '—');

            const card = document.createElement('div');
            card.className = 'glass-card price-card reveal';
            card.innerHTML = `
                <h3>${item.name}</h3>
                <span class="ticker">${item.ticker}</span>
                <div class="price-value">₹${Number(item.price).toFixed(2)}</div>
                <div class="price-change ${cls}">
                    ${icon} ${sign}${Number(item.change).toFixed(2)} (${sign}${Number(item.pct_change).toFixed(2)}%)
                </div>
            `;
            grid.appendChild(card);
            // Trigger reveal
            requestAnimationFrame(() => {
                setTimeout(() => card.classList.add('visible'), 50);
            });
        });

    } catch (err) {
        // Determine error message
        let msg = 'Could not load live prices.';
        if (err.name === 'AbortError') msg = 'Request timed out. Market may be closed or API is busy.';
        else if (err.message.includes('HTTP')) msg = `Server error (${err.message}). Please try again.`;

        grid.innerHTML = `
            <div style="grid-column:1/-1; text-align:center; padding:2rem; color:#ef4444;">
                <div style="font-size:2rem; margin-bottom:0.5rem;">⚠️</div>
                <p style="margin-bottom:0.5rem; font-weight:600;">${msg}</p>
                <p style="font-size:0.82rem; color:#8899bb;">Live prices require the market to be open. NSE trading hours: Mon–Fri, 9:15 AM – 3:30 PM IST.</p>
                <button onclick="loadLivePrices()" style="margin-top:1rem; padding:0.5rem 1.25rem; background:#3b82f6; color:white; border:none; border-radius:6px; cursor:pointer; font-weight:600;">🔄 Retry</button>
            </div>
        `;
    }
}

// ─── GENERATE REPORT BUTTON ──────────────────────────────
function showGenerating(e) {
    const btn = document.getElementById('generate-btn');
    const msg = document.getElementById('generating-msg');
    if (!btn || !msg) return;

    btn.textContent = '⏳ Opening report…';
    btn.style.opacity = '0.7';
    btn.style.pointerEvents = 'none';
    msg.style.display = 'flex';

    // Re-enable after 90s (report generation timeout)
    setTimeout(() => {
        btn.textContent = '🚀 Generate My Live Report (PDF)';
        btn.style.opacity = '1';
        btn.style.pointerEvents = 'auto';
        msg.style.display = 'none';
    }, 90000);
}

// ─── REVEAL ON SCROLL ────────────────────────────────────
function setupReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08 });

    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}

// ─── AMOUNT INPUT LISTENER ───────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Initial calculator render
    renderCalculator();

    // Live update on typing
    const input = document.getElementById('invest-amount');
    if (input) {
        input.addEventListener('input', () => {
            const val = parseFloat(input.value);
            if (val > 0) renderCalculator();
        });
    }

    // Load live prices
    loadLivePrices();

    // Set up scroll reveal
    setupReveal();
});

// ─── EXPOSE GLOBALS FOR onclick ATTRIBUTES ───────────────
// type="module" scopes functions — must attach to window
// for HTML onclick="..." attributes to find them
window.setAmount      = setAmount;
window.switchTab      = switchTab;
window.showGenerating = showGenerating;
