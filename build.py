"""
경기광주 재가복지센터 사이트 빌드

content/posts.json 의 글 중에서 '오늘까지 발행일이 된 글'만 골라 public/ 폴더에 사이트를 만들어요.
발행일 = config.json 의 start_date + 글의 day 값

  python build.py                    # 오늘(한국 시간) 기준으로 빌드
  BUILD_DATE=2026-11-01 python build.py   # 특정 날짜 기준으로 미리보기
"""
import os, re, json, html, shutil, datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'public')
CFG = json.load(open(os.path.join(ROOT, 'config.json'), encoding='utf-8'))
DOMAIN = CFG['domain'].rstrip('/')
if 'YOUR-DOMAIN' in DOMAIN and os.environ.get('GITHUB_REPOSITORY'):
    # 도메인을 아직 안 정했으면 GitHub Pages 기본 주소를 써요 (아이디.github.io/레포이름)
    _owner, _repo = os.environ['GITHUB_REPOSITORY'].split('/')
    DOMAIN = f'https://{_owner.lower()}.github.io/{_repo}'
NAME = CFG['name']
TEL = CFG['tel']
TEL_RAW = re.sub(r'\D', '', TEL)
START = datetime.date.fromisoformat(CFG['start_date'])
TODAY = datetime.date.fromisoformat(os.environ['BUILD_DATE']) if os.environ.get('BUILD_DATE') else datetime.datetime.now(ZoneInfo('Asia/Seoul')).date()

ALL = json.load(open(os.path.join(ROOT, 'content', 'posts.json'), encoding='utf-8'))
for p in ALL:
    p['date'] = START + datetime.timedelta(days=int(p['day']))
POSTS = sorted([p for p in ALL if p['date'] <= TODAY], key=lambda p: (p['date'], -ALL.index(p)), reverse=True)  # 최신 글이 앞
PUB = {p['id'] for p in POSTS}

CATS = [("grade", "등급 신청"), ("money", "비용·지원"), ("service", "서비스 이용"), ("dementia", "치매 돌봄"),
        ("health", "건강·생활"), ("family", "가족 돌봄"), ("policy", "2026 제도"), ("center", "센터 고르기")]
CN = dict(CATS)
ICONS = {
    'grade': '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 14.5l2 2 4-4"/>',
    'money': '<rect x="3" y="6" width="18" height="13" rx="2.5"/><path d="M3 10h18"/><path d="M15.5 14.5h2"/>',
    'service': '<path d="M4 11l8-7 8 7"/><path d="M6 9.5V20h12V9.5"/><path d="M10 20v-5h4v5"/>',
    'dementia': '<path d="M9 18h6"/><path d="M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    'health': '<path d="M12 20s-7.5-4.6-7.5-10.2A4.2 4.2 0 0 1 12 7.3a4.2 4.2 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z"/>',
    'family': '<circle cx="9" cy="8" r="3.2"/><circle cx="17" cy="9.5" r="2.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M15.5 14.6c2.9.2 5.5 2.3 5.5 5.4"/>',
    'policy': '<path d="M4 10v4h3l7.5 4.5v-13L7 10z"/><path d="M18 9a4.2 4.2 0 0 1 0 6"/>',
    'center': '<path d="M12 3l7 3v5.5c0 4.6-3 7.9-7 9.5-4-1.6-7-4.9-7-9.5V6z"/><path d="M9 12l2.2 2.2L15.5 10"/>',
    'search': '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>',
    'list': '<path d="M8 6h12M8 12h12M8 18h12"/><path d="M4 6h.01M4 12h.01M4 18h.01"/>',
}

e = lambda x: html.escape(str(x), quote=True)
ic = lambda k, cls='': f'<svg class="ic{(" " + cls) if cls else ""}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[k]}</svg>'
tone = lambda c: f'--tone:var(--t-{c});--icon:var(--i-{c})'
inl = lambda x: re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', e(x))
dot = lambda d: d.strftime('%Y.%m.%d')
cnt = lambda c: sum(1 for p in POSTS if p['category'] == c)
live_cats = [(c, n) for c, n in CATS if cnt(c)]


