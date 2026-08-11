from pathlib import Path
import html
import shutil
from datetime import datetime

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

D = {
    p.stem: yaml.safe_load(p.read_text(encoding='utf-8'))
    for p in (ROOT / 'data').glob('*.yml')
}

s = D['site']
r = D['research']
pubs = D['publications']
projs = D['projects']
news = D['news']
SHORT_NAME = s.get('short_name', 'SOL')


def esc(value):
    return html.escape(str(value))


def href(value):
    return html.escape(str(value), quote=True)


# Publications validation
for p in pubs:
    if not p.get('image'):
        raise SystemExit(f"Publication image is required: {p.get('title')}")
    try:
        p['year'] = int(p['year'])
    except (TypeError, ValueError, KeyError):
        raise SystemExit(
            f"Publication year must be a 4-digit number: {p.get('title')}"
        )

PUBLICATION_YEARS = sorted({p['year'] for p in pubs}, reverse=True)
CSS = (ROOT / 'assets' / 'style.css').read_text(encoding='utf-8')


def img(path, alt=''):
    return f'<img src="{href(path)}" alt="{href(alt)}">'


def head(title, active=''):
    links = [
        ('Home', 'index.html'),
        ('People', 'people.html'),
        ('Research', 'research.html'),
        ('Publications', 'publications.html'),
        ('Achievements', 'achievements.html'),
        ('News', 'news.html'),
        ('Join Us', 'join.html'),
    ]
    nav = ''.join(
        f'<a class="{"active" if n == active else ""}" href="{u}">{n}</a>'
        for n, u in links
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · {esc(SHORT_NAME)}</title><style>{CSS}</style></head><body><header class="site-header"><div class="header"><a class="brand" href="index.html">{esc(SHORT_NAME)}</a><nav class="nav">{nav}</nav></div></header>'''


def foot():
    return f'''<footer class="footer"><div class="footer-inner"><strong>{esc(SHORT_NAME)}</strong>{esc(s['lab_name'])} · {esc(s['department'])} · {esc(s['university'])} ({esc(s['campus'])})</div></footer></body></html>'''


def pagehero(title, text):
    return f'''<section class="page-hero"><div class="page-hero-inner"><div class="eyebrow">{esc(SHORT_NAME)} · Yonsei University</div><h1>{esc(title)}</h1><p>{esc(text)}</p></div></section>'''


def parse_news_date(value):
    text = str(value).strip()
    for fmt in ('%Y.%m.%d', '%Y-%m-%d', '%Y/%m/%d'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise SystemExit(
        f'News date must be YYYY.MM.DD, YYYY-MM-DD, or YYYY/MM/DD: {text}'
    )


for n in news:
    if not n.get('title') or not n.get('category') or not n.get('date'):
        raise SystemExit(f'News requires date, category, and title: {n}')
    n['_date_obj'] = parse_news_date(n['date'])

news_sorted = sorted(news, key=lambda n: n['_date_obj'], reverse=True)


# Highlights
hl = []
for p in pubs:
    if p.get('highlight'):
        hl.append(('Publication', p['title'], p['journal'], p['image']))
for p in projs:
    if p.get('highlight'):
        hl.append(('Research Project', p['title'], p['agency'], None))


# --------------------------------------------------
# Home
# --------------------------------------------------

h = head('Home', 'Home') + f'''<section class="hero"><div class="hero-inner"><div><div class="eyebrow">{esc(s['university'])}<br>{esc(s['department'])}</div><h1>{esc(s['hero_title'])}</h1><div class="ko">{esc(s['lab_name'])}</div><div class="ko">{esc(s['korean_name'])}</div><p class="lead">{esc(s['hero_lead'])}</p><a class="btn" href="research.html">Explore our research →</a></div></div></section><main><div class="intro-copy">{esc(s['intro'])}</div><section class="section"><div class="section-head"><div><div class="label">What we explore</div><h2>Research Areas</h2></div><a href="research.html">Explore Research →</a></div><div class="research-grid">'''

for x in r:
    h += f'''<a class="research-card" href="research.html#{href(x['id'])}">{img(x['image'], x['title'])}<div class="research-overlay"></div><div class="research-copy"><div class="num">{esc(x['number'])}</div><h3>{esc(x['title'])}</h3><p>{esc(x['short'])}</p></div></a>'''

h += '''</div></section><section class="section"><div class="section-head"><div><div class="label">Selected</div><h2>Highlights</h2></div></div><div class="highlights">'''

if hl:
    kind, title, meta, image = hl[0]
    h += f'''<a class="highlight-main" href="publications.html">{img(image, title) if image else ''}<div class="highlight-body"><div class="kicker">{esc(kind)}</div><h3>{esc(title)}</h3><p>{esc(meta)}</p></div></a><div class="highlight-side">'''
    for kind, title, meta, image in hl[1:3]:
        h += f'''<a class="highlight-small" href="research.html"><div class="kicker">{esc(kind)}</div><h3>{esc(title)}</h3><p>{esc(meta)}</p></a>'''
    h += '</div>'

h += '''</div></section><section class="section"><div class="section-head"><div><div class="label">Updates</div><h2>Recent News</h2></div><a href="news.html">View all news →</a></div><div class="news-grid">'''

for i, n in enumerate(news_sorted[:6], 1):
    summary = f'<p>{esc(n["summary"])}</p>' if n.get('summary') else ''
    h += f'''<a class="news-card news-text-card" href="news.html"><div class="news-card-top"><span class="news-index">{i:02d}</span><span class="news-date">{esc(n['date'])}</span></div><div class="news-meta">{esc(n['category'])}</div><h3>{esc(n['title'])}</h3>{summary}<span class="news-arrow">↗</span></a>'''

h += f'''</div></section><div class="join-strip"><div><h2>Interested in joining {esc(SHORT_NAME)}?</h2><p>Graduate students · Undergraduate researchers · Collaborations</p></div><a class="btn" href="join.html">Join {esc(SHORT_NAME)} →</a></div></main>'''
h += foot()
(OUT / 'index.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# Research
# --------------------------------------------------

h = (
    head('Research', 'Research')
    + pagehero(
        'Research',
        'Optical imaging, sensing, thermal photonics, and optical systems — from fundamental concepts to biomedical and emerging applications.'
    )
    + '<main>'
)

for x in r:
    h += f'''<section class="research-feature" id="{href(x['id'])}"><div class="feature-image">{img(x['image'], x['title'])}</div><div class="feature-copy"><div class="num">{esc(x['number'])}</div><h2>{esc(x['title'])}</h2><p>{esc(x['description'])}</p></div></section>'''

h += '''<section class="section" style="margin-top:75px"><div class="section-head"><div><div class="label">Research & Projects</div><h2>Research Projects</h2></div></div><div class="project-list">'''

for p in projs:
    h += f'''<div class="project"><div class="status">{esc(p['status'])}</div><div><h3>{esc(p['title'])}</h3><p>{esc(p['agency'])} · {esc(p['period'])}</p></div></div>'''

h += '</div></section></main>' + foot()
(OUT / 'research.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# People
# --------------------------------------------------

pe = D['people']
pi = pe['pi']


def external_link(url, label='View link ↗'):
    if not url:
        return ''
    return f'<a class="pub-link" href="{href(url)}" target="_blank" rel="noopener">{esc(label)}</a>'


def cv_record(period, title, organization, link=''):
    period_text = esc(period) if period else '—'
    return f'''<div class="record"><div class="record-year">{period_text}</div><div><h3>{esc(title)}</h3><p>{esc(organization)}</p>{external_link(link)}</div></div>'''


h = (
    head('People', 'People')
    + pagehero(
        'People',
        f'Principal Investigator, current members, and alumni of {SHORT_NAME}.'
    )
    + '<main>'
)

h += '<section class="section"><div class="pi">'
h += img(pi['photo'], pi['name'])
h += '<div>'
h += '<div class="eyebrow">Principal Investigator</div>'
h += f'<h2>{esc(pi["name"])}</h2>'
h += f'<div class="role">{esc(pi["title"])}</div>'
h += f'<p>{esc(pi["department"])}</p>'
h += f'<p>{esc(pi["bio"])}</p>'
h += (
    f'<p><b>Office</b> {esc(pi["office"])}'
    f'<br><b>Tel</b> {esc(pi["phone"])}'
    f'<br><b>Email</b> {esc(pi["email"])}</p>'
)
h += external_link(pi.get('scholar', ''), 'Google Scholar ↗')
h += '</div></div></section>'

# Academic Appointments
h += '<section class="achievement-section"><h2>Academic Appointments</h2>'
for item in pi.get('appointments', []):
    h += cv_record(
        item.get('period', ''),
        item.get('title', ''),
        item.get('organization', ''),
        item.get('link', '')
    )
h += '</section>'

# Academic Leadership
h += '<section class="achievement-section"><h2>Academic Leadership</h2>'
for item in pi.get('leadership', []):
    h += cv_record(
        item.get('period', ''),
        item.get('title', ''),
        item.get('organization', ''),
        item.get('link', '')
    )
h += '</section>'

# Academic Service
h += '<section class="achievement-section"><h2>Academic Service</h2>'
for item in pi.get('service', []):
    h += cv_record(
        item.get('period', ''),
        item.get('title', ''),
        item.get('organization', ''),
        item.get('link', '')
    )
h += '</section>'

# Education
h += '<section class="achievement-section"><h2>Education</h2>'
for item in pi.get('education', []):
    h += cv_record(
        item.get('year', ''),
        item.get('degree', ''),
        item.get('institution', ''),
        item.get('link', '')
    )
h += '</section>'

# Honors & Awards
h += '<section class="achievement-section"><h2>Honors & Awards</h2>'
for item in pi.get('honors', []):
    h += cv_record(
        item.get('year', ''),
        item.get('title', ''),
        item.get('organization', ''),
        item.get('link', '')
    )
h += '</section>'

# Current Members
h += '''<section class="section"><div class="section-head"><div><div class="label">Team</div><h2>Current Members</h2></div></div><div class="member-grid">'''

for p in pe.get('current', []):
    email_line = f'<p>{esc(p["email"])}</p>' if p.get('email') else ''
    h += f'''<div class="member">{img(p['photo'], p['name'])}<h3>{esc(p['name'])}</h3><p><b>{esc(p['role'])}</b></p><p>{esc(p['interest'])}</p>{email_line}</div>'''

h += '</div></section>'

# Alumni
h += '''<section class="section"><div class="section-head"><div><div class="label">Alumni</div><h2>Where they are now</h2></div></div>'''

for a in pe.get('alumni', []):
    h += f'''<div class="alumni-row"><strong>{esc(a['name'])}</strong><span>{esc(a['period'])}</span><span>{esc(a.get('next', ''))}</span></div>'''

h += '</section></main>' + foot()
(OUT / 'people.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# Publications
# --------------------------------------------------


def publication_metrics(p):
    chips = []
    if p.get('impact_factor') not in (None, ''):
        chips.append(f'<span class="metric if">IF {esc(p["impact_factor"])}</span>')
    if p.get('jcr_percent') not in (None, ''):
        chips.append(f'<span class="metric jcr">JCR {esc(p["jcr_percent"])}%</span>')
    if p.get('jcr_category'):
        label = esc(p['jcr_category'])
        if p.get('jcr_year') not in (None, ''):
            label += f' · {esc(p["jcr_year"])}'
        chips.append(f'<span class="metric category">{label}</span>')
    return ''.join(chips)


h = (
    head('Publications', 'Publications')
    + pagehero(
        'Publications',
        'Our publications are organized by year and presented with representative images and journal information.'
    )
    + '<main><div class="pub-tools">'
    + ''.join(f'<span class="chip">{y}</span>' for y in PUBLICATION_YEARS)
    + '</div>'
)

for y in PUBLICATION_YEARS:
    h += f'<h2 class="pub-year">{y}</h2><div class="pub-grid">'
    year_pubs = [x for x in pubs if x['year'] == y]
    year_pubs.sort(key=lambda x: str(x.get('date', '')), reverse=True)
    for p in year_pubs:
        metrics = publication_metrics(p)
        h += f'''<article class="pub-card">{img(p['image'], p['title'])}<div class="pub-copy"><div class="pub-journal">{esc(p['journal'])}</div><h3>{esc(p['title'])}</h3><div class="pub-authors">{esc(p['authors'])}</div><div class="pub-metrics">{metrics}</div><div class="pub-date">{esc(p['date'])}</div><a class="pub-link" href="{href(p['url'])}">VIEW PAPER ↗</a></div></article>'''
    h += '</div>'

h += '</main>' + foot()
(OUT / 'publications.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# Achievements
# --------------------------------------------------

ac = D['achievements']
h = (
    head('Achievements', 'Achievements')
    + pagehero(
        'Achievements',
        'Patents, awards & honors, and conference activities of our laboratory.'
    )
    + '<main><div class="tabs"><a class="tablink" href="#patents">Patents</a><a class="tablink" href="#awards">Awards & Honors</a><a class="tablink" href="#conferences">Conferences</a></div>'
)

for key, title in [
    ('patents', 'Patents'),
    ('awards', 'Awards & Honors'),
    ('conferences', 'Conferences'),
]:
    h += f'<section id="{key}" class="achievement-section"><h2>{title}</h2>'
    for a in ac[key]:
        if key == 'patents':
            body = f'''<h3>{esc(a['title'])}</h3><p>{esc(a['people'])}</p><p>{esc(a['status'])} · {esc(a['number'])}</p>'''
        elif key == 'awards':
            body = f'''<h3>{esc(a['title'])}</h3><p>{esc(a['recipient'])} · {esc(a['organization'])}</p>'''
        else:
            body = f'''<h3>{esc(a['title'])}</h3><p>{esc(a['type'])} · {esc(a['event'])}</p><p>{esc(a['date'])} · {esc(a['location'])}</p>'''
        h += f'''<div class="record"><div class="record-year">{esc(a['year'])}</div><div>{body}</div></div>'''
    h += '</section>'

h += '</main>' + foot()
(OUT / 'achievements.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# News
# --------------------------------------------------

h = (
    head('News', 'News')
    + pagehero(
        'News',
        'Publications, awards, conferences, people, projects, and laboratory updates.'
    )
    + '<main>'
)

news_years = sorted({n['_date_obj'].year for n in news_sorted}, reverse=True)

for y in news_years:
    h += f'<section class="news-year-section"><h2 class="news-year">{y}</h2><div class="news-list">'
    for n in [x for x in news_sorted if x['_date_obj'].year == y]:
        summary = (
            f'<p class="news-summary">{esc(n["summary"])}</p>'
            if n.get('summary')
            else ''
        )
        arrow = (
            f'<a class="news-row-arrow" href="{href(n["link"])}">↗</a>'
            if n.get('link')
            else '<span class="news-row-arrow muted">—</span>'
        )
        h += f'''<article class="news-row"><div class="news-row-date">{esc(n['date'])}</div><div class="news-row-body"><div class="news-meta">{esc(n['category'])}</div><h3>{esc(n['title'])}</h3>{summary}</div>{arrow}</article>'''
    h += '</div></section>'

h += '</main>' + foot()
(OUT / 'news.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# Join Us
# --------------------------------------------------

h = (
    head('Join Us', 'Join Us')
    + pagehero(
        f'Join {SHORT_NAME}',
        'We welcome students and collaborators interested in optical imaging, sensing, thermal photonics, and optical systems.'
    )
    + f'''<main><div class="join-grid"><div class="join-card"><h2>Graduate Students</h2><p>Students interested in optical experiments, imaging, sensing, photonics, thermal management, or system development are encouraged to get in touch.</p><h2>Undergraduate Researchers</h2><p>Undergraduate research can begin through focused projects in simulation, optical experiments, imaging, sensing, or materials.</p><h2>Collaborations</h2><p>We welcome interdisciplinary collaborations connecting optical science and engineering with biomedical and emerging applications.</p></div><div class="contact-box"><div class="eyebrow">Contact</div><h2>{esc(SHORT_NAME)} · Yonsei University</h2><p><b>Email</b><br>{esc(s['email'])}</p><p><b>Phone</b><br>{esc(s['phone'])}</p><p><b>Address</b><br>{esc(s['address'])}</p></div></div></main>'''
)

h += foot()
(OUT / 'join.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# Copy assets
# --------------------------------------------------

shutil.copytree(ROOT / 'assets', OUT / 'assets')
