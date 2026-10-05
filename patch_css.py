with open('web/style.css', 'r') as f:
    css = f.read()

# Replace root variables
css = css.replace('--bg-dark: #0a0f1e;', '--bg-dark: #f8fafc;')
css = css.replace('--bg-card: rgba(20, 30, 55, 0.72);', '--bg-card: #ffffff;')
css = css.replace('--bg-card-solid: #0f172a;', '--bg-card-solid: #ffffff;')
css = css.replace('--text-primary: #f0f4ff;', '--text-primary: #0f172a;')
css = css.replace('--text-secondary: #8899bb;', '--text-secondary: #475569;')
css = css.replace('--border: rgba(255, 255, 255, 0.08);', '--border: #e2e8f0;')
css = css.replace('--border-hover: rgba(255, 255, 255, 0.25);', '--border-hover: #cbd5e1;')

# Fix backdrop filter
css = css.replace('backdrop-filter: blur(18px);', '')
css = css.replace('-webkit-backdrop-filter: blur(18px);', '')

# Fix premium card
css = css.replace('background: linear-gradient(170deg, rgba(25,37,60,0.95) 0%, rgba(20,30,55,0.7) 100%);', 'background: #ffffff; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);')
css = css.replace('border-color: rgba(251,191,36,0.25);', 'border-color: #fbbf24;')

with open('web/style.css', 'w') as f:
    f.write(css)
