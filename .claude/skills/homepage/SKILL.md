---
name: homepage
description: Maintain the 원주 건강한치과 static homepage (index.html at repo root), its GitHub Pages deployment, custom domain, and related trust/SEO work (Google Search Console, Google Business Profile, Google Ads). Use when the user asks to edit the homepage, fix hero/footer copy, add sections/images to index.html, or touches healthydental.co.kr / GitHub Pages / domain / Google Search Console / Google Ads for this clinic.
---

# 원주 건강한치과 홈페이지

Single static `index.html` at the **repo root** (`D:\OneDrive\Claude_Dental Clinic\index.html`) —
unrelated to the `dental-blog-autopost/` subproject (different skill, different deploy target).
Same GitHub repo (`michelle8107/wonju-healthy-dental`), same git history, but this is plain
static HTML served by **GitHub Pages**, not Vercel.

## File size gotcha — do not use the Read tool on the whole file

All photos (hero, facility, profile, gallery, awards) are inlined as `data:image/...;base64,...`
directly in the HTML — the file is ~2MB. The Read tool will refuse (`exceeds maximum allowed
size/tokens`) on any range that includes one of these lines. Workflow that works:
- Use `Grep`/`grep -n` to find line numbers by text content (headings, known copy) — never grep
  for base64 content itself.
- Use `Edit` with short, unique `old_string`/`new_string` text snippets — this works fine even
  though the file is huge, since Edit does a targeted string replace, not a full read.
- If you need to eyeball structure, make a trimmed copy first:
  `awk '{ if (length($0) > 500) print substr($0,1,500) " ...[TRUNCATED]"; else print }' index.html > trimmed.html`
  then Read the trimmed copy.
- To **add** a new base64 image, don't paste the base64 through the Edit tool's old_string/new_string
  params (burns huge context). Instead write a small Python script that reads the file, finds an
  insertion marker via `content.find(...)`, and splices in a pre-built HTML snippet (with the
  base64 read directly from a `.b64` file on disk) — see git history around 2026-08-31 for the
  exact pattern used to add the "수상 및 인증" (awards) section.

## Visual QA before shipping a copy/layout change

`file://` URLs are blocked by the browser extension's navigation guard. Serve locally instead:
```
python3 -m http.server 8792   # plain http.server sends `Content-Type: text/html` with NO charset,
```
**which makes Chrome mojibake all the Korean text.** Use a tiny custom handler that forces
`text/html; charset=utf-8` (see git history / ask for the snippet) before navigating Chrome to
`http://localhost:PORT/index.html`. Kill the server when done (`pkill -f http.server`).

## Deployment: GitHub Pages + custom domain (set up 2026-08-30/31)

- Pages source: `master` branch, `/` (root) — any push to `master` triggers a rebuild
  (`gh api repos/michelle8107/wonju-healthy-dental/pages/builds/latest` to poll status; wait for
  `"status":"built"` before assuming a change is live — takes ~30-90s).
- Custom domain `healthydental.co.kr` (bought via 가비아): DNS is 4 A records (`185.199.108/109/110/111.153`)
  on host `@`, plus a `CNAME` record `www` → `michelle8107.github.io` — this is the standard
  GitHub Pages apex-domain recipe, not project-specific. Gabia nameserver setting stays default
  ("가비아 네임서버 사용"), since DNS is managed directly in Gabia's own DNS panel.
- The repo has a `CNAME` file at root (auto-created by `gh api -X PUT .../pages -f cname=...`) —
  don't delete it, that's what tells GitHub Pages which custom domain to serve.
- HTTPS: enable via `gh api -X PUT repos/.../pages -F https_enforced=true` (note **-F** not -f,
  it's a boolean not a string — `-f https_enforced=true` fails with a 422 type error). Only do
  this after `https_certificate.state` is `"issued"` or `"approved"` (check via `gh api
  repos/.../pages`) — enabling too early can lock out HTTP visitors before the cert is ready.
- `google<hash>.html` at repo root is the Google Search Console ownership-verification file —
  keep it forever ("확인이 완료된 후에도 파일을 삭제하지 마세요" per Google's own instructions).

## Business/trust facts — verified against the actual 사업자등록증 (2026-08-31)

Source document: `d:\OneDrive\문서\15_사업자등록증(기타)\건강한 치과.jpg`.
- 상호: 건강한치과의원, 대표자: 표경열, 사업자등록번호: **463-96-00295**
- **개업연월일: 2017-03-20** — i.e. this Bangok-dong location has been open ~9 years (as of
  2026), NOT 20 years. The doctor's *total* clinical career (across prior clinics listed in his
  profile: 강남 청담 보스톤치과, 의정부 보스톤치과, 아산 현대치과, 강동 고운美치과) is what adds up
  to ~20 years.
- **Never conflate these two numbers again.** The copy was originally wrong in FOUR places
  (hero lede, hero stat badge, "신뢰의 기록" principle card, and the intro splash screen caption)
  — all said something like "20년째 이 자리에서" (20 years *at this location*), which is a false,
  legally-risky claim under 의료법 과장광고 rules. Correct framing: "20년 경력" (total career) as
  one fact, "반곡동에서 9년째" (or similar, recompute from 2017-03-20 as time passes) as a
  separate fact — never merge them into one "20년째 이 자리" sentence.
- Footer now carries the legally-expected disclosure line (상호·대표자·사업자등록번호·개설일·주소)
  — Korean medical-business sites without this read as "thrown-together marketing site" to a
  skeptical visitor; don't remove it in a future redesign.

## Awards/certificates section (`#awards`, added 2026-08-31)

Real photos of the doctor's actual physical certificates/plaques, sourced from
`assets/screenshots/다운로드 (4).jpg` through `(7).jpg` (unfortunately named — they're a shelf of
frames: DKU 위촉장/감사장, GAO Highly Advanced Prosthetics certificate, 국회의원 표창장, 방사선
안전관리책임자 수료증, and a wide shelf shot). Resize to ~750-1000px wide via ffmpeg before
base64-embedding (originals are ~1280x960 and would otherwise bloat the page further) — this
section added ~300KB to the page even after compression. If more certs get photographed later,
follow the same resize-then-splice-via-Python pattern, don't inflate the file with full-res shots.

## Google services status (as of 2026-08-31)

- **Search Console**: property `https://www.healthydental.co.kr/` verified via HTML-file method
  (the `google<hash>.html` file above). `site:healthydental.co.kr` returned nothing before this —
  brand-new domain, expect real indexing to take days, not minutes.
- **Google Business Profile / Google Ads**: the user started what they described as "구글
  비즈니스 등록" but the actual flow they landed in (headline/description RSA builder, "광고 제목",
  "내용 입력란", budget step ahead) is **Google Ads** (paid, per-click), not the free Google
  Business Profile listing at business.google.com. Flag this distinction again if it comes up —
  don't assume the user knows which product they're in. Ad copy already drafted follows the same
  no-superlative/no-guarantee guardrail as the blog content (see `dental-blog-autopost` skill).
- **Naver 스마트플레이스**: recommended as the actually-highest-impact registration for Korean
  local search ("원주 치과" style queries mostly happen on Naver, not Google) — not yet started as
  of this writing. Higher priority than polishing Google Ads copy if the user asks what to do next.