def md(src):
    out, ul, tb = [], None, None
    def flush():
        nonlocal ul, tb
        if ul:
            out.append('<ul>' + ''.join(ul) + '</ul>'); ul = None
        if tb:
            h = tb.pop(0)
            out.append('<div class="tw"><table><thead><tr>' + ''.join(f'<th>{inl(c)}</th>' for c in h) + '</tr></thead><tbody>' +
                       ''.join('<tr>' + ''.join(f'<td>{inl(c)}</td>' for c in r) + '</tr>' for r in tb) + '</tbody></table></div>')
            tb = None
    for line in src.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('- '):
            if tb: flush()
            ul = ul or []; ul.append(f'<li>{inl(line[2:])}</li>'); continue
        if line.startswith('| '):
            if ul: flush()
            tb = tb or []; tb.append([c.strip() for c in line.strip('|').split('|')]); continue
        flush()
        if line.startswith('## '):
            out.append(f'<h2>{inl(line[3:])}</h2>')
        elif line.startswith('> '):
            pr = line[2:].split('|', 1)
            out.append(f'<div class="box"><b>{inl(pr[0])}</b>{inl(pr[1] if len(pr) > 1 else "")}</div>')
        else:
            out.append(f'<p>{inl(line)}</p>')
    flush()
    return ''.join(out)


def card(p, base, search=False):
    heads = " ".join(l[3:] for l in p["body"].split("\n") if l.startswith("## "))
    dq = f' data-q="{e(p["title"] + " " + p["summary"] + " " + p["keyword"] + " " + heads)}"' if search else ''
    return (f'<a class="card" href="{base}{p["id"]}.html" style="{tone(p["category"])}" data-c="{p["category"]}"{dq}>'
            f'<div class="thumb"><span class="tc"><i>{ic(p["category"])}</i>{e(CN[p["category"]])}</span><span class="kw">{e(p["keyword"])}</span>{ic(p["category"], "big-ic")}</div>'
            f'<h3>{e(p["title"])}</h3><p>{e(p["summary"])}</p><span class="m">{dot(p["date"])} · {p["minutes"]}분 읽기</span></a>')


FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap">')


def head(title, desc, path, root, kind='website', extra=''):
    url = f'{DOMAIN}/{path}'
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="{e(NAME)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ko_KR">
<meta name="theme-color" content="#1F3B34">
<!-- 네이버 서치어드바이저 / 구글 서치콘솔 소유확인 태그를 여기에 붙여넣기 -->
{FONT}
<link rel="stylesheet" href="{root}assets/style.css">
{extra}
</head>
<body>
'''


def header(root, home=False):
    h = '' if home else root
    return f'''<div class="notice">등급이 없어도 괜찮아요. <b>등급 신청부터 같이 해 드려요.</b></div>
<header class="top">
  <div class="wrap">
    <a class="logo" href="{root or './'}"><i aria-hidden="true"></i>{e(NAME)}</a>
    <nav class="menu" aria-label="주요 메뉴">
      <a href="{h}#service">방문요양</a>
      <a href="{h}#dye">염색 케어</a>
      <a href="{h}#cost">비용</a>
      <a href="{root}info/">요양 정보</a>
      <a href="{h}#faq">자주 묻는 질문</a>
    </nav>
    <a class="tel" href="{h}#contact">상담 신청</a>
  </div>
</header>
'''


def footer(root, home=False):
    h = '' if home else root
    return f'''<footer>
  <div class="wrap">
    <div><b>{e(NAME)}</b> · 경기도 광주 방문요양</div>
    <div>경기도 광주시 (상세 주소) · 대표 ○○○ · 장기요양기관 지정번호 (지정 후 기재) · {TEL}</div>
    <div>등급별 한도와 본인부담률은 2026년 기준이에요. 해마다 바뀔 수 있어요.</div>
  </div>
</footer>
<div class="mbar">
  <a class="btn btn-line" href="tel:{TEL_RAW}">전화하기</a>
  <a class="btn btn-brand" href="{h}#contact">상담 신청</a>
