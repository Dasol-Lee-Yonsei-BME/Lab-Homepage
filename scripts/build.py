from pathlib import Path
import yaml, html, base64, shutil
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
D={p.stem:yaml.safe_load(p.read_text(encoding='utf-8')) for p in (ROOT/'data').glob('*.yml')}
for p in D['publications']:
    if not p.get('image'):
        raise SystemExit(f"Publication image is required: {p.get('title')}")
    try:
        p['year'] = int(p['year'])
    except (TypeError, ValueError, KeyError):
        raise SystemExit(f"Publication year must be a 4-digit number: {p.get('title')}")

# Any publication year is accepted. The archive is generated dynamically from
# the years that actually exist in data/publications.yml.
PUBLICATION_YEARS = sorted({p['year'] for p in D['publications']}, reverse=True)
CSS=(ROOT/'assets/style.css').read_text(encoding='utf-8')
def img(path,alt=''):
    return f'<img src="{html.escape(path)}" alt="{html.escape(alt)}">'
def head(title,active=''):
    links=[('Home','index.html'),('People','people.html'),('Research','research.html'),('Publications','publications.html'),('Achievements','achievements.html'),('News','news.html'),('Join Us','join.html')]
    nav=''.join(f'<a class="{"active" if n==active else ""}" href="{u}">{n}</a>' for n,u in links)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · BNSL</title><style>{CSS}</style></head><body><header class="site-header"><div class="header"><a class="brand" href="index.html">BNSL</a><nav class="nav">{nav}</nav></div></header>'''
def foot():
    s=D['site'];return f'<footer class="footer"><div class="footer-inner"><strong>BNSL</strong>{s["lab_name"]} · {s["department"]} · {s["university"]} ({s["campus"]})</div></footer></body></html>'
def pagehero(title,text):return f'<section class="page-hero"><div class="page-hero-inner"><div class="eyebrow">BNSL · Yonsei University</div><h1>{title}</h1><p>{text}</p></div></section>'
# home
s=D['site']; r=D['research']; pubs=D['publications']; projs=D['projects']; news=D['news']

def parse_news_date(value):
    text=str(value).strip()
    for fmt in ('%Y.%m.%d','%Y-%m-%d','%Y/%m/%d'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise SystemExit(f'News date must be YYYY.MM.DD, YYYY-MM-DD, or YYYY/MM/DD: {text}')

for n in news:
    if not n.get('title') or not n.get('category') or not n.get('date'):
        raise SystemExit(f'News requires date, category, and title: {n}')
    n['_date_obj']=parse_news_date(n['date'])
news_sorted=sorted(news, key=lambda n:n['_date_obj'], reverse=True)
hl=[]
for p in pubs:
    if p.get('highlight'): hl.append(('Publication',p['title'],p['journal'],p['image']))
for p in projs:
    if p.get('highlight'): hl.append(('Research Project',p['title_en'],p['agency'],None))
<h1>{s['hero_title']}</h1><div class="ko">{s['lab_name']}</div><div class="ko">{s['korean_name']}</div>
for x in r:
    h+=f'<a class="research-card" href="research.html#{x["id"]}">{img(x["image"],x["title"])}<div class="research-overlay"></div><div class="research-copy"><div class="num">{x["number"]}</div><h3>{x["title"]}</h3><p>{x["short"]}</p></div></a>'
h+='</div></section><section class="section"><div class="section-head"><div><div class="label">Selected</div><h2>Highlights</h2></div></div><div class="highlights">'
if hl:
    kind,title,meta,image=hl[0]
    h+=f'<a class="highlight-main" href="publications.html">{img(image,title) if image else ""}<div class="highlight-body"><div class="kicker">{kind}</div><h3>{title}</h3><p>{meta}</p></div></a><div class="highlight-side">'
    for kind,title,meta,image in hl[1:3]: h+=f'<a class="highlight-small" href="research.html"><div class="kicker">{kind}</div><h3>{title}</h3><p>{meta}</p></a>'
    h+='</div>'
h+='</div></section><section class="section"><div class="section-head"><div><div class="label">Updates</div><h2>Recent News</h2></div><a href="news.html">View all news →</a></div><div class="news-grid">'
for i,n in enumerate(news_sorted[:6],1):
    summary=f'<p>{html.escape(str(n["summary"]))}</p>' if n.get('summary') else ''
    h+=f'<a class="news-card news-text-card" href="news.html"><div class="news-card-top"><span class="news-index">{i:02d}</span><span class="news-date">{html.escape(str(n["date"]))}</span></div><div class="news-meta">{html.escape(str(n["category"]))}</div><h3>{html.escape(str(n["title"]))}</h3>{summary}<span class="news-arrow">↗</span></a>'
h+='</div></section><div class="join-strip"><div><h2>Interested in joining BNSL?</h2><p>Graduate students · Undergraduate researchers · Collaborations</p></div><a class="btn" href="join.html">Join BNSL →</a></div></main>'+foot()
(OUT/'index.html').write_text(h,encoding='utf-8')
# research
h=head('Research','Research')+pagehero('Research','Nanophotonics, biomedical optics, sensing, thermal photonics, and optical systems — with projects organized under the research themes they support.')+'<main>'
for x in r:
    h+=f'<section class="research-feature" id="{x["id"]}"><div class="feature-image">{img(x["image"],x["title"])}</div><div class="feature-copy"><div class="num">{x["number"]}</div><h2>{x["title"]}</h2><p>{x["description"]}</p></div></section>'
h+='<section class="section" style="margin-top:75px"><div class="section-head"><div><div class="label">Research & Projects</div><h2>Current Projects</h2></div></div><div class="project-list">'
for p in projs:
    h+=f'<div class="project"><div class="status">{p["status"]}</div><div><h3>{p["title_en"]}</h3><p>{p["title"]}</p><p>{p["agency"]} · {p["period"]}</p></div></div>'
h+='</div></section></main>'+foot();(OUT/'research.html').write_text(h,encoding='utf-8')
# people
pe=D['people'];h=head('People','People')+pagehero('People','Principal Investigator, current members, and alumni of BNSL.')+'<main><section class="section"><div class="pi">'+img(pe['pi']['photo'],pe['pi']['name'])+f'<div><div class="eyebrow">Principal Investigator</div><h2>{pe["pi"]["name"]}</h2><div class="role">{pe["pi"]["title"]}</div><p>{pe["pi"]["department"]}</p><p>{pe["pi"]["bio"]}</p><p><b>Office</b> {pe["pi"]["office"]}<br><b>Email</b> {pe["pi"]["email"]}</p><h3>Education</h3><ul>'+''.join(f'<li>{x}</li>' for x in pe['pi']['education'])+'</ul></div></div></section><section class="section"><div class="section-head"><div><div class="label">Team</div><h2>Current Members</h2></div></div><div class="member-grid">'
for p in pe['current']:
    h+=f'<div class="member">{img(p["photo"],p["name"])}<h3>{p["name"]}</h3><p><b>{p["role"]}</b></p><p>{p["interest"]}</p></div>'
h+='</div></section><section class="section"><div class="section-head"><div><div class="label">Alumni</div><h2>Where they are now</h2></div></div>'
for a in pe['alumni']: h+=f'<div class="alumni-row"><strong>{a["name"]}</strong><span>{a["period"]}</span><span>{a["next"]}</span></div>'
h+='</section></main>'+foot();(OUT/'people.html').write_text(h,encoding='utf-8')
# publications
def publication_metrics(p):
    chips=[]
    if p.get('impact_factor') not in (None, ''):
        chips.append(f'<span class="metric if">IF {html.escape(str(p["impact_factor"]))}</span>')
    if p.get('jcr_percent') not in (None, ''):
        chips.append(f'<span class="metric jcr">JCR {html.escape(str(p["jcr_percent"]))}%</span>')
    if p.get('jcr_category'):
        label=html.escape(str(p['jcr_category']))
        if p.get('jcr_year') not in (None, ''):
            label += f' · {html.escape(str(p["jcr_year"]))}'
        chips.append(f'<span class="metric category">{label}</span>')
    return ''.join(chips)

h=head('Publications','Publications')+pagehero('Publications','Every publication is presented with an image and can store Impact Factor and JCR category/ranking data. Publication years are not limited; any year entered in the data file is automatically grouped and displayed.')+'<main><div class="must-image-note"><b>Archive rule:</b> every publication requires an image. IF and JCR fields are optional, and when provided they are shown automatically. Years are generated from the data itself, so publications before 2021 are handled the same way.</div><div class="pub-tools">'+''.join(f'<span class="chip">{y}</span>' for y in PUBLICATION_YEARS)+'</div>'
for y in PUBLICATION_YEARS:
    h+=f'<h2 class="pub-year">{y}</h2><div class="pub-grid">'
    year_pubs=[x for x in pubs if x['year']==y]
    year_pubs.sort(key=lambda x: str(x.get('date','')), reverse=True)
    for p in year_pubs:
        metrics=publication_metrics(p)
        h+=f'<article class="pub-card">{img(p["image"],p["title"])}<div class="pub-copy"><div class="pub-journal">{html.escape(str(p["journal"]))}</div><h3>{html.escape(str(p["title"]))}</h3><div class="pub-authors">{html.escape(str(p["authors"]))}</div><div class="pub-metrics">{metrics}</div><div class="pub-date">{html.escape(str(p["date"]))}</div><a class="pub-link" href="{html.escape(str(p["url"]))}">VIEW PAPER ↗</a></div></article>'
    h+='</div>'
h+='</main>'+foot();(OUT/'publications.html').write_text(h,encoding='utf-8')
# achievements
ac=D['achievements'];h=head('Achievements','Achievements')+pagehero('Achievements','Patents, awards & honors, and conferences are grouped here so the top navigation stays simple.')+'<main><div class="tabs"><a class="tablink" href="#patents">Patents</a><a class="tablink" href="#awards">Awards & Honors</a><a class="tablink" href="#conferences">Conferences</a></div>'
for key,title in [('patents','Patents'),('awards','Awards & Honors'),('conferences','Conferences')]:
    h+=f'<section id="{key}" class="achievement-section"><h2>{title}</h2>'
    for a in ac[key]:
        if key=='patents': body=f'<h3>{a["title"]}</h3><p>{a["people"]}</p><p>{a["status"]} · {a["number"]}</p>'
        elif key=='awards': body=f'<h3>{a["title"]}</h3><p>{a["recipient"]} · {a["organization"]}</p>'
        else: body=f'<h3>{a["title"]}</h3><p>{a["type"]} · {a["event"]}</p><p>{a["date"]} · {a["location"]}</p>'
        h+=f'<div class="record"><div class="record-year">{a["year"]}</div><div>{body}</div></div>'
    h+='</section>'
h+='</main>'+foot();(OUT/'achievements.html').write_text(h,encoding='utf-8')
# news
h=head('News','News')+pagehero('News','Publications, awards, conferences, people, projects, and lab updates. News is intentionally text-first so the archive stays easy to migrate and maintain.')+'<main>'
news_years=sorted({n['_date_obj'].year for n in news_sorted}, reverse=True)
for y in news_years:
    h+=f'<section class="news-year-section"><h2 class="news-year">{y}</h2><div class="news-list">'
    for n in [x for x in news_sorted if x['_date_obj'].year==y]:
        summary=f'<p class="news-summary">{html.escape(str(n["summary"]))}</p>' if n.get('summary') else ''
        arrow=f'<a class="news-row-arrow" href="{html.escape(str(n["link"]))}">↗</a>' if n.get('link') else '<span class="news-row-arrow muted">—</span>'
        h+=f'<article class="news-row"><div class="news-row-date">{html.escape(str(n["date"]))}</div><div class="news-row-body"><div class="news-meta">{html.escape(str(n["category"]))}</div><h3>{html.escape(str(n["title"]))}</h3>{summary}</div>{arrow}</article>'
    h+='</div></section>'
h+='</main>'+foot();(OUT/'news.html').write_text(h,encoding='utf-8')
# join
h=head('Join Us','Join Us')+pagehero('Join BNSL','We welcome researchers interested in nanophotonics, biomedical optics, optical sensing, imaging systems, and translational photonics.')+'<main><div class="join-grid"><div class="join-card"><h2>Graduate Students</h2><p>Students interested in experimental photonics, nanophotonics, biomedical optical systems, sensing, or radiative cooling are encouraged to get in touch.</p><h2>Undergraduate Researchers</h2><p>Undergraduate research can begin through focused projects in simulation, optical experiments, imaging, sensing, or materials.</p><h2>Collaborations</h2><p>We welcome interdisciplinary collaborations that connect photonics with biomedical engineering and translational applications.</p></div><div class="contact-box"><div class="eyebrow">Contact</div><h2>BNSL · Yonsei University</h2><p><b>Email</b><br>'+s['email']+'</p><p><b>Phone</b><br>'+s['phone']+'</p><p><b>Address</b><br>'+s['address']+'</p></div></div></main>'+foot();(OUT/'join.html').write_text(h,encoding='utf-8')
# copy images
shutil.copytree(ROOT/'assets',OUT/'assets')
