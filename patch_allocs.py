import re
with open('web/index.html', 'r') as f:
    html = f.read()

# Max Sharpe
ms_new = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-gold"></span>GoldBees</div>
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
                                <div class="alloc-info"><span class="dot dot-red"></span>JuniorBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:15%; background:#ef4444"></div></div><span>15.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-blue"></span>NiftyBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:10%; background:#60a5fa"></div></div><span>10.0%</span></div>
                            </div>
                            <div class="alloc-row zero-weight">
                                <div class="alloc-info"><span class="dot dot-dim"></span>Others (4)</div>
                                <div class="alloc-right"><span class="zero-tag">0% — Excluded</span></div>
                            </div>"""

# Min Volatility
mv_new = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-purple"></span>LiquidBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:45%; background:#a78bfa"></div></div><span>45.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#ec4899"></span>SETF10GILT</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:30%; background:#ec4899"></div></div><span>30.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-gold"></span>GoldBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:15%; background:#fbbf24"></div></div><span>15.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-blue"></span>NiftyBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:10%; background:#60a5fa"></div></div><span>10.0%</span></div>
                            </div>
                            <div class="alloc-row zero-weight">
                                <div class="alloc-info"><span class="dot dot-dim"></span>Others (5)</div>
                                <div class="alloc-right"><span class="zero-tag">0% — Excluded</span></div>
                            </div>"""

# Equal Weight
eq_new = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-blue"></span>All 9 Assets</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:11.1%; background:#60a5fa"></div></div><span>11.1% each</span></div>
                            </div>"""

html = re.sub(r'<h4>Allocation Breakdown</h4>.*?</div>\s*<div class="card-insight">', 
              r'<h4>Allocation Breakdown</h4>\n{{MS}}\n</div>\n<div class="card-insight">', html, count=1, flags=re.DOTALL)
html = html.replace('{{MS}}', ms_new)

html = re.sub(r'<h4>Allocation Breakdown</h4>.*?</div>\s*<div class="card-insight">', 
              r'<h4>Allocation Breakdown</h4>\n{{MV}}\n</div>\n<div class="card-insight">', html, count=1, flags=re.DOTALL)
html = html.replace('{{MV}}', mv_new)

html = re.sub(r'<h4>Allocation Breakdown</h4>.*?</div>\s*<div class="card-insight insight-warn">', 
              r'<h4>Allocation Breakdown</h4>\n{{EQ}}\n</div>\n<div class="card-insight insight-warn">', html, count=1, flags=re.DOTALL)
html = html.replace('{{EQ}}', eq_new)

html = html.replace('GSEC10IETF', 'SETF10GILT')
html = html.replace('means 40%', 'means 22.2%')

with open('web/index.html', 'w') as f:
    f.write(html)