</div>
<script src="{root}assets/main.js" defer></script>
</body>
</html>
'''


def unlink_unpublished(s):
    """아직 발행 안 된 글로 가는 링크는 글자만 남겨요."""
    def fix(m):
        return m.group(0) if m.group(2) in PUB else m.group(3)
    return re.sub(r'<a href="((?:\.\./)?info/)?([a-z0-9-]+)\.html"[^>]*>(.*?)</a>', fix, s)


def write(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)


# ---------- clean output ----------
if os.path.exists(OUT):
    shutil.rmtree(OUT)
shutil.copytree(os.path.join(ROOT, 'static'), OUT)

# ---------- home ----------
home_cards = POSTS[:6]
news = f'''<section class="sec tight" id="news">
    <div class="wrap">
      <div class="sec-h">
        <span class="kicker">요양 정보</span>
        <h2>알고 시작하면<br>훨씬 쉬워요</h2>
        <p>등급 신청, 비용, 치매 돌봄까지. 상담 전화에서 자주 듣는 질문을 매일 한 편씩 정리하고 있어요.</p>
      </div>
      <div class="cats">{''.join(f'<a class="cat" href="info/?cat={c}" style="{tone(c)}"><span class="badge-ic">{ic(c)}</span><b>{n}</b><span>{cnt(c)}개</span></a>' for c, n in live_cats)}</div>
      <div class="cards">{''.join(card(p, 'info/') for p in home_cards)}</div>
      <div class="allbtn"><a class="btn btn-dark" href="info/">요양 정보 {len(POSTS)}개 전체 보기</a></div>
    </div>
  </section>'''
main = open(os.path.join(ROOT, 'src', 'home_main.html'), encoding='utf-8').read()
main = main.replace('{{NEWS}}', news).replace('{{TEL_RAW}}', TEL_RAW).replace('{{TEL}}', TEL)
ld_home = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": NAME,
           "description": "경기도 광주 방문요양 재가센터. 사회복지 20년 경력 센터장이 상담부터 요양보호사 연결까지 직접 맡아요.",
           "url": DOMAIN + "/", "telephone": TEL,
           "address": {"@type": "PostalAddress", "addressRegion": "경기도", "addressLocality": "광주시", "streetAddress": "상세 주소 입력", "addressCountry": "KR"},
           "areaServed": ["경기도 광주시", "오포읍", "초월읍", "곤지암읍", "퇴촌면"], "openingHours": "Mo-Fr 09:00-18:00"}
home = head(f'{NAME} | 경기도 광주 방문요양·재가센터',
            '경기도 광주 방문요양 재가센터. 사회복지 20년 경력 센터장이 등급 신청부터 요양보호사 연결까지 직접 챙겨요. 이용 어르신 월 1회 염색 케어, 2026년 비용 계산기.',
            '', '', extra=f'<script type="application/ld+json">{json.dumps(ld_home, ensure_ascii=False)}</script>')
write('index.html', unlink_unpublished(home + header('', True) + '\n' + main + '\n' + footer('', True)))

# ---------- hub ----------
picks = [p for p in POSTS if p['id'] in ('grade', 'cost', 'compare')]
side = (f'<a href="./" data-c="all" style="{tone("center")}"><span class="bi">{ic("list")}</span>전체<em>{len(POSTS)}</em></a>' +
        ''.join(f'<a href="?cat={c}" data-c="{c}" style="{tone(c)}"><span class="bi">{ic(c)}</span>{n}<em>{cnt(c)}</em></a>' for c, n in live_cats))
hub = head(f'요양 정보 | {NAME}', f'장기요양등급 신청, 방문요양 비용, 치매 돌봄, 가족요양까지. 경기도 광주 재가센터가 2026년 기준으로 정리한 요양 정보.', 'info/', '../')
hub += header('../') + f'''
<main class="hub" id="hub">
  <div class="hub-h">
    <div><span class="kicker">{e(NAME)}</span><h1 style="margin-top:8px">요양 정보</h1><p>장기요양 제도부터 집에서 돌보는 요령까지, 2026년 기준으로 정리했어요.</p></div>
    <label class="hsearch">{ic("search")}<input type="search" id="hubQ" placeholder="궁금한 단어로 검색 (예: 치매, 한도)" aria-label="글 검색"></label>
  </div>
  <div class="hub-b">
    <nav class="side" aria-label="분류">{side}</nav>
    <div class="hub-main">
      {'<section class="picks" id="picks"><h2>처음이라면 이것부터</h2><div class="cards">' + ''.join(card(p, '') for p in picks) + '</div></section>' if picks else '<div id="picks" hidden></div>'}
      <h2 class="lh"><span id="hubHead">전체 글</span> <small id="hubCount">{len(POSTS)}개</small></h2>
      <div class="cards" id="hubCards">{''.join(card(p, '', search=True) for p in POSTS)}</div>
      <div class="more-btn" id="hubMoreWrap" hidden><button type="button" class="btn btn-line" id="hubMore">더 보기</button></div>
      <div class="empty" id="hubEmpty" hidden>찾는 글이 없어요. 다른 단어로 검색해 보거나 <a href="../#contact">상담으로 물어보세요</a>.</div>
    </div>
  </div>
