#!/usr/bin/env python3
"""치과지식 페이지(knowledge.html) 빌더.

사용법 (저장소 루트에서):  python knowledge/build.py

- knowledge/carousels.json 의 순서(최신순)대로 바둑판 카드를 만든다.
- 각 캐러셀의 원본 PNG(src 폴더)를 knowledge/img/<slug>/NN.jpg 로 변환하고, 표지 썸네일 cover.jpg 를 만든다.
- 헤더·스타일·퀵메뉴·푸터는 index.html 에서 그대로 가져와서 홈페이지와 모양이 항상 같게 유지된다.
  (index.html 의 #앵커 링크는 index.html#앵커 로 바꿔 넣는다.)
새 캐러셀을 올리면 carousels.json 맨 앞에 항목을 추가하고 이 스크립트를 다시 실행하면 된다.
"""
import html
import json
import pathlib
import re

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
KN = ROOT / "knowledge"
IMG = KN / "img"
OUT = ROOT / "knowledge.html"
SITE = "https://healthydental.co.kr"  # www는 apex로 301 리다이렉트된다


def stale(dst, src):
    return not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime


def convert(item):
    src_dir = ROOT / item["src"]
    files = sorted(p for p in src_dir.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
    if not files:
        raise SystemExit(f"슬라이드 이미지가 없습니다: {src_dir}")
    out = IMG / item["slug"]
    out.mkdir(parents=True, exist_ok=True)
    names = []
    for i, p in enumerate(files, 1):
        dst = out / f"{i:02d}.jpg"
        if stale(dst, p):
            Image.open(p).convert("RGB").save(dst, "JPEG", quality=84, optimize=True, progressive=True)
        names.append(dst.name)
    for extra in out.glob("[0-9][0-9].jpg"):
        if extra.name not in names:
            extra.unlink()
    cover = out / "cover.jpg"
    if stale(cover, files[0]):
        im = Image.open(files[0]).convert("RGB")
        im.thumbnail((640, 800), Image.LANCZOS)
        im.save(cover, "JPEG", quality=82, optimize=True, progressive=True)
    return [f"knowledge/img/{item['slug']}/{n}" for n in names]


src = (ROOT / "index.html").read_text(encoding="utf-8")


def block(start, end):
    i = src.index(start)
    return src[i:src.index(end, i) + len(end)]


def relink(s):
    return re.sub(r'href="#([^"]*)"',
                  lambda m: 'href="index.html"' if m.group(1) in ("", "top") else f'href="index.html#{m.group(1)}"', s)


def mark_current(s):
    return s.replace('<a href="knowledge.html">치과지식</a>', '<a href="knowledge.html" aria-current="page">치과지식</a>')


fonts = block('<link rel="preconnect" href="https://fonts.googleapis.com">', 'rel="stylesheet">')
style = block("<style>", "</style>")
header = mark_current(relink(block('<header class="site">', "</header>")))
mobile_js = mark_current(relink(block("<script>\n  // move mobile links", "</script>")))
quick = relink(block('<nav class="quick-menu"', "</nav>"))
quick_js = re.search(r"<script>\s*\(function \(\) \{\s*var menu = document\.querySelector\('\.quick-menu'\).*?</script>",
                     src, re.S).group(0)
footer = relink(block('<footer class="site">', "</footer>"))
if 'href="knowledge.html"' not in header:
    raise SystemExit("index.html 상단 메뉴에 치과지식 링크가 없습니다 — 먼저 추가하세요.")

items = json.loads((KN / "carousels.json").read_text(encoding="utf-8"))
data = {}
cards = []
for it in items:
    slides = convert(it)
    data[it["slug"]] = {"title": it["title"], "instagram": it.get("instagram", ""), "slides": slides}
    e = {k: html.escape(str(v)) for k, v in it.items()}
    n = len(slides)
    cards.append(f"""
      <li class="kn-card" data-cat="{e['category']}">
        <a class="kn-thumb" href="#{e['slug']}" aria-label="{e['title']} 카드뉴스 보기 ({n}장)">
          <img src="knowledge/img/{e['slug']}/cover.jpg" alt="{e['title']} 카드뉴스 표지" width="640" height="800" loading="lazy">
          <span class="kn-count"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><rect x="7" y="7" width="14" height="14" rx="2"/><path d="M3 17V5a2 2 0 0 1 2-2h12"/></svg>{n}장</span>
        </a>
        <div class="kn-meta"><span class="kn-cat">{e['category']}</span><span class="mono">{e['date'].replace('-', '.')}</span></div>
        <h2><a href="#{e['slug']}">{e['title']}</a></h2>
        <p>{e['summary']}</p>
      </li>""")

cats = []
for it in items:
    if it["category"] not in cats:
        cats.append(it["category"])
chips = '<button class="kn-chip" type="button" data-cat="" aria-pressed="true">전체</button>' + "".join(
    f'<button class="kn-chip" type="button" data-cat="{html.escape(c)}" aria-pressed="false">{html.escape(c)}</button>'
    for c in cats)

og_image = f"{SITE}/knowledge/img/{items[0]['slug']}/cover.jpg" if items else ""
data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>치과지식 | 원주 건강한치과</title>
<meta name="description" content="원주 건강한치과가 정리한 치과 상식 카드뉴스 모음 — 임플란트, 소아 진료, 진료 전 확인할 점, 생활 속 치아 관리.">
<link rel="canonical" href="{SITE}/knowledge.html">
<meta property="og:type" content="website">
<meta property="og:title" content="치과지식 | 원주 건강한치과">
<meta property="og:description" content="진료실에서 자주 받는 질문을 카드뉴스로 정리했습니다.">
<meta property="og:url" content="{SITE}/knowledge.html">
<meta property="og:image" content="{og_image}">
<!-- 이 파일은 knowledge/build.py 가 생성합니다. 직접 수정하지 말고 carousels.json 을 고친 뒤 다시 빌드하세요. -->
{fonts}

{style}
<style>
  nav.links a[aria-current="page"], .mobile-panel a[aria-current="page"] {{ color: var(--primary); font-weight: 600; }}

  .kn-hero {{ padding: clamp(2.5rem, 6vw, 4.5rem) 0 clamp(1.25rem, 3vw, 2rem); }}
  .kn-hero h1 {{ font-size: clamp(1.9rem, 4vw, 2.6rem); font-weight: 700; }}
  .kn-hero p {{ margin: 0.9rem 0 0; color: var(--ink-soft); max-width: 60ch; }}

  .kn-filters {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0 0 clamp(1.25rem, 3vw, 2rem); }}
  .kn-chip {{
    font: inherit; font-size: 0.86rem; padding: 0.42rem 0.95rem; border-radius: 999px;
    border: 1px solid var(--line); background: transparent; color: var(--ink-soft); cursor: pointer;
  }}
  .kn-chip:hover {{ border-color: var(--primary); color: var(--primary); }}
  .kn-chip[aria-pressed="true"] {{ background: var(--primary); border-color: var(--primary); color: var(--on-primary); }}

  .kn-grid {{
    list-style: none; margin: 0; padding: 0;
    display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: clamp(1.5rem, 3vw, 2.25rem) clamp(0.75rem, 2vw, 1.5rem);
  }}
  @media (max-width: 860px) {{ .kn-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
  .kn-card {{ min-width: 0; }}
  .kn-thumb {{
    position: relative; display: block; aspect-ratio: 4 / 5; max-width: 100%;
    border-radius: 6px; overflow: hidden; background: var(--surface); box-shadow: var(--shadow);
  }}
  .kn-thumb img {{ width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.3s ease; }}
  .kn-thumb:hover img {{ transform: scale(1.03); }}
  .kn-count {{
    position: absolute; top: 0.6rem; right: 0.6rem; display: inline-flex; align-items: center; gap: 0.3rem;
    background: rgba(8, 14, 20, 0.62); color: #fff; font-size: 0.74rem; font-weight: 600;
    padding: 0.22rem 0.55rem; border-radius: 999px;
  }}
  .kn-meta {{ margin-top: 0.8rem; display: flex; gap: 0.6rem; align-items: center; font-size: 0.76rem; color: var(--ink-faint); }}
  .kn-cat {{ color: var(--primary); font-weight: 600; }}
  .kn-card h2 {{
    font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; font-weight: 700;
    font-size: clamp(0.95rem, 1.6vw, 1.1rem); line-height: 1.45; margin-top: 0.3rem;
  }}
  .kn-card h2 a {{ text-decoration: none; }}
  .kn-card h2 a:hover {{ color: var(--primary); }}
  .kn-card p {{
    margin: 0.45rem 0 0; font-size: 0.88rem; color: var(--ink-soft);
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
  }}
  @media (max-width: 560px) {{ .kn-card p {{ -webkit-line-clamp: 2; font-size: 0.82rem; }} }}

  .kn-note {{
    margin: clamp(2.5rem, 6vw, 4rem) 0 0; padding: 1rem 1.25rem; border-radius: 6px;
    background: var(--surface); color: var(--ink-soft); font-size: 0.86rem;
  }}

  /* 슬라이드 뷰어 — 사이트 테마와 무관하게 항상 어두운 배경 */
  .kv {{
    position: fixed; inset: 0; z-index: 300; display: flex; flex-direction: column;
    background: #070B12; color: #fff;
  }}
  .kv[hidden] {{ display: none; }}
  .kv-top {{ display: flex; align-items: center; gap: 1rem; padding: 0.75rem clamp(1rem, 3vw, 1.5rem); }}
  .kv-title {{ flex: 1; min-width: 0; font-weight: 600; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .kv-counter {{ font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); }}
  .kv-btn {{
    border: 0; cursor: pointer; color: #fff; background: rgba(255, 255, 255, 0.12);
    width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center; flex: none;
  }}
  .kv-btn:hover {{ background: rgba(255, 255, 255, 0.22); }}
  .kv-btn:disabled {{ opacity: 0.25; cursor: default; }}
  .kv-stage {{
    flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center;
    gap: clamp(0.5rem, 2vw, 1.5rem); padding: 0 1rem;
  }}
  .kv-track {{
    width: min(100%, calc((100dvh - 170px) * 0.8)); aspect-ratio: 4 / 5; max-width: 100%;
    display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none;
    border-radius: 6px; overscroll-behavior-x: contain;
  }}
  .kv-track::-webkit-scrollbar {{ display: none; }}
  .kv-track img {{ flex: 0 0 100%; width: 100%; height: 100%; object-fit: contain; scroll-snap-align: center; display: block; }}
  .kv-bottom {{ display: flex; flex-direction: column; align-items: center; gap: 0.6rem; padding: 0.8rem 1rem 1.1rem; }}
  .kv-dots {{ display: flex; gap: 0.45rem; }}
  .kv-dots button {{ width: 8px; height: 8px; padding: 0; border: 0; border-radius: 50%; background: rgba(255, 255, 255, 0.35); cursor: pointer; }}
  .kv-dots button[aria-current="true"] {{ background: #fff; }}
  .kv-ig {{ color: rgba(255, 255, 255, 0.8); font-size: 0.85rem; }}
  @media (max-width: 640px) {{
    .kv-stage .kv-btn {{ display: none; }}
    .kv-track {{ width: min(100%, calc((100dvh - 150px) * 0.8)); }}
  }}
</style>
</head>
<body>

{header}

{mobile_js}

<main id="top">
  <section class="kn-hero">
    <div class="wrap">
      <span class="eyebrow">Dental Knowledge · 치과 상식</span>
      <h1>치과지식</h1>
      <p>진료실에서 자주 받는 질문을 카드뉴스로 정리했습니다. 표지를 누르면 한 장씩 넘겨보실 수 있어요.</p>
    </div>
  </section>

  <section class="kn-list">
    <div class="wrap">
      <div class="kn-filters" role="group" aria-label="주제별 보기">{chips}</div>
      <ul class="kn-grid">{''.join(cards)}
      </ul>
      <p class="kn-note">이 페이지의 내용은 일반적인 구강 건강 정보이며, 필요한 진료는 개인의 상태에 따라 달라질 수 있습니다.
      정확한 진단은 내원 후 상담을 통해 받으실 수 있습니다.</p>
    </div>
  </section>
</main>

<div class="kv" id="kv" hidden role="dialog" aria-modal="true" aria-labelledby="kv-title">
  <div class="kv-top">
    <span class="kv-title" id="kv-title"></span>
    <span class="kv-counter mono" id="kv-counter"></span>
    <button class="kv-btn" type="button" id="kv-close" aria-label="닫기">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </button>
  </div>
  <div class="kv-stage" id="kv-stage">
    <button class="kv-btn" type="button" id="kv-prev" aria-label="이전 장">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M15 5l-7 7 7 7"/></svg>
    </button>
    <div class="kv-track" id="kv-track"></div>
    <button class="kv-btn" type="button" id="kv-next" aria-label="다음 장">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M9 5l7 7-7 7"/></svg>
    </button>
  </div>
  <div class="kv-bottom">
    <div class="kv-dots" id="kv-dots"></div>
    <a class="kv-ig" id="kv-ig" target="_blank" rel="noopener">인스타그램에서 보기 ↗</a>
  </div>
</div>

{quick}

{footer}

{quick_js}
<script>
  (function () {{
    var DATA = {data_json};
    var kv = document.getElementById('kv');
    var track = document.getElementById('kv-track');
    var dots = document.getElementById('kv-dots');
    var counter = document.getElementById('kv-counter');
    var prev = document.getElementById('kv-prev');
    var next = document.getElementById('kv-next');
    var ig = document.getElementById('kv-ig');
    var current = null, index = 0, openedByNav = false, lastFocus = null;
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function render(slug) {{
      var c = DATA[slug];
      current = slug;
      index = 0;
      document.getElementById('kv-title').textContent = c.title;
      track.innerHTML = c.slides.map(function (src, i) {{
        return '<img src="' + src + '" alt="' + c.title.replace(/"/g, '&quot;') + ' ' + (i + 1) + '/' + c.slides.length + '"' +
               (i > 1 ? ' loading="lazy"' : '') + ' draggable="false">';
      }}).join('');
      dots.innerHTML = c.slides.map(function (_, i) {{
        return '<button type="button" aria-label="' + (i + 1) + '번째 장"></button>';
      }}).join('');
      Array.prototype.forEach.call(dots.children, function (b, i) {{
        b.addEventListener('click', function () {{ go(i); }});
      }});
      if (c.instagram) {{ ig.href = c.instagram; ig.hidden = false; }} else {{ ig.hidden = true; }}
      if (kv.hidden) {{ lastFocus = document.activeElement; }}
      kv.hidden = false;
      document.body.style.overflow = 'hidden';
      track.scrollLeft = 0;
      update();
      document.getElementById('kv-close').focus();
    }}

    function update() {{
      var n = DATA[current].slides.length;
      counter.textContent = (index + 1) + ' / ' + n;
      prev.disabled = index === 0;
      next.disabled = index === n - 1;
      Array.prototype.forEach.call(dots.children, function (b, i) {{
        b.setAttribute('aria-current', i === index ? 'true' : 'false');
      }});
    }}

    function go(i) {{
      var n = DATA[current].slides.length;
      i = Math.max(0, Math.min(n - 1, i));
      track.scrollTo({{ left: i * track.clientWidth, behavior: reduceMotion ? 'auto' : 'smooth' }});
    }}

    function hide() {{
      kv.hidden = true;
      current = null;
      document.body.style.overflow = '';
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }}

    function close() {{
      if (openedByNav) {{ history.back(); }}
      else {{ hide(); history.replaceState(null, '', location.pathname + location.search); }}
    }}

    track.addEventListener('scroll', function () {{
      if (!current) return;
      var i = Math.round(track.scrollLeft / track.clientWidth);
      if (i !== index) {{ index = i; update(); }}
    }}, {{ passive: true }});

    prev.addEventListener('click', function () {{ go(index - 1); }});
    next.addEventListener('click', function () {{ go(index + 1); }});
    document.getElementById('kv-close').addEventListener('click', close);
    document.getElementById('kv-stage').addEventListener('click', function (e) {{
      if (e.target === this) close();
    }});
    document.addEventListener('keydown', function (e) {{
      if (kv.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') go(index - 1);
      else if (e.key === 'ArrowRight') go(index + 1);
    }});
    window.addEventListener('resize', function () {{
      if (current) track.scrollLeft = index * track.clientWidth;
    }});

    function fromHash() {{
      var slug = decodeURIComponent(location.hash.slice(1));
      if (DATA[slug]) {{ render(slug); }}
      else if (!kv.hidden) {{ hide(); }}
    }}
    window.addEventListener('hashchange', function () {{ openedByNav = true; fromHash(); if (kv.hidden) openedByNav = false; }});
    fromHash();

    var chips = document.querySelectorAll('.kn-chip');
    var cards = document.querySelectorAll('.kn-card');
    Array.prototype.forEach.call(chips, function (chip) {{
      chip.addEventListener('click', function () {{
        var cat = chip.getAttribute('data-cat');
        Array.prototype.forEach.call(chips, function (c) {{ c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); }});
        Array.prototype.forEach.call(cards, function (card) {{ card.hidden = !!cat && card.getAttribute('data-cat') !== cat; }});
      }});
    }});
  }})();
</script>
</body>
</html>
"""

OUT.write_text(page, encoding="utf-8", newline="\n")
total = sum(len(v["slides"]) for v in data.values())
print(f"knowledge.html 생성 완료: 캐러셀 {len(items)}개, 슬라이드 {total}장, {OUT.stat().st_size / 1024:.0f}KB")
