import re

with open('web/index.html', 'r') as f:
    html = f.read()

# Fix counts
html = html.replace('5 NSE-listed', '8 NSE-listed')
html = html.replace('5 major', '8 major')
html = html.replace('5 NSE', '8 NSE')
html = html.replace('1,875 trading days', 'trading days')
html = html.replace('all 5 ETFs', 'all 8 ETFs')
html = html.replace('the 5 ETFs', 'the 8 ETFs')
html = html.replace('What Are These 5 ETFs?', 'What Are These 8 Asset Classes?')

# Update Sharpe ratios and metrics
html = html.replace('17.22%', '19.44%')
html = html.replace('12.08%', '13.02%')
html = html.replace('0.8626', '0.9631')
html = html.replace('86.26%', '96.31%')
html = html.replace('0.5672', '0.7300')
html = html.replace('56.72%', '73.00%')
html = html.replace('0.5930', '0.6512')
html = html.replace('59.30%', '65.12%')
html = html.replace('10.66%', '8.21%')
html = html.replace('6.51%', '5.20%')
html = html.replace('12.28%', '14.20%')
html = html.replace('9.66%', '11.50%')

# Add missing ETF cards
missing_cards = """
                    <div class="etf-card glass-card reveal">
                        <div class="etf-icon" style="background: linear-gradient(135deg,#00796B,#004D40)">M150</div>
                        <h3>Mid150Bees</h3>
                        <div class="etf-ticker">MID150BEES.NS</div>
                        <p>Tracks India's <strong>midcap segment</strong> — higher growth potential with slightly higher volatility.</p>
                        <div class="etf-tag tag-equity">Equity · Mid Cap</div>
                    </div>
                    <div class="etf-card glass-card reveal">
                        <div class="etf-icon" style="background: linear-gradient(135deg,#673AB7,#512DA8)">N100</div>
                        <h3>Nasdaq100</h3>
                        <div class="etf-ticker">MON100.NS</div>
                        <p>Tracks the <strong>US Tech sector</strong>, providing geographic diversification and USD currency hedging.</p>
                        <div class="etf-tag tag-equity">Equity · US Tech</div>
                    </div>
                    <div class="etf-card glass-card reveal">
                        <div class="etf-icon" style="background: linear-gradient(135deg,#9E9E9E,#757575)">SLV</div>
                        <h3>SilverBees</h3>
                        <div class="etf-ticker">SILVERBEES.NS</div>
                        <p>Tracks <strong>physical silver</strong>, acting as both an industrial commodity and precious metal diversifier.</p>
                        <div class="etf-tag tag-commodity">Commodity · Silver</div>
                    </div>
                    <div class="etf-card glass-card reveal">
                        <div class="etf-icon" style="background: linear-gradient(135deg,#E91E63,#C2185B)">GSEC</div>
                        <h3>GSec10Yr</h3>
                        <div class="etf-ticker">GSEC10IETF.NS</div>
                        <p>Tracks <strong>10-Year Sovereign Bonds</strong>, offering stable long-duration fixed income backed by the Indian Government.</p>
                        <div class="etf-tag tag-fixed">Fixed Income · Sovereign Bond</div>
                    </div>
"""
# Insert cards right before closing grid div
html = html.replace('</div>\n            </div>\n        </section>\n\n        <!-- ═══════════════════════════════════════════════════════ -->\n        <!-- REPORT SECTION', missing_cards + '                </div>\n            </div>\n        </section>\n\n        <!-- ═══════════════════════════════════════════════════════ -->\n        <!-- REPORT SECTION')


with open('web/index.html', 'w') as f:
    f.write(html)

print("index.html patched")