</main>
<script>window.CAT_NAMES={json.dumps(CN, ensure_ascii=False)};</script>
''' + footer('../')
write('info/index.html', hub)

# ---------- posts ----------
chron = list(reversed(POSTS))  # 오래된 글 → 최신 글
for i, p in enumerate(chron):
    prev = chron[i - 1] if i > 0 else None
    nxt = chron[i + 1] if i < len(chron) - 1 else None
    rel = [x for x in POSTS if x['category'] == p['category'] and x is not p][:3]
    if len(rel) < 3:
        rel += [x for x in POSTS if x['category'] != p['category']][:3 - len(rel)]
    c = p['category']
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": p['title'], "description": p['summary'],
           "datePublished": p['date'].isoformat(), "dateModified": p['date'].isoformat(), "inLanguage": "ko",
           "author": {"@type": "Organization", "name": NAME}, "publisher": {"@type": "Organization", "name": NAME},
           "mainEntityOfPage": f'{DOMAIN}/info/{p["id"]}.html'},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "홈", "item": DOMAIN + "/"},
              {"@type": "ListItem", "position": 2, "name": "요양 정보", "item": DOMAIN + "/info/"},
              {"@type": "ListItem", "position": 3, "name": CN[c], "item": f'{DOMAIN}/info/?cat={c}'}]}]
    pg = head(f'{p["title"]} | {NAME}', p['summary'] + ' 경기도 광주 방문요양 재가센터가 2026년 기준으로 정리했어요.',
              f'info/{p["id"]}.html', '../', 'article', f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
    pg += header('../') + f'''
<main>
<article class="post" style="{tone(c)}">
  <nav class="crumb" aria-label="위치"><a href="../">홈</a><span>›</span><a href="./">요양 정보</a><span>›</span><a href="./?cat={c}">{e(CN[c])}</a></nav>
  <span class="post-cat">{ic(c)}{e(CN[c])}</span>
  <h1>{e(p["title"])}</h1>
  <div class="meta">{e(NAME)} · <time datetime="{p["date"].isoformat()}">{dot(p["date"])}</time> · {p["minutes"]}분 읽기</div>
  <div class="sum"><b>한눈에 보기</b><p>{e(p["summary"])}</p></div>
  <div class="pb">{md(p["body"])}</div>
  <div class="cta"><div><p>우리 부모님 경우가 궁금하다면</p><span>경기도 광주 어디든, 센터장이 직접 전화로 알려 드려요.</span></div><a class="btn btn-brand" href="../#contact">상담 신청하기</a></div>
  <div class="pn">{f'<a href="{prev["id"]}.html"><span>← 이전 글</span><b>{e(prev["title"])}</b></a>' if prev else '<span></span>'}{f'<a class="nx" href="{nxt["id"]}.html"><span>다음 글 →</span><b>{e(nxt["title"])}</b></a>' if nxt else ''}</div>
  {f'<section class="related"><h2 style="font-size:19px;font-weight:800;margin-bottom:18px">같이 보면 좋은 글</h2><div class="cards">{"".join(card(x, "") for x in rel)}</div></section>' if rel else ''}
  <p class="src">이 글은 국민건강보험공단, 보건복지부 공개 자료를 바탕으로 2026년 기준으로 정리했어요. 제도는 바뀔 수 있으니 신청 전에 공단(1577-1000)에서 한 번 더 확인하세요.</p>
</article>
</main>
''' + footer('../')
    write(f'info/{p["id"]}.html', pg)

# ---------- sitemap / robots / CNAME ----------
latest = POSTS[0]['date'] if POSTS else TODAY
urls = [(DOMAIN + '/', latest), (DOMAIN + '/info/', latest)] + [(f'{DOMAIN}/info/{p["id"]}.html', p['date']) for p in POSTS]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      ''.join(f'  <url><loc>{u}</loc><lastmod>{d.isoformat()}</lastmod></url>\n' for u, d in urls) + '</urlset>\n')
write('robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n')
host = re.sub(r'^https?://', '', DOMAIN)
if 'YOUR-DOMAIN' not in host and not host.endswith('github.io'):
    write('CNAME', host + '\n')
write('.nojekyll', '')

nxt = min((p for p in ALL if p['date'] > TODAY), key=lambda p: p['date'], default=None)
print(f'[{TODAY}] 발행된 글 {len(POSTS)}/{len(ALL)}편' + (f' · 다음 글: {nxt["date"]} 「{nxt["title"]}」' if nxt else ' · 전부 발행됨'))
