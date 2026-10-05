import re
with open('web/dashboard.html', 'r') as f:
    html = f.read()

# REMOVE GLOWING ORBS
html = re.sub(r'<div class="background-effects">.*?</div>', '', html, flags=re.DOTALL)

with open('web/dashboard.html', 'w') as f:
    f.write(html)
