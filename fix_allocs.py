with open('web/index.html', 'r') as f:
    html = f.read()

# Max Sharpe
ms_old = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-gold"></span>GoldBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:45%; background:#fbbf24"></div></div><span>45.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-red"></span>JuniorBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:33.4%; background:#ef4444"></div></div><span>33.4%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-blue"></span>NiftyBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:21.6%; background:#60a5fa"></div></div><span>21.6%</span></div>
                            </div>
                            <div class="alloc-row zero-weight">
                                <div class="alloc-info"><span class="dot dot-dim"></span>BankBees</div>
                                <div class="alloc-right"><span class="zero-tag">0% — Excluded</span></div>
                            </div>
                            <div class="alloc-row zero-weight">
                                <div class="alloc-info"><span class="dot dot-dim"></span>LiquidBees</div>
                                <div class="alloc-right"><span class="zero-tag">0% — Excluded</span></div>
                            </div>"""

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
mv_old = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-purple"></span>LiquidBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:45%; background:#a78bfa"></div></div><span>45.0%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-gold"></span>GoldBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:42.1%; background:#fbbf24"></div></div><span>42.1%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-blue"></span>NiftyBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:12.9%; background:#60a5fa"></div></div><span>12.9%</span></div>
                            </div>
                            <div class="alloc-row zero-weight">
                                <div class="alloc-info"><span class="dot dot-dim"></span>BankBees</div>
                                <div class="alloc-right"><span class="zero-tag">~0% — Excluded</span></div>
                            </div>
                            <div class="alloc-row zero-weight">
                                <div class="alloc-info"><span class="dot dot-dim"></span>JuniorBees</div>
                                <div class="alloc-right"><span class="zero-tag">~0% — Excluded</span></div>
                            </div>"""

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
eq_old = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-blue"></span>NiftyBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:20%; background:#60a5fa"></div></div><span>20%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-red"></span>JuniorBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:20%; background:#ef4444"></div></div><span>20%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-orange"></span>BankBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:20%; background:#f59e0b"></div></div><span>20%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-gold"></span>GoldBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:20%; background:#fbbf24"></div></div><span>20%</span></div>
                            </div>
                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-purple"></span>LiquidBees</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:20%; background:#a78bfa"></div></div><span>20%</span></div>
                            </div>"""

eq_new = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot dot-blue"></span>All 9 Assets</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:11.1%; background:#60a5fa"></div></div><span>11.1% each</span></div>
                            </div>"""

html = html.replace(ms_old, ms_new)
html = html.replace(mv_old, mv_new)
html = html.replace(eq_old, eq_new)

html = html.replace('GSEC10IETF.NS', 'SETF10GILT.NS')
html = html.replace('GSEC10IETF', 'SETF10GILT')
html = html.replace('means 40%', 'means 22.2%')

# We need to change "8 ETFs" in the header to "9 ETFs"
html = html.replace('<h2>🏦 What Are These 8 ETFs?</h2>', '<h2>🏦 What Are These 9 ETFs?</h2>')

with open('web/index.html', 'w') as f:
    f.write(html)
