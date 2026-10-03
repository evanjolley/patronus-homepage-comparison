"""Snapshot a live patronus.ai page into pages/ using the homepage snapshot conventions:
assets localized as assets/<sha256(url)[:16]>.<ext>, analytics/tracking removed,
local fonts, anchors absolute to patronus.ai opening in a new tab."""
import hashlib, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
LOCAL_HOSTS = r'(?:https://cdn\.prod\.website-files\.com|https://d3e54v103j8qbb\.cloudfront\.net|https://unpkg\.com|https://cdn\.jsdelivr\.net/npm/swiper)'
EXT_BY_TYPE = {'image/svg+xml': '.svg', 'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp',
               'image/avif': '.avif', 'image/gif': '.gif', 'text/css': '.css', 'image/x-icon': '.ico',
               'application/javascript': '.js', 'text/javascript': '.js', 'font/woff2': '.woff2', 'font/ttf': '.ttf'}
KNOWN_EXT = set(EXT_BY_TYPE.values()) | {'.jpeg', '.ico', '.woff', '.otf', '.mp4', '.webm', '.json'}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get('Content-Type', '').split(';')[0].strip()

def localize(url):
    raw = url.replace('&amp;', '&')
    h = hashlib.sha256(raw.encode()).hexdigest()[:16]
    for name in os.listdir(ASSETS):
        if name.startswith(h + '.'):
            return 'assets/' + name
    data, ctype = fetch(raw)
    ext = os.path.splitext(urllib.parse.urlparse(raw).path)[1].lower()
    if ext not in KNOWN_EXT:
        ext = EXT_BY_TYPE.get(ctype, '.bin')
    if ext == '.css' and re.search(rb'url\(', data):
        sys.exit(f'new stylesheet with url() references needs manual handling: {raw}')
    open(os.path.join(ASSETS, h + ext), 'wb').write(data)
    return 'assets/' + h + ext

DROP_SCRIPT = [r'webfont\.js', r'WebFont\.load', r'google_tags_first_party', r'src="/g0ln', r"gtag\('js'",
               r'googletagmanager', r'waitForElm', r'reb2b', r'npm/gsap@', r'@finsweet/attributes', r'pm7lmv89',
               r'getkoala', r'const softlinks', r'blockedDomains']

def snapshot(url, out, title, sections):
    s, _ = fetch(url)
    s = s.decode()
    def drop(m):
        return '' if any(re.search(p, m.group(0)) for p in DROP_SCRIPT) else m.group(0)
    s = re.sub(r'<script\b[^>]*>.*?</script>', drop, s, flags=re.S)
    s = re.sub(r'<noscript>.*?</noscript>', '', s, flags=re.S)
    s = re.sub(r'<link[^>]*rel="prefetch"[^>]*>', '', s)
    s = re.sub(r'\s(integrity)="[^"]*"', '', s)
    s = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', s)
    # Same font + Swiper stylesheet lines the homepage snapshot uses in place of Google WebFont loader.
    s = s.replace('</head>', '<link href="assets/0dffe3fe2f73e29e.css" rel="stylesheet"/>'
                  '<link href="assets/49c2efef81e36e43.bin" rel="stylesheet"/></head>', 1)
    shared_css = 'https://cdn.prod.website-files.com/64e655d42d3be60f582d0472/css/patronus-ai.webflow.shared.3e3711ce2.min.css'
    s = s.replace(shared_css, 'assets/222bc9fccec14bd2.css?v=2')
    # Localize asset references (not anchors, not lottie data-src: same as homepage snapshot).
    s = re.sub(r'(<(?:img|script|source|video|link)\b[^>]*?\s(?:src|href|poster)=")(' + LOCAL_HOSTS + r'[^"]+)"',
               lambda m: m.group(1) + localize(m.group(2)) + '"', s)
    s = re.sub(r'srcset="([^"]+)"', lambda m: 'srcset="' + re.sub(LOCAL_HOSTS + r'\S+', lambda u: localize(u.group(0)), m.group(1)) + '"', s)
    s = re.sub(r'url\((["\']?)(' + LOCAL_HOSTS + r'[^"\')]+)\1\)', lambda m: 'url(' + m.group(1) + localize(m.group(2)) + m.group(1) + ')', s)
    # Anchors open the real destination in a new tab.
    def anchor(m):
        tag = m.group(0)
        href = re.search(r'href="([^"]*)"', tag)
        if not href or not re.match(r'(https?:|/)', href.group(1)):
            return tag
        dest = href.group(1)
        if dest.startswith('/'):
            dest = 'https://patronus.ai' + dest
        tag = re.sub(r'\s(target|rel)="[^"]*"', '', tag)
        return tag.replace(href.group(0), f'href="{dest}"', 1)[:-1] + ' rel="noopener noreferrer" target="_blank">'
    s = re.sub(r'<a\b[^>]*>', anchor, s)
    for cls, key in sections:
        n = s.count(f'class="{cls}"')
        assert n == 1, (cls, n)
        s = s.replace(f'class="{cls}"', f'class="{cls}" data-compare-section="{key}"', 1)
    s = s.replace('</body>', '<script src="preview-runtime.js"></script></body>', 1)
    leftover = re.findall(r'<(?:img|script|link)\b[^>]*(?:src|href)="(https?://[^"]+)"', s)
    print(out, 'remaining external asset refs:', [u for u in leftover if 'fonts.g' not in u and 'website-files.com"' not in u])
    open(os.path.join(ROOT, out), 'w').write(s)

if __name__ == '__main__':
    snapshot('https://patronus.ai/products', 'products-original.html', 'Patronus AI | Products — Original',
             [('section_product-hero', 'hero'), ('section_product-quote', 'phases'), ('section_product-steps', 'steps'),
              ('section_product-quote2', 'quote'), ('section_footer_collaborate', 'cta'), ('section_footer', 'footer')])
    snapshot('https://patronus.ai/research', 'research-original.html', 'Patronus AI | Research — Original',
             [('section_research-hero', 'hero'), ('section_research-who', 'who'), ('section_research-foundational', 'foundational'),
              ('section_research-work', 'papers'), ('section_research-focus', 'focus'), ('section_research-updates', 'updates'),
              ('section_footer_collaborate', 'cta'), ('section_footer', 'footer')])
