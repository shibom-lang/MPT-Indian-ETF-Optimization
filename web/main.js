// Add simple reveal animation on scroll
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.glass-card');
    
    // Initial state
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => observer.observe(card));
});

// Fetch and render live prices
async function loadLivePrices() {
    const grid = document.getElementById('price-grid');
    if (!grid) return;

    try {
        const response = await fetch('/api/prices');
        if (!response.ok) throw new Error('Failed to fetch prices');
        const prices = await response.json();
        
        grid.innerHTML = ''; // Clear loading text
        
        prices.forEach(item => {
            const isUp = item.change > 0;
            const isDown = item.change < 0;
            const colorClass = isUp ? 'price-up' : (isDown ? 'price-down' : 'price-neutral');
            const sign = isUp ? '+' : '';
            const icon = isUp ? '📈' : (isDown ? '📉' : '➖');
            
            grid.innerHTML += `
                <div class="glass-card price-card">
                    <h3>${item.name}</h3>
                    <span class="ticker">${item.ticker}</span>
                    <div class="price-value">₹${item.price.toFixed(2)}</div>
                    <div class="price-change ${colorClass}">
                        ${sign}${item.change.toFixed(2)} (${sign}${item.pct_change.toFixed(2)}%) ${icon}
                    </div>
                </div>
            `;
        });
        
        // Re-run observer for new cards
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('.price-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            observer.observe(card);
        });
        
    } catch (error) {
        grid.innerHTML = `<p class="text-center" style="color: #ef4444;">Could not load live data. Please try again later.</p>`;
        console.error(error);
    }
}

document.addEventListener('DOMContentLoaded', loadLivePrices);
