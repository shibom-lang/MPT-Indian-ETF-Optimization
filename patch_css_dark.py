with open('web/style.css', 'r') as f:
    css = f.read()

# Make the glass cards solid instead of blurred
css = css.replace('backdrop-filter: blur(18px);', '')
css = css.replace('-webkit-backdrop-filter: blur(18px);', '')
css = css.replace('background: var(--bg-card);', 'background: var(--bg-card-solid);')

with open('web/style.css', 'w') as f:
    f.write(css)

with open('web/index.html', 'r') as f:
    html = f.read()
import re
html = re.sub(r'<div class="background-effects">.*?</div>', '', html, flags=re.DOTALL)
with open('web/index.html', 'w') as f:
    f.write(html)

with open('web/dashboard.html', 'r') as f:
    html = f.read()
html = re.sub(r'<div class="background-effects">.*?</div>', '', html, flags=re.DOTALL)
with open('web/dashboard.html', 'w') as f:
    f.write(html)
