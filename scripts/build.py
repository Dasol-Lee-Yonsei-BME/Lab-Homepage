from pathlib import Path
import html
import re
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
ac = D['achievements']
SHORT_NAME = s.get('short_name', 'Photonics Lab.')


def esc(value):
    return html.escape(str(value))


def href(value):
    return html.escape(str(value), quote=True)


# Publications validation
for p in pubs:
    try:
        p['year'] = int(p['year'])
    except (TypeError, ValueError, KeyError):
        raise SystemExit(
            f"Publication year must be a 4-digit number: {p.get('title')}"
        )

PUBLICATION_YEARS = sorted({p['year'] for p in pubs}, reverse=True)
CSS = (ROOT / 'assets' / 'style.css').read_text(encoding='utf-8')


# People-page layout refinements. These rules are appended to the shared CSS
# so the People page can be updated without editing assets/style.css separately.
PEOPLE_CSS = r'''
.people-major-section { margin-bottom: 110px; }
.people-major-section > .section-head { margin-bottom: 42px; }
.people-major-section .pi { padding-bottom: 46px; border-bottom: 0; }

.people-cv { margin-top: 58px; }
.people-cv-section { padding: 34px 0 10px; border-top: 1px solid var(--line); }
.people-cv-section:first-child { border-top: 1px solid #9aacbb; }
.people-cv-section .cv-heading {
  margin: 0 0 18px;
  color: var(--navy2);
  font-size: 26px;
  line-height: 1.2;
  letter-spacing: -.02em;
}
.people-cv .record {
  grid-template-columns: minmax(230px, 260px) minmax(0, 1fr);
  gap: 28px;
  padding: 20px 0;
}
.people-cv .record-year {
  white-space: nowrap;
  font-size: 14px;
  line-height: 1.45;
}
.people-cv .record h3 { margin: 0 0 4px; }
.people-cv .record p { margin: 2px 0; }

@media (max-width: 760px) {
  .people-major-section { margin-bottom: 78px; }
  .people-major-section > .section-head { margin-bottom: 28px; }
  .people-cv { margin-top: 40px; }
  .people-cv-section { padding-top: 28px; }
  .people-cv-section .cv-heading { font-size: 23px; }
  .people-cv .record {
    grid-template-columns: 1fr;
    gap: 7px;
    padding: 18px 0;
  }
  .people-cv .record-year { white-space: normal; }
}
'''
CSS += PEOPLE_CSS


