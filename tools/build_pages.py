"""Derive the revised /products and /research pages and wire in-site navigation across all comparison pages."""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
read = lambda n: open(os.path.join(ROOT, n)).read()
def write(n, s): open(os.path.join(ROOT, n), 'w').write(s)

def element(s, start_pat):
    """(start, end) of the first element whose opening tag matches start_pat, balancing same-name tags."""
    m = re.search(start_pat, s)
    assert m, start_pat
    tag = re.match(r'<(\w+)', m.group(0)).group(1)
    depth, i = 0, m.start()
    for t in re.finditer(rf'<(/?){tag}\b[^>]*>', s[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return m.start(), m.start() + t.end()
    raise ValueError(start_pat)

def replace_element(s, start_pat, new):
    a, b = element(s, start_pat)
    return s[:a] + new + s[b:]

def replace_inner(s, start_pat, inner):
    a, b = element(s, start_pat)
    open_tag = re.match(r'<[^>]+>', s[a:b]).group(0)
    tag = re.match(r'<(\w+)', open_tag).group(1)
    return s[:a] + open_tag + inner + f'</{tag}>' + s[b:]

def once(s, old, new):
    assert s.count(old) == 1, (old[:80], s.count(old))
    return s.replace(old, new)

SECTIONS = [
    ('Training Tasks',
     'We develop tasks around observed model failures, grounded in real-world workflows and calibrated to the capabilities your team is training.',
     [('Task Context', 'Realistic objectives, constraints, and supporting evidence drawn from professional work'),
      ('Reference Solutions', 'Expert-validated outputs that establish what successful completion looks like'),
      ('Rubrics &amp; Graders', 'Task-specific criteria that assess outcomes and the behavior required to achieve them')],
     ('View sample task', None)),
    ('Simulation Environments',
     'We build simulated applications and workflows where agents can execute complex tasks, delivered to run within your training infrastructure.',
     [('Existing Environments', 'Ready-built environments spanning software development, computer use, and knowledge work'),
      ('Custom Environments', 'Applications, tools, and world states developed around your team’s training objectives'),
      ('Multi-App Workflows', 'Connected environments that require agents to maintain context and coordinate work across applications')],
     ('Explore environments', None)),
    ('Research &amp; Validation',
     'Our research connects a deep investigation of model failures with methods for scaling useful training data through world modeling and synthetic generation.',
     [('Failure Investigation', 'Studying where models fall short to identify meaningful targets for training'),
      ('Difficulty Calibration', 'Testing and refining tasks against target models to preserve useful learning signals'),
      ('Quality Validation', 'Checking task realism, reference solutions, and graders through expert review and automated testing')],
     ('Explore our research', 'research/')),
]

def products_revised():
    s = read('products-original.html')
    s = once(s, '<title>Patronus AI | Products — Original</title>', '<title>Patronus AI | Products — Revised</title>')
    arrow = re.search(r'<div class="rl-cta-icon w-embed"><svg.*?</svg></div>', s, re.S).group(0)

    def link(label, href, cls):
        if href:
            return f'<div class="product_section-link"><a class="{cls}" href="{href}" target="_top"><div>{label}</div>{arrow}</a></div>'
        # Placeholder until the destination exists: no href, so it cannot navigate or jump.
        return (f'<div class="product_section-link"><a class="{cls} is-inactive" aria-disabled="true" role="link">'
                f'<div>{label}</div>{arrow}</a></div>')

    # Site-wide announcement banner, removed from the approved revised homepage as well.
    s = replace_element(s, r'<div class="callout_banner">', '')
    # Hero
    s = once(s, '>Patronus AI Products</h1>', '>Frontier Training Data</h1>')
    s = once(s, '>Central to our product evolution is dynamism. Our industry landscape has evolved rapidly over the past few years, and so have we.</p>',
             '>We develop tasks and simulated environments for frontier labs, targeting model failures to improve capabilities through mid-training and reinforcement learning.</p>')
    # Phase/history section and its color-scrub script go entirely.
    s = replace_element(s, r'<div class="section_product-quote" data-compare-section="phases"', '')
    s = re.sub(r'<script>\s*gsap\.registerPlugin\(ScrollTrigger\);\s*gsap\.set\("#product-quote_1".*?</script>', '', s, flags=re.S)
    assert 'product-quote_1' not in s
    # Numbered sections, desktop and mobile copies.
    for n, (title, intro, blocks, (label, href)) in enumerate(SECTIONS, 1):
        heading = f'<div class="heading-style-h2 wow">0{n} </div><div class="heading-style-h2 wow">{title}</div>'
        s = replace_inner(s, rf'<div id="number_{n}" ', heading)
        s = replace_inner(s, rf'<div id="mobile-number_{n}" ', heading)
        desk = ''.join(f'<div class="step_child-insight"><div class="step_insight-child_text"><div class="text-size-24 text-weight-normal text-color-white">{t}</div>'
                       f'<p class="text-size-16">{d}</p></div></div>' for t, d in blocks)
        mob = ''.join(f'<div class="step_child-insight"><div class="step_insight-child_text"><div class="text-weight-normal text-color-white">{t}</div>'
                      f'<p class="text-size-14">{d}</p></div></div>' for t, d in blocks)
        s = replace_inner(s, rf'<div id="text_{n}" ',
                          f'<p class="heading-style-h4 wow text-color-white">{intro}</p><div class="steps_child-grid is-3_col">{desk}</div>'
                          + link(label, href, 'wowbutton explore w-inline-block'))
        s = replace_inner(s, rf'<div id="mobile-text_{n}" ',
                          f'<p class="text-size-24 text-weight-normal text-color-white">{intro}</p><div class="steps_child-grid is-3_col">{mob}</div>'
                          + link(label, href, 'wowbutton w-inline-block'))
    # Closing quotation and the stray duplicated attribution in the CTA.
    s = replace_element(s, r'<div class="section_product-quote2" data-compare-section="quote"', '')
    s = once(s, '<div class="footer_cta_author">- Tim Sweeney</div>', '')
    assert 'Tim Sweeney' not in s and 'Explore</div>' not in s
    s = once(s, '</head>', '<style>.product_section-link{display:flex}.wowbutton.is-inactive{opacity:.4;pointer-events:none;cursor:default}</style></head>')
    write('products-revised.html', s)
    return s

def research_revised(products):
    """Minimal landing page: approved research copy + the approved homepage Featured Research cards."""
    s = products.replace('<title>Patronus AI | Products — Revised</title>', '<title>Patronus AI | Research — Revised</title>')
    s = once(s, '>Frontier Training Data</h1>', '>Research</h1>')
    s = once(s, '>We develop tasks and simulated environments for frontier labs, targeting model failures to improve capabilities through mid-training and reinforcement learning.</p>',
             f'>{SECTIONS[2][1]}</p>')
    a, b = element(read('revised.html'), r'<div class="section_wowresearch" data-compare-section="papers"')
    papers = read('revised.html')[a:b]
    # The section's own "Research" button would link to this page; drop it.
    papers = re.sub(r'<a class="wowbutton w-button" href="https://patronus.ai/research"[^>]*>Research</a>', '', papers, count=1)
    s = replace_element(s, r'<div class="section_product-steps" data-compare-section="steps"', papers)
    # Products is not the current page here. (The sticky products script returns early without its elements.)
    s, n = re.subn(r'( aria-current="page")?( class="navbar12_dropdown-toggle) w--current"', r'\2"', s)
    assert n == 1
    write('research-revised.html', s)

def wire_navigation():
    """Logo, Products and Research Hub stay inside the comparison site; everything else is unchanged."""
    routes = [('navbar12_logo-link', 'https://patronus.ai/', './'),
              ('navbar12_dropdown-toggle', 'https://patronus.ai/products', 'products/'),
              ('navbar12_dropdown-link', 'https://patronus.ai/research', 'research/')]
    for name in ['original.html', 'revised.html', 'products-original.html', 'products-revised.html',
                 'research-original.html', 'research-revised.html']:
        s = read(name)
        counts = []
        for cls, live, local in routes:
            def sub(m):
                tag = m.group(0)
                if f'href="{live}"' not in tag or not re.search(rf'class="{cls}[ "]', tag):
                    return tag
                tag = re.sub(r'\s(rel|target)="[^"]*"', '', tag)
                return tag.replace(f'href="{live}"', f'href="{local}"')[:-1] + ' target="_top">'
            s, n = re.subn(r'<a\b[^>]*>', sub, s)
            counts.append(sum(1 for _ in re.finditer(rf'href="{re.escape(local)}" ', s)))
        print(name, dict(zip(['home', 'products', 'research'], counts)))
        write(name, s)

if __name__ == '__main__':
    research_revised(products_revised())
    wire_navigation()
