"""Generate one comparison shell per route from the homepage shell's markup and styles."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' "
           "fill='%23181818'/%3E%3Cpath d='M9 24V8h8a6 6 0 0 1 0 12H9' fill='none' stroke='white' stroke-width='3'/%3E%3C/svg%3E")
STYLE = re.search(r'<style>.*?</style>', open(os.path.join(ROOT, 'tools', 'shell-style.html')).read(), re.S).group(0)

ROUTES = [
    dict(dir='', title='Patronus — Original / Revised', label='Homepage comparison', live='https://patronus.ai/',
         original='original.html', revised='revised.html', original_title='Original homepage — snapshot of October 2, 2026',
         revised_title='Revised homepage',
         options=[('hero', 'Hero'), ('research', 'Research direction'), ('metrics', 'Metrics'), ('domains', 'Simulation domains'),
                  ('capabilities', 'Capabilities'), ('papers', 'Featured research'), ('footer', 'Footer')],
         order=['hero', 'research', 'world-model', 'metrics', 'domains', 'capabilities', 'papers', 'footer']),
    dict(dir='products/', title='Patronus Products — Original / Revised', label='Products comparison', live='https://patronus.ai/products',
         original='products-original.html', revised='products-revised.html', original_title='Original products page — snapshot of October 2, 2026',
         revised_title='Revised products page',
         options=[('hero', 'Hero'), ('step-1', '01 Training Tasks'), ('step-2', '02 Simulation Environments'),
                  ('step-3', '03 Research &amp; Validation'), ('cta', 'Let’s collaborate'), ('footer', 'Footer')],
         order=['hero', 'phases', 'steps', 'quote', 'cta', 'footer']),
    dict(dir='research/', title='Patronus Research — Original / Revised', label='Research comparison', live='https://patronus.ai/research',
         original='research-original.html', revised='research-revised.html', original_title='Original research page — snapshot of October 2, 2026',
         revised_title='Revised research page',
         options=[('hero', 'Hero'), ('papers', 'Featured research'), ('cta', 'Let’s collaborate'), ('footer', 'Footer')],
         order=['hero', 'who', 'foundational', 'papers', 'focus', 'updates', 'cta', 'footer']),
]

for r in ROUTES:
    base = '../' * r['dir'].count('/')
    options = ''.join(f'<option value="{k}">{v}</option>' for k, v in r['options'])
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{r['title']}</title>
<link rel="icon" href="{FAVICON}">
{STYLE}
</head>
<body>
<header class="toolbar">
 <div class="identity"><strong>Patronus</strong><span>{r['label']}</span></div>
 <div class="tabs" role="group" aria-label="Page version">
  <button type="button" data-version="original" aria-pressed="false">Original</button>
  <button type="button" data-version="revised" aria-pressed="true">Revised</button>
 </div>
 <div class="tools">
  <select aria-label="Jump to section" id="section">{options}</select>
  <a href="{r['live']}" target="_blank" rel="noopener noreferrer">Open live site</a>
 </div>
</header>
<main class="stage">
 <iframe id="original" class="hidden" src="{base}{r['original']}" title="{r['original_title']}" aria-hidden="true" tabindex="-1"></iframe>
 <iframe id="revised" src="{base}{r['revised']}" title="{r['revised_title']}"></iframe>
</main>
<script>window.COMPARE={json.dumps({'order': r['order']})};</script>
<script src="{base}compare-shell.js"></script>
</body>
</html>
'''
    os.makedirs(os.path.join(ROOT, r['dir']), exist_ok=True)
    open(os.path.join(ROOT, r['dir'], 'index.html'), 'w').write(html)
    print('wrote', r['dir'] + 'index.html')
