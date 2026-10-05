import re
with open('web/index.html', 'r') as f:
    html = f.read()

eq_new = """                            <div class="alloc-row">
                                <div class="alloc-info"><span class="dot" style="background:#60a5fa"></span>All 9 Assets</div>
                                <div class="alloc-right"><div class="mini-bar"><div class="mini-fill" style="width:11.1%; background:#60a5fa"></div></div><span>11.1% each</span></div>
                            </div>"""

html = re.sub(r'<h4>Allocation Breakdown</h4>.*?</div>\s*<div class="card-insight insight-warn">', 
              r'<h4>Allocation Breakdown</h4>\n' + eq_new + r'\n</div>\n<div class="card-insight insight-warn">', html, count=1, flags=re.DOTALL)

with open('web/index.html', 'w') as f:
    f.write(html)
