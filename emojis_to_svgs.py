import re

with open('web/index.html', 'r') as f:
    html = f.read()

# ✅ Checkmark (Heroicons solid check-circle, green)
check_svg = '<svg class="svg-icon" style="color: #34d399; margin-right: 8px;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>'
html = html.replace('✅ ', check_svg)

# 🚀 Rocket -> Document arrow down (Heroicons outline document-arrow-down)
doc_svg = '<svg class="btn-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>'
html = html.replace('🚀 ', doc_svg)

# ⭐ Star
star_svg = '<svg class="svg-icon" style="color: #fbbf24; margin-right: 8px;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>'
html = html.replace('⭐ ', star_svg)

# 🛡️ Shield
shield_svg = '<svg class="svg-icon" style="color: #ef4444; margin-right: 8px;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clip-rule="evenodd" /></svg>'
html = html.replace('🛡️ ', shield_svg)

# ⚖️ Scales
scales_svg = '<svg class="svg-icon" style="color: #60a5fa; margin-right: 8px;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" /></svg>'
html = html.replace('⚖️ ', scales_svg)

# 🏦 Bank (Building)
bank_svg = '<svg class="svg-icon" style="color: #f0f4ff; margin-right: 8px; width: 1.5rem; height: 1.5rem;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1v1H9V7zm5 0h1v1h-1V7zm-5 4h1v1H9v-1zm5 0h1v1h-1v-1zm-5 4h1v1H9v-1zm5 0h1v1h-1v-1z" /></svg>'
html = html.replace('🏦 ', bank_svg)

# 🏆 Trophy
trophy_svg = '<svg class="svg-icon" style="color: #fbbf24; margin-left: 4px;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 3v4M3 5h4M21 5h-4M19 3v4m-5 9h-4m4 0v4m0-4v-4m0 0A7 7 0 015 9V5h14v4a7 7 0 01-7 7z" /></svg>'
html = html.replace(' 🏆', trophy_svg)
html = html.replace('🏆 ', trophy_svg)

# 💡 Lightbulb
bulb_svg = '<svg class="svg-icon" style="color: #fbbf24; margin-right: 8px;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>'
html = html.replace('💡 ', bulb_svg)

# ⚠️ Warning
warn_svg = '<svg class="svg-icon" style="color: #f59e0b; margin-right: 8px;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>'
html = html.replace('⚠️ ', warn_svg)

# Just in case some have no space after
html = html.replace('✅', check_svg)
html = html.replace('🚀', doc_svg)
html = html.replace('⭐', star_svg)
html = html.replace('🛡️', shield_svg)
html = html.replace('⚖️', scales_svg)
html = html.replace('🏦', bank_svg)
html = html.replace('💡', bulb_svg)
html = html.replace('⚠️', warn_svg)


with open('web/index.html', 'w') as f:
    f.write(html)
