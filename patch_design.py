import re
import json

with open('web/index.html', 'r') as f:
    html = f.read()

# 1. REMOVE GLOWING ORBS
html = re.sub(r'<div class="background-effects">.*?</div>', '', html, flags=re.DOTALL)

# 2. REPLACE PORTFOLIO CARDS
# Max Sharpe
ms_new = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#fbbf24"></span>GoldBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:25%; background:#fbbf24"></div></div><span>25.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#14b8a6"></span>Mid150Bees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:25%; background:#14b8a6"></div></div><span>25.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#8b5cf6"></span>Nasdaq100</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:25%; background:#8b5cf6"></div></div><span>25.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#ef4444"></span>JuniorBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:15%; background:#ef4444"></div></div><span>15.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#60a5fa"></span>NiftyBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:10%; background:#60a5fa"></div></div><span>10.0%</span></div>
                            </div>
                            <div class="alloc-row zero-weight">
                                <div class="alloc-info"><span class="dot dot-dim"></span>Others (4)</div>
                                <div class="alloc-right"><span class="zero-tag">0% — Excluded</span></div>
                            </div>"""

# Min Volatility
mv_new = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#a78bfa"></span>LiquidBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:45%; background:#a78bfa"></div></div><span>45.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#ec4899"></span>GSec10Yr</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:30%; background:#ec4899"></div></div><span>30.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#fbbf24"></span>GoldBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:15%; background:#fbbf24"></div></div><span>15.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#60a5fa"></span>NiftyBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:10%; background:#60a5fa"></div></div><span>10.0%</span></div>
                            </div>
                            <div class="alloc-row zero-weight">
                                <div class="alloc-info"><span class="dot dot-dim"></span>Others (5)</div>
                                <div class="alloc-right"><span class="zero-tag">0% — Excluded</span></div>
                            </div>"""

# Equal Weight
eq_new = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#60a5fa"></span>All 9 Assets</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:11.1%; background:#60a5fa"></div></div><span>11.1% each</span></div>
                            </div>"""

def replace_alloc(html, header_text, new_alloc):
    # Find the block starting with header_text and replace the contents of <div class="alloc-row">...</div> inside it
    pattern = re.compile(rf'(<h3>{header_text}</h3>.*?</style>\s*</div>\s*</div>)', re.DOTALL)
    # wait, the insight cards are below it. Let's just do regex on the allocation block
    pattern = re.compile(rf'(<h3>{header_text}</h3>.*?<h4>Allocation Breakdown</h4>\s*<div class="alloc-row">).*?(</div>\s*<div class="card-insight">)', re.DOTALL)
    return html

# We will just replace it by string matching the whole block for safety
# Actually regex is easier if I do it cleanly:
html = re.sub(r'<h4>Allocation Breakdown</h4>.*?</div>\s*<div class="card-insight">', 
              r'<h4>Allocation Breakdown</h4>\n{{MS}}\n</div>\n<div class="card-insight">', html, count=1, flags=re.DOTALL)
html = html.replace('{{MS}}', ms_new)

html = re.sub(r'<h4>Allocation Breakdown</h4>.*?</div>\s*<div class="card-insight">', 
              r'<h4>Allocation Breakdown</h4>\n{{MV}}\n</div>\n<div class="card-insight">', html, count=1, flags=re.DOTALL)
html = html.replace('{{MV}}', mv_new)

html = re.sub(r'<h4>Allocation Breakdown</h4>.*?</div>\s*<div class="card-insight">', 
              r'<h4>Allocation Breakdown</h4>\n{{EQ}}\n</div>\n<div class="card-insight">', html, count=1, flags=re.DOTALL)
html = html.replace('{{EQ}}', eq_new)

with open('web/index.html', 'w') as f:
    f.write(html)