# Publications-page refinements. Kept here so only build.py and
# data/publications.yml need to be replaced for this update.
PUBLICATION_CSS = r'''
.pub-legend {
  display:flex; flex-wrap:wrap; gap:10px 22px; align-items:center;
  margin:0 0 34px; padding:16px 18px; border:1px solid var(--line);
  background:#fbfdff; color:#536575; font-size:13px;
}
.pub-legend strong { color:var(--navy2); }
.lab-author { color:var(--blue); font-weight:700; }
.pi-author {
  color:var(--ink); font-weight:800; text-decoration:underline;
  text-decoration-thickness:1.5px; text-underline-offset:2px;
}
.pub-tools { margin-bottom:48px; }
.pub-tools .chip { text-decoration:none; cursor:pointer; transition:.18s ease; }
.pub-tools .chip:hover { background:var(--navy); color:#fff; border-color:var(--navy); }
.pub-year { scroll-margin-top:105px; }
.pub-card.long-authors { grid-column:1 / -1; }
.pub-authors { line-height:1.55; }
.pub-authors sup { font-size:.72em; line-height:0; vertical-align:super; margin-left:1px; }
.pub-journal .pub-issn { font-weight:600; opacity:.78; letter-spacing:0; }
.pub-biblio { margin-top:8px; color:#778694; font-size:12px; line-height:1.45; }
.pub-metrics { margin-top:10px; }
.pub-card.no-image {
  grid-template-columns:1fr;
  min-height:0;
}
.pub-card.no-image .pub-copy {
  padding:21px 22px 22px;
}
.pub-card.has-image {
  grid-template-columns:190px minmax(0,1fr);
  align-items:start;
}
.pub-card.has-image > img {
  display:block;
  width:100%;
  height:auto !important;
  min-height:0 !important;
  max-height:none !important;
  object-fit:contain !important;
  object-position:center center;
  align-self:center;
  background:#fff;
}
@media (max-width:760px) {
  .pub-card.long-authors { grid-column:auto; }
  .pub-card.has-image { grid-template-columns:145px minmax(0,1fr); }
  .pub-card.no-image { grid-template-columns:1fr; }
}
@media (max-width:520px) {
  .pub-card.has-image { grid-template-columns:1fr; }
  .pub-card.has-image > img {
    width:100%;
    height:auto !important;
    aspect-ratio:auto !important;
  }
}
'''
CSS += PUBLICATION_CSS
# Achievements-page refinements. Kept here so the update only requires
# scripts/build.py and data/achievements.yml.
ACHIEVEMENTS_CSS = r'''
.achievement-tabs { margin-bottom: 54px; }
.achievement-tabs .tablink { text-decoration:none; transition:.18s ease; }
.achievement-tabs .tablink:hover { background:var(--navy); color:#fff; border-color:var(--navy); }
.achievement-section { scroll-margin-top:105px; margin-bottom:96px; }
.achievement-section > h2 { margin-bottom:30px; }
.ach-group { margin-top:42px; }
.ach-group:first-of-type { margin-top:26px; }
.ach-group-head { display:flex; align-items:flex-end; justify-content:space-between; gap:18px; margin-bottom:10px; }
.ach-group-head h3 { margin:0; color:var(--navy2); font-size:23px; line-height:1.25; }
.ach-group-head span { color:var(--muted); font-size:12px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.ach-subgroup { margin:24px 0 8px; color:var(--blue); font-size:12px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.ach-record { display:grid; grid-template-columns:125px minmax(0,1fr); gap:26px; padding:20px 0; border-bottom:1px solid var(--line); }
.ach-date { color:var(--blue); font-weight:800; font-size:13px; line-height:1.45; white-space:nowrap; }
.ach-record h4 { margin:0 0 6px; color:var(--ink); font-size:17px; line-height:1.4; }
.ach-record p { margin:3px 0; color:var(--muted); font-size:13px; line-height:1.55; }
.ach-secondary { color:#697b89 !important; font-style:italic; }
.ach-people { color:#425563 !important; }
.ach-meta { display:flex; flex-wrap:wrap; gap:7px 12px; align-items:center; margin-top:8px !important; }
.ach-badge { display:inline-block; padding:4px 8px; border:1px solid #ccd8e1; background:#f8fbfd; color:var(--navy2); font-size:10px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }
.ach-badge.pending { color:#76520d; background:#fffaf0; border-color:#e8d7ad; }
.ach-badge.registered { color:#205f45; background:#f3faf6; border-color:#bed9cb; }
.ach-badge.international { color:#285a8a; background:#f3f8fd; border-color:#bfd1e4; }
.ach-note { margin-top:8px !important; color:#725615 !important; font-weight:700; }
.ach-link { display:inline-block; margin-top:8px; color:var(--blue); font-size:12px; font-weight:800; text-decoration:none; }
.ach-link:hover { text-decoration:underline; }
.tech-transfer { margin-top:56px; padding-top:28px; border-top:1px solid #9aacbb; }
.tech-transfer h3 { margin:0 0 10px; color:var(--navy2); font-size:23px; }
@media (max-width:760px) {
  .achievement-section { margin-bottom:72px; }
  .ach-group-head { display:block; }
  .ach-group-head span { display:block; margin-top:6px; }
  .ach-record { grid-template-columns:1fr; gap:7px; padding:18px 0; }
  .ach-date { white-space:normal; }
}
'''
CSS += ACHIEVEMENTS_CSS


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

    base_url = 'https://photon.yonsei.ac.kr'

    page_urls = {
        'Home': f'{base_url}/',
        'People': f'{base_url}/people.html',
        'Research': f'{base_url}/research.html',
        'Publications': f'{base_url}/publications.html',
        'Achievements': f'{base_url}/achievements.html',
        'News': f'{base_url}/news.html',
        'Join Us': f'{base_url}/join.html',
    }

    seo_titles = {
        'Home': f'Dasol Lee | {s["lab_name"]} | {s["university"]}',
        'People': f'Dasol Lee & Lab Members | {s["lab_name"]} | {s["university"]}',
        'Research': f'Research | {s["lab_name"]} | {s["university"]}',
        'Publications': f'Publications | Dasol Lee | {s["university"]}',
        'Achievements': f'Achievements | Dasol Lee | {s["university"]}',
        'News': f'News | {s["lab_name"]} | {s["university"]}',
        'Join Us': f'Join Us | {s["lab_name"]} | {s["university"]}',
    }

    seo_descriptions = {
        'Home': (
            f'Official website of Dasol Lee and {s["lab_name"]} at '
            f'{s["university"]}. Research in optical imaging, sensing, '
            f'thermal photonics, and optical systems.'
        ),
        'People': (
            f'Dasol Lee and members of {s["lab_name"]}, '
            f'{s["department"]}, {s["university"]}.'
        ),
        'Research': (
            f'Research from {s["lab_name"]} at {s["university"]} '
            f'in optical imaging, sensing, thermal photonics, '
            f'and optical systems.'
        ),
        'Publications': (
            f'Peer-reviewed publications from Dasol Lee and '
            f'{s["lab_name"]} at {s["university"]}.'
        ),
        'Achievements': (
            f'Patents, awards, conferences, invited talks, and academic '
            f'activities of Dasol Lee and {s["lab_name"]}.'
        ),
        'News': (
            f'Latest research, publication, achievement, and laboratory '
            f'updates from {s["lab_name"]} at {s["university"]}.'
        ),
        'Join Us': (
            f'Graduate student, undergraduate researcher, and collaboration '
            f'opportunities at {s["lab_name"]}, {s["university"]}.'
        ),
    }

    seo_title = seo_titles.get(
        title,
        f'{title} | {s["lab_name"]} | {s["university"]}'
    )

    description = seo_descriptions.get(
        title,
        f'{title} page of {s["lab_name"]} at {s["university"]}.'
    )

    canonical = page_urls.get(title, f'{base_url}/')

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<meta name="google-site-verification" content="tI54YZfk5YNNvyT6SR_VK4kN9zCZRI2usKHY-R5lmJs" />

<title>{esc(seo_title)}</title>
<meta name="description" content="{href(description)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{href(canonical)}">

<meta property="og:title" content="{href(seo_title)}">
<meta property="og:description" content="{href(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{href(canonical)}">
<meta property="og:site_name" content="{href(s["lab_name"])}">

<style>{CSS}</style>
</head>
<body>
<header class="site-header">
<div class="header">
<a class="brand" href="index.html">{esc(SHORT_NAME)}</a>
<nav class="nav">{nav}</nav>
</div>
</header>'''


def foot():
    return f'''<footer class="footer"><div class="footer-inner"><strong>{esc(SHORT_NAME)}</strong>{esc(s['lab_name'])} · {esc(s['department'])} · {esc(s['university'])} ({esc(s['campus'])})</div></footer></body></html>'''


def pagehero(title, text):
    return f'''<section class="page-hero"><div class="page-hero-inner"><div class="eyebrow">{esc(SHORT_NAME)} · Yonsei University</div><h1>{esc(title)}</h1><p>{esc(text)}</p></div></section>'''


def parse_news_date(value):
    """Return a sortable date while preserving flexible display dates.

    Accepted examples: 2026.07.10, 2025.11.30-12.05, 2026.02, 2024.11.
    Ranges are sorted by their first date; month-only records use day 1.
    """
    text = str(value or '').strip()
    compact = re.sub(r'\s+', '', text)

    # Full date at the beginning of the string, including date ranges.
    m = re.match(r'^(\d{4})[./-](\d{1,2})[./-](\d{1,2})', compact)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # Month-only date.
    m = re.match(r'^(\d{4})[./-](\d{1,2})(?:\D|$)', compact)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), 1)

    # Year-only fallback.
    m = re.match(r'^(\d{4})$', compact)
    if m:
        return datetime(int(m.group(1)), 1, 1)

    raise SystemExit(f'Unsupported News date: {text}')


def make_news_item(date, category, title, summary='', link='', source='manual'):
    item = {
        'date': str(date),
        'category': str(category),
        'title': str(title),
        'summary': str(summary or ''),
        'link': str(link or ''),
        'source': source,
    }
    item['_date_obj'] = parse_news_date(item['date'])
    return item


# Standalone news.yml records.
news_items = []
for n in news:
    if not n.get('title') or not n.get('category') or not n.get('date'):
        raise SystemExit(f'News requires date, category, and title: {n}')
    news_items.append(make_news_item(
        n['date'], n['category'], n['title'], n.get('summary', ''), n.get('link', ''), 'manual'
    ))

# Publication highlights automatically become News items.
for p in pubs:
    if not p.get('highlight'):
        continue
    title = p.get('news_title') or p.get('title', '')
    summary = p.get('news_summary') or f'Published in {p.get("journal", "")}.'.strip()
    news_items.append(make_news_item(
        p.get('date', p.get('year', '')),
        'Publication Highlight',
        title,
        summary,
        f'publications.html#year-{p.get("year", "")}',
        'publication',
    ))

# Highlighted research projects also become News items.
# The first date in the project period is used as the News date.
for p in projs:
    if not p.get('highlight'):
        continue
    start_date = str(p.get('period', '')).split('–', 1)[0].split('-', 1)[0].strip()
    title = p.get('news_title') or p.get('title', '')
    summary = p.get('news_summary') or ' · '.join(
        x for x in [p.get('agency', ''), p.get('period', '')] if x
    )
    news_items.append(make_news_item(
        start_date or p.get('year', ''),
        'Project Highlight',
        title,
        summary,
        'research.html',
        'project',
    ))


def add_achievement_news(items, category, anchor, title_fn, summary_fn):
    for a in items:
        if not a.get('news'):
            continue
        title = a.get('news_title') or title_fn(a)
        summary = a.get('news_summary') or summary_fn(a)
        news_items.append(make_news_item(
            a.get('date', a.get('year', '')),
            a.get('news_category') or category,
            title,
            summary,
            f'achievements.html#{anchor}',
            'achievement',
        ))


# Patents and technology transfer.
add_achievement_news(
    ac.get('patents', []), 'Patent', 'patents',
    lambda a: a.get('title_ko') or a.get('title_en') or 'Patent update',
    lambda a: f'{a.get("status", "")} · {a.get("jurisdiction", "")} {a.get("number", "")}'.strip(' ·'),
)
add_achievement_news(
    ac.get('technology_transfer', []), 'Technology Transfer', 'patents',
    lambda a: a.get('title', 'Technology transfer'),
    lambda a: a.get('description', ''),
)

# Awards & honors.
for award_group in ('pi', 'students'):
    add_achievement_news(
        ac.get('awards', {}).get(award_group, []), 'Award & Honor', 'awards',
        lambda a: a.get('title', 'Award'),
        lambda a: ' · '.join(x for x in [a.get('recipient', ''), a.get('organization', '')] if x),
    )

# Conferences: PI international/domestic and students.
pi_confs = ac.get('conferences', {}).get('pi', {})
for scope in ('international', 'domestic'):
    add_achievement_news(
        pi_confs.get(scope, []), 'Conference', 'conferences',
        lambda a: a.get('title', 'Conference activity'),
        lambda a: ' · '.join(x for x in [a.get('type', ''), a.get('event', ''), a.get('location', '')] if x),
    )
add_achievement_news(
    ac.get('conferences', {}).get('students', []), 'Conference', 'conferences',
    lambda a: a.get('title', 'Conference activity'),
    lambda a: ' · '.join(x for x in [a.get('type', ''), a.get('event', '')] if x),
)

# Talks and academic service.
add_achievement_news(
    ac.get('talks', []), 'Talk', 'talks',
    lambda a: a.get('title') or a.get('host') or a.get('institution') or 'Invited talk',
    lambda a: ' · '.join(x for x in [a.get('host', ''), a.get('institution', '')] if x),
)
add_achievement_news(
    ac.get('academic_service', []), 'Academic Service', 'academic-service',
    lambda a: a.get('role', 'Academic service'),
    lambda a: a.get('event', ''),
)

news_sorted = sorted(news_items, key=lambda n: n['_date_obj'], reverse=True)


# Home Selected Highlights
# `highlight: true` controls News integration for publications/projects.
# `home_highlight: true` independently marks items as eligible for Home Highlights.
# Eligible items are sorted by date, and only the latest three are displayed.
hl = []
for p in pubs:
    if p.get('home_highlight'):
        hl.append((
            'Publication',
            p['title'],
            p['journal'],
            p.get('image', ''),
            f'publications.html#year-{p.get("year", "")}',
            parse_news_date(p.get('date', p.get('year', ''))),
        ))
for p in projs:
    if p.get('home_highlight'):
        start_date = str(p.get('period', '')).split('–', 1)[0].split('-', 1)[0].strip()
        hl.append((
            'Research Project',
            p['title'],
            p['agency'],
            None,
            'research.html',
            parse_news_date(start_date or p.get('year', '')),
        ))

hl = sorted(hl, key=lambda item: item[5], reverse=True)[:3]


# --------------------------------------------------
# Home
# --------------------------------------------------

h = head('Home', 'Home') + f'''<section class="hero"><div class="hero-inner"><div><div class="eyebrow">{esc(s['university'])}<br>{esc(s['department'])}</div><h1>{esc(s['hero_title'])}</h1><div class="ko">{esc(s['lab_name'])}</div><div class="ko">{esc(s['korean_name'])}</div><p class="lead">{esc(s['hero_lead'])}</p><a class="btn" href="research.html">Explore our research →</a></div></div></section><main><div class="intro-copy">{esc(s['intro'])}</div><section class="section"><div class="section-head"><div><div class="label">What we explore</div><h2>Research Areas</h2></div><a href="research.html">Explore Research →</a></div><div class="research-grid">'''

for x in r:
    h += f'''<a class="research-card" href="research.html#{href(x['id'])}">{img(x['image'], x['title'])}<div class="research-overlay"></div><div class="research-copy"><div class="num">{esc(x['number'])}</div><h3>{esc(x['title'])}</h3><p>{esc(x['short'])}</p></div></a>'''

h += '''</div></section><section class="section"><div class="section-head"><div><div class="label">Selected</div><h2>Highlights</h2></div></div><div class="highlights">'''

if hl:
    kind, title, meta, image, link, _date_obj = hl[0]
    h += f'''<a class="highlight-main" href="{href(link)}">{img(image, title) if image else ''}<div class="highlight-body"><div class="kicker">{esc(kind)}</div><h3>{esc(title)}</h3><p>{esc(meta)}</p></div></a><div class="highlight-side">'''
    for kind, title, meta, image, link, _date_obj in hl[1:]:
        h += f'''<a class="highlight-small" href="{href(link)}"><div class="kicker">{esc(kind)}</div><h3>{esc(title)}</h3><p>{esc(meta)}</p></a>'''
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


def external_link(url, label='View link'):
    if not url:
        return ''
    return f'<a class="pub-link" href="{href(url)}" target="_blank" rel="noopener">{esc(label)} &#8599;</a>'


def cv_record(period, title, organization, link=''):
    period_text = esc(period) if period else '\u2014'
    return f'''<div class="record"><div class="record-year">{period_text}</div><div><h3>{esc(title)}</h3><p>{esc(organization)}</p>{external_link(link)}</div></div>'''


def cv_section(title, items, year_key='period', title_key='title', org_key='organization'):
    if not items:
        return ''
    out = f'<div class="people-cv-section"><h3 class="cv-heading">{esc(title)}</h3>'
    for item in items:
        out += cv_record(
            item.get(year_key, ''),
            item.get(title_key, ''),
            item.get(org_key, ''),
            item.get('link', '')
        )
    out += '</div>'
    return out


h = (
    head('People', 'People')
    + pagehero(
        'People',
        f'Principal Investigator, current members, and alumni of {SHORT_NAME}.'
    )
    + '<main>'
)

# 01 - Principal Investigator
h += '''<section class="section people-major-section"><div class="section-head"><div><div class="label">01 &middot; Principal Investigator</div><h2>Principal Investigator</h2></div></div>'''
h += '<div class="pi">'
h += img(pi['photo'], pi['name'])
h += '<div>'
h += f'<h2>{esc(pi["name"])}</h2>'
h += f'<div class="role">{esc(pi["title"])}</div>'
h += f'<p>{esc(pi["department"])}</p>'
h += f'<p>{esc(pi["bio"])}</p>'
h += (
    f'<p><b>Office</b> {esc(pi["office"])}'
    f'<br><b>Tel</b> {esc(pi["phone"])}'
    f'<br><b>Email</b> {esc(pi["email"])}</p>'
)
h += external_link(pi.get('scholar', ''), 'Google Scholar')
h += '</div></div>'

# PI curriculum vitae
h += '<div class="people-cv">'
h += cv_section('Academic Appointments', pi.get('appointments', []))
h += cv_section('Academic Leadership', pi.get('leadership', []))
h += cv_section('Academic Service', pi.get('service', []))
h += cv_section(
    'Education',
    pi.get('education', []),
    year_key='year',
    title_key='degree',
    org_key='institution'
)
h += cv_section(
    'Honors & Awards',
    pi.get('honors', []),
    year_key='year'
)
h += '</div></section>'

# 02 - Team
h += '''<section class="section people-major-section"><div class="section-head"><div><div class="label">02 &middot; Team</div><h2>Current Members</h2></div></div><div class="member-grid">'''

for p in pe.get('current', []):
    email_line = f'<p>{esc(p["email"])}</p>' if p.get('email') else ''
    h += f'''<div class="member">{img(p['photo'], p['name'])}<h3>{esc(p['name'])}</h3><p><b>{esc(p['role'])}</b></p><p>{esc(p['interest'])}</p>{email_line}</div>'''

h += '</div></section>'

# 03 - Alumni
h += '''<section class="section people-major-section"><div class="section-head"><div><div class="label">03 &middot; Alumni</div><h2>Alumni</h2></div></div>'''

for a in pe.get('alumni', []):
    h += f'''<div class="alumni-row"><strong>{esc(a['name'])}</strong><span>{esc(a['period'])}</span><span>{esc(a.get('next', ''))}</span></div>'''

h += '</section></main>' + foot()
(OUT / 'people.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# Publications
# --------------------------------------------------

# Names verified from the current/alumni list on the legacy BNSL site.
# Add a new student here once they appear as an author on a publication.
LAB_AUTHORS = [
    'Kyung-Hyun Yu',
    'Jihoon Yang',
    'Marjona Murodkhuja Kizi Kiyomova',
    'Wooju Choi',
    'Semere Araya Asefa',
    'Sangmin Shim',
    'Seokgyu Kwon',
    'Minseo Jeong',
    'Changhwan Hyeon',
    'Lawrence Naatey Terkper',
]


def format_authors(author_text):
    rendered = esc(author_text)

    # Lab students/alumni are blue.
    for name in sorted(LAB_AUTHORS, key=len, reverse=True):
        safe = esc(name)
        rendered = rendered.replace(
            safe,
            f'<span class="lab-author">{safe}</span>'
        )

    # PI stays black, bold and underlined. Older papers use the abbreviated form.
    for name in ('Dasol Lee', 'D. Lee'):
        safe = esc(name)
        rendered = rendered.replace(
            safe,
            f'<span class="pi-author">{safe}</span>'
        )

    # Author-role symbols are displayed as superscripts.
    # When a first/co-first author is also a corresponding author,
    # keep the dagger, comma, and asterisk together in one superscript.
    combined_marker = '__AUTHOR_DAGGER_STAR__'
    rendered = rendered.replace('†,*', combined_marker)
    rendered = rendered.replace('†', '<sup>†</sup>')
    rendered = rendered.replace('*', '<sup>*</sup>')
    rendered = rendered.replace(combined_marker, '<sup>†,*</sup>')

    return rendered


def publication_metrics(p):
    chips = []
    if p.get('impact_factor') not in (None, ''):
        chips.append(f'<span class="metric if">IF {esc(p["impact_factor"])}</span>')
    if p.get('jcr_percent') not in (None, ''):
        chips.append(f'<span class="metric jcr">JCR {esc(p["jcr_percent"])}%</span>')
    if p.get('jcr_category'):
        label = esc(p['jcr_category'])
        if p.get('jcr_year') not in (None, ''):
            label += f' / {esc(p["jcr_year"])}'
        chips.append(f'<span class="metric category">{label}</span>')
    return ''.join(chips)


def publication_month(value):
    text = str(value or '').strip()
    if len(text) >= 7:
        return text[:7]
    return text or '-'


def publication_biblio(p):
    volume = str(p.get('volume') or '-').strip() or '-'
    issue = str(p.get('issue') or '-').strip() or '-'
    pages = str(p.get('pages') or '-').strip() or '-'
    month = publication_month(p.get('date', ''))
    return f'{esc(volume)}({esc(issue)}), {esc(pages)} · {esc(month)}'


def publication_visual(p):
    # Publication images are optional. If image is blank, no image column is rendered.
    if not p.get('image'):
        return ''
    return img(p['image'], p['title'])


legend = f'''<div class="pub-legend">
<span><strong>†</strong> First / co-first author</span>
<span><strong>*</strong> Corresponding author</span>
<span><span class="lab-author">Blue author</span> = {esc(SHORT_NAME)} student / alumnus</span>
</div>'''

h = (
    head('Publications', 'Publications')
    + pagehero(
        'Publications',
        'Peer-reviewed journal papers from our laboratory and prior research.'
    )
    + '<main>'
    + legend
    + '<nav class="pub-tools" aria-label="Publication years">'
    + ''.join(
        f'<a class="chip" href="#year-{y}">{y}</a>'
        for y in PUBLICATION_YEARS
    )
    + '</nav>'
)

for y in PUBLICATION_YEARS:
    h += f'<h2 class="pub-year" id="year-{y}">{y}</h2><div class="pub-grid">'
    year_pubs = [x for x in pubs if x['year'] == y]
    year_pubs.sort(key=lambda x: str(x.get('date', '')), reverse=True)

    for p in year_pubs:
        metrics = publication_metrics(p)
        authors_html = format_authors(p.get('authors', ''))
        biblio_html = publication_biblio(p)

        journal_label = esc(p['journal'])
        if p.get('issn'):
            journal_label += f' <span class="pub-issn">(ISSN {esc(p["issn"])})</span>'

        link_html = ''
        if p.get('url'):
            link_html = (
                f'<a class="pub-link" href="{href(p["url"])}" '
                'target="_blank" rel="noopener">VIEW PAPER &#8599;</a>'
            )

        card_classes = ['pub-card', 'has-image' if p.get('image') else 'no-image']
        if len(str(p.get('authors', ''))) > 420:
            card_classes.append('long-authors')
        card_class = ' '.join(card_classes)

        h += (
            f'<article class="{card_class}">'
            f'{publication_visual(p)}'
            '<div class="pub-copy">'
            f'<div class="pub-journal">{journal_label}</div>'
            f'<h3>{esc(p["title"])}</h3>'
            f'<div class="pub-authors">{authors_html}</div>'
            f'<div class="pub-biblio">{biblio_html}</div>'
            f'<div class="pub-metrics">{metrics}</div>'
            f'{link_html}'
            '</div></article>'
        )

    h += '</div>'

h += '</main>' + foot()
(OUT / 'publications.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# Achievements
# --------------------------------------------------


def ach_link(url, label='View link'):
    if not url:
        return ''
    return (
        f'<a class="ach-link" href="{href(url)}" target="_blank" '
        f'rel="noopener">{esc(label)} &#8599;</a>'
    )


def ach_record(date, body):
    return (
        '<div class="ach-record">'
        f'<div class="ach-date">{esc(date)}</div>'
        f'<div>{body}</div>'
        '</div>'
    )


h = (
    head('Achievements', 'Achievements')
    + pagehero(
        'Achievements',
        'Patents, awards & honors, conference activities, invited talks, and academic service of our laboratory.'
    )
    + '<main><div class="tabs achievement-tabs">'
      '<a class="tablink" href="#patents">Patents</a>'
      '<a class="tablink" href="#awards">Awards & Honors</a>'
      '<a class="tablink" href="#conferences">Conferences</a>'
      '<a class="tablink" href="#talks">Talks</a>'
      '<a class="tablink" href="#academic-service">Academic Service</a>'
      '</div>'
)

# Patents
h += '<section id="patents" class="achievement-section"><h2>Patents</h2>'

patent_groups = [
    ('International · Registered', [
        x for x in ac.get('patents', [])
        if x.get('scope') == 'International' and x.get('status') == 'Registered'
    ]),
    ('Domestic · Pending', [
        x for x in ac.get('patents', [])
        if x.get('scope') == 'Domestic' and x.get('status') == 'Pending'
    ]),
    ('Domestic · Registered', [
        x for x in ac.get('patents', [])
        if x.get('scope') == 'Domestic' and x.get('status') == 'Registered'
    ]),
]

for group_title, items in patent_groups:
    if not items:
        continue
    h += f'<div class="ach-group"><div class="ach-group-head"><h3>{esc(group_title)}</h3><span>{len(items)} records</span></div>'
    for a in items:
        main_title = a.get('title_ko') or a.get('title_en') or '-'
        secondary = ''
        if a.get('title_ko') and a.get('title_en'):
            secondary = f'<p class="ach-secondary">{esc(a["title_en"])}</p>'
        status_class = str(a.get('status', '')).lower()
        body = (
            f'<h4>{esc(main_title)}</h4>'
            f'{secondary}'
            f'<p class="ach-people">{esc(a.get("people", ""))}</p>'
            '<p class="ach-meta">'
            f'<span class="ach-badge {status_class}">{esc(a.get("status", ""))}</span>'
            f'<span>{esc(a.get("jurisdiction", ""))} {esc(a.get("number", ""))}</span>'
            f'<span>{esc(a.get("date_label", "Date"))} · {esc(a.get("date", ""))}</span>'
            '</p>'
        )
        h += ach_record(a.get('date', a.get('year', '')), body)
    h += '</div>'

transfers = ac.get('technology_transfer', [])
if transfers:
    h += '<div class="tech-transfer"><h3>Technology Transfer</h3>'
    for a in transfers:
        body = (
            f'<h4>{esc(a.get("title", ""))}</h4>'
            f'<p>{esc(a.get("description", ""))}</p>'
            f'<p class="ach-people">{esc(a.get("parties", ""))}</p>'
        )
        h += ach_record(a.get('date', a.get('year', '')), body)
    h += '</div>'
h += '</section>'

# Awards & Honors
h += '<section id="awards" class="achievement-section"><h2>Awards & Honors</h2>'
for key, title in [('pi', 'Principal Investigator'), ('students', 'Students')]:
    items = ac.get('awards', {}).get(key, [])
    if not items:
        continue
    h += f'<div class="ach-group"><div class="ach-group-head"><h3>{esc(title)}</h3><span>{len(items)} records</span></div>'
    for a in items:
        detail = f'<p>{esc(a["detail"])}</p>' if a.get('detail') else ''
        body = (
            f'<h4>{esc(a.get("title", ""))}</h4>'
            f'<p class="ach-people">{esc(a.get("recipient", ""))} · {esc(a.get("organization", ""))}</p>'
            f'{detail}'
            f'{ach_link(a.get("link", ""), "View")}'
        )
        h += ach_record(a.get('date', a.get('year', '')), body)
    h += '</div>'
h += '</section>'

# Conferences
h += '<section id="conferences" class="achievement-section"><h2>Conferences</h2>'
pi_confs = ac.get('conferences', {}).get('pi', {})
if pi_confs:
    total_pi = sum(len(pi_confs.get(k, [])) for k in ('international', 'domestic'))
    h += f'<div class="ach-group"><div class="ach-group-head"><h3>Principal Investigator</h3><span>{total_pi} records</span></div>'
    for scope_key, scope_title in [('international', 'International'), ('domestic', 'Domestic')]:
        items = pi_confs.get(scope_key, [])
        if not items:
            continue
        h += f'<div class="ach-subgroup">{esc(scope_title)}</div>'
        for a in items:
            scope_class = scope_title.lower()
            location = f' · {esc(a["location"])}' if a.get('location') else ''
            body = (
                f'<h4>{esc(a.get("title", ""))}</h4>'
                f'<p class="ach-people">{esc(a.get("authors", ""))}</p>'
                '<p class="ach-meta">'
                f'<span class="ach-badge {scope_class}">{esc(scope_title)}</span>'
                f'<span class="ach-badge">{esc(a.get("type", ""))}</span>'
                f'<span>{esc(a.get("event", ""))}{location}</span>'
                '</p>'
            )
            h += ach_record(a.get('date', a.get('year', '')), body)
    h += '</div>'

student_confs = ac.get('conferences', {}).get('students', [])
if student_confs:
    h += f'<div class="ach-group"><div class="ach-group-head"><h3>Students</h3><span>{len(student_confs)} records</span></div>'
    for a in student_confs:
        scope = a.get('scope', '')
        scope_class = scope.lower()
        note = f'<p class="ach-note">{esc(a["note"])}</p>' if a.get('note') else ''
        body = (
            f'<h4>{esc(a.get("title", ""))}</h4>'
            f'<p class="ach-people">{esc(a.get("authors", ""))}</p>'
            '<p class="ach-meta">'
            f'<span class="ach-badge {scope_class}">{esc(scope)}</span>'
            f'<span class="ach-badge">{esc(a.get("type", ""))}</span>'
            f'<span>{esc(a.get("event", ""))}</span>'
            '</p>'
            f'{note}'
        )
        h += ach_record(a.get('date', a.get('year', '')), body)
    h += '</div>'
h += '</section>'

# Talks outside conferences
h += '<section id="talks" class="achievement-section"><h2>Talks</h2>'
h += '<div class="ach-group"><div class="ach-group-head"><h3>Invited Seminars & External Talks</h3><span>Outside conferences</span></div>'
for a in ac.get('talks', []):
    heading = a.get('title') or a.get('host') or a.get('institution') or 'Talk'
    institution = f'<p>{esc(a["institution"])}</p>' if a.get('institution') else ''
    host = '' if heading == a.get('host') else f'<p>{esc(a.get("host", ""))}</p>'
    body = (
        f'<h4>{esc(heading)}</h4>'
        f'{host}{institution}'
        f'{ach_link(a.get("link", ""), "Watch")}'
    )
    h += ach_record(a.get('date', a.get('year', '')), body)
h += '</div></section>'

# Academic Service
service_items = ac.get('academic_service', [])
if service_items:
    h += '<section id="academic-service" class="achievement-section"><h2>Academic Service</h2>'
    h += f'<div class="ach-group"><div class="ach-group-head"><h3>Principal Investigator</h3><span>{len(service_items)} records</span></div>'
    for a in service_items:
        detail = f'<p>{esc(a["detail"])}</p>' if a.get('detail') else ''
        body = (
            f'<h4>{esc(a.get("role", ""))}</h4>'
            f'<p class="ach-people">{esc(a.get("event", ""))}</p>'
            f'{detail}'
        )
        h += ach_record(a.get('date', a.get('year', '')), body)
    h += '</div></section>'

h += '</main>' + foot()
(OUT / 'achievements.html').write_text(h, encoding='utf-8')


# --------------------------------------------------
# News
# --------------------------------------------------

h = (
    head('News', 'News')
    + pagehero(
        'News',
        'Selected updates from publication highlights, achievements, people, media, and laboratory life.'
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
        if n.get('link'):
            external = str(n['link']).startswith(('http://', 'https://'))
            target = ' target="_blank" rel="noopener"' if external else ''
            arrow = f'<a class="news-row-arrow" href="{href(n["link"])}"{target}>↗</a>'
        else:
            arrow = '<span class="news-row-arrow muted">—</span>'
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
