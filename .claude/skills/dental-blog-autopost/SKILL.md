---
name: dental-blog-autopost
description: Maintain/extend the 원주 건강한치과 Blogger auto-posting worker AND the Instagram/Threads publishing scripts, all living in the dental-blog-autopost/ subproject. Use when the user asks about the dental blog automation, uploading a 건치 쇼츠 episode to Instagram/Threads, changing posting schedule/topics/guardrails/hashtags, debugging why a post didn't publish, or rotating credentials.
---

## Standing rule: every new 건치 쇼츠 episode goes to Instagram + Blogger

Per the user's explicit instruction (2026-08-28): whenever a new episode is finished (see the
`geonchi-shorts` skill for production), it gets uploaded to **Instagram + Google Blogger**.
**Naver Blog is now half-automated** (added 2026-09-05, see "Naver Blog drafts" below): still no
posting API, but a Playwright script fills the 스마트에디터 ONE and saves a **임시저장 draft**;
the user reviews and hits 발행 manually. Kakao Channel still gets manual copy-paste text only —
write the post text with photo-placement markers like `[사진: ...]`, don't attempt to automate it.

- **Naming: never say "소아치과" (implies a specialist pediatric-dentistry designation this
  clinic doesn't hold) — use "소아 진료" instead**, everywhere (post titles, labels, body text).
  Corrected 2026-08-29 after it slipped into a published post's title/label/banner.
- **Naming: the on-screen mascot is always called 건치 in copy/captions/blog text, never
  토순이** (corrected 2026-08-28 — 토순이 was this assistant's placeholder name, never the
  user's; even though the character model is visually a rabbit, the series title "건치의 하루"
  makes 건치 the character's actual name everywhere it's referred to in writing).
- **의료광고법: 발행 전 매번 자가검토하고, 무엇을 확인했는지 사용자에게 보고할 것**
  (2026-09-08 사용자 명시 지시: "의료광고법 저촉되는지 항상 신경써줘"). 블로그·캐러셀·릴스 캡션 등
  병원 이름으로 나가는 모든 콘텐츠에 적용된다. 자동 생성 경로는 `lib/anthropic.ts`의 `GUARDRAILS`가
  막아주지만, **캐러셀·수동 블로그 글은 사람이 쓰므로 같은 기준을 손으로 적용**해야 한다.
  금지: 효과 보장·성공률, 치료 전후 비교, 환자 후기/체험담(창작 포함), 가격·할인·이벤트,
  최상급(최고/1위/유일), 특정 시술이 항상 우월하다는 단정, 환자 유인성 표현.
  권장: 부작용·한계 명시, "정확한 진단은 내원 후 상담" 마무리. 원장 본인의 임상 경험 서술은
  후기가 아니라 저자 목소리라 허용. 경력·자격은 사실이고 검증 가능하면 기재 가능 —
  다만 약력의 "임플란트 1만례 수술 기념패 수여"는 심의에서 '인증/보증'으로 읽힐 여지가 가장 큰
  문구라고 사용자에게 한 번 안내해 뒀다(2026-09-08). 사용자가 빼자고 하면 전체 글에 일괄 반영할 것.
- **발행 리듬(2026-09-08 사용자 지시): 건치 에피소드 영상 → 치과 상식 콘텐츠(캐러셀) → 건치 영상 →
  ... 번갈아 올린다.** 같은 종류를 연달아 올리지 않는다. 대기 중인 캐러셀이 있어도 다음 건치
  에피소드가 먼저 나가야 하므로, "이거 올릴까요?"를 묻기 전에 마지막 게시물이 뭐였는지부터 확인할 것.
- **Instagram caption**: never include `#토순이` — the user explicitly asked for it excluded.
  Confirmed hashtag set (2026-08-28): `#건치의하루 #원주치과 #원주임플란트 #반곡동치과
  #치과검진 #스케일링 #치과`. Use this set (swap in whatever specific service the episode is
  about if not implant-related) rather than improvising a new mix each time.

**Threads: scoped in, then explicitly canceled the same day (2026-08-28).** A Meta app
(`THREADS_APP_ID`/`THREADS_APP_SECRET`) exists and is saved in `.env.local`, but the user said
"쓰레드는 하지말자" (let's not do Threads) before OAuth/publishing was ever completed — likely
because of the "Tech Provider Verification" uncertainty documented below. Don't resume this
work unless the user explicitly asks again; if they do, the section further down still has
everything needed to pick back up.

# 원주 건강한치과 Blogger 자동 포스팅

Code lives in `dental-blog-autopost/` — a Next.js (App Router, API-routes-only) subproject inside
this same repo, deployed as its **own separate Vercel project** with Root Directory set to
`dental-blog-autopost`. It is unrelated to the static homepage (`index.html`) at repo root; both
just happen to share one git repo/GitHub remote (`michelle8107/wonju-healthy-dental`).

## What it does

Vercel Cron hits `GET /api/cron/generate-post` on a schedule (`vercel.json`, currently
Mon/Thu 09:00 KST = `0 0 * * 1,4` UTC) with `Authorization: Bearer $CRON_SECRET` (Vercel adds
this header automatically for cron-triggered requests — that's also why the route uses `GET`,
not `POST`). The handler:

1. Rejects anything without the correct `CRON_SECRET` (401) — this is the only thing stopping
   randoms from POSTing spam to the blog via this URL.
2. Reads recent post topics from Upstash Redis (`lib/redis.ts`, `dental-blog:recent-topics`,
   last 30) so the model doesn't repeat itself.
3. Calls Claude Sonnet 5 (`lib/anthropic.ts`, structured output via `zodOutputFormat` —
   requires `@anthropic-ai/sdk` >=0.100ish and `zod` v4, see gotcha below) to write a title +
   HTML body + labels, picking a category not in the recent-topics list.
4. Publishes straight to Blogger (`lib/blogger.ts`, `isDraft: false` — **no human review step,
   this was an explicit user decision**, not an oversight).
5. Appends the topic to Redis history.

**No draft/review gate exists on purpose.** If the user ever asks to add one, that's a real
scope change (switch `isDraft` to `true` and stop there, or add a second "publish" endpoint) —
don't just do it silently, confirm which behavior they want.

## Guardrails baked into the system prompt (`lib/anthropic.ts` `GUARDRAILS` const)

No efficacy guarantees, no before/after comparisons, no patient testimonial quotes (real or
fabricated), no discount/event promotion, no superlatives ("최고"/"1위"/"유일"), no diagnostic
language standing in for an actual dentist — always close with "정확한 진단은 방문 후 상담"-style
language. This exists because the user explicitly acknowledged and accepted 의료광고법 risk in
exchange for zero-review automation, on the condition that obvious violations are prompt-guarded.
**Don't relax this list without the user explicitly asking to relax it.**

Topic rotation categories live in the `TOPIC_CATEGORIES` array in the same file — add/remove
categories there, not by editing the prompt string directly.

## Env vars (`.env.example` is the source of truth — keep it in sync with any new var)

`ANTHROPIC_API_KEY`, `BLOGGER_CLIENT_ID`, `BLOGGER_CLIENT_SECRET`, `BLOGGER_REFRESH_TOKEN`,
`BLOGGER_BLOG_ID`, `KV_REST_API_URL`, `KV_REST_API_TOKEN` (Upstash via Vercel Marketplace —
keep the `KV_REST_API_*` naming even though it's Upstash, not Vercel KV — that's just what the
Marketplace integration injects), `CRON_SECRET`.

None of these are ever in git — `.gitignore` excludes all `.env*` except `.env.example`
(which ships with empty values only). If a rotation is needed (leaked key, revoked OAuth grant),
update the value directly in the Vercel project's Environment Variables — nothing else to touch.

## Getting a new BLOGGER_REFRESH_TOKEN

**확인됨 (2026-09-08): OAuth 동의화면이 "테스트(Testing)" 상태라 refresh token이 7일마다 만료된다.**
예전 주석의 "테스트 모드 토큰은 무기한 괜찮을 것"이라는 추측은 틀렸다 — 8/28 발급된 토큰이 9/4에
만료돼 **9/3 이후 크론이 전부 조용히 실패**했고(블로그에 새 글 0건), 아무 알림도 뜨지 않았다.

**증상 판별.** 발행 스크립트가 Blogger에서 `401 Invalid Credentials`를 뱉으면 access token이 아니라
refresh 단계가 죽은 것이다. 토큰 교환을 직접 때려보면 `400 invalid_grant: Token has been expired or
revoked`가 나온다. 크론이 도는지 확인하려면 공개 피드가 제일 빠르다:
`curl -s "https://healthydentalwonju.blogspot.com/feeds/posts/summary?alt=json&max-results=5"`
— 최근 월/목에 글이 없으면 이 문제다.

**복구 절차 (전부 해야 함 — 하나라도 빠지면 크론은 계속 죽어 있다):**
1. `node --env-file=.env.local scripts/get-refresh-token.mjs` (백그라운드로 띄우고 출력의 승인 URL을
   사용자에게 전달 — 사용자가 브라우저에서 승인하면 스크립트가 자동으로 토큰을 받아 출력한다).
   블로그를 관리하는 구글 계정으로 승인해야 한다.
2. `.env.local`의 `BLOGGER_REFRESH_TOKEN` 교체 → 토큰 refresh가 200 나오는지 먼저 확인.
3. **Vercel 환경변수 교체**: `vercel env rm BLOGGER_REFRESH_TOKEN production --yes` 후
   `printf '<token>' | vercel env add BLOGGER_REFRESH_TOKEN production`.
   (이 변수는 production에만 등록돼 있다 — preview/development에는 없어서 rm이 "not found"를 낸다.)
4. **반드시 재배포**: `vercel deploy --prod --yes`. 환경변수만 바꾸면 기존 배포는 옛 값을 계속 쓴다.
   이 단계를 빼먹는 게 가장 흔한 실수다.
5. `vercel crons ls`로 `/api/cron/generate-post` `0 0 * * 1,4`가 그대로인지 확인.

**근본 해결 (아직 미완료 — 사용자가 직접 해야 함).** Google Cloud Console → API 및 서비스 →
OAuth 동의 화면에서 **"앱 게시" / 프로덕션으로 전환**. blogger 스코프는 민감 스코프가 아니라
Google 심사 없이 즉시 전환되고, 전환 후에는 refresh token이 만료되지 않는다. 2026-09-08에 안내했고
사용자가 아직 전환하지 않았다면 **약 9/15경 또 만료된다** — 다음 세션에서 먼저 확인할 것.

## Known SDK gotcha (hit once already, worth not re-discovering)

`package.json` pins `@anthropic-ai/sdk` with `^0.122.0`, not `^0.68.x` — a `^0.68.0` range
caret-locks to `<0.69.0` (0.x semver rules) and resolves to a version *without*
`zodOutputFormat`/`messages.parse` structured-output support, which lives at the non-beta path
`@anthropic-ai/sdk/helpers/zod` only from around 0.100+. Also: that helper expects **zod v4**
types (`zod/v4` internally) — `zod` must be pinned `^4.x`, not `^3.x`, or `tsc` fails with
"missing properties from type ZodType" even though everything *looks* like a normal zod schema.

## Blog companion post for each 건치 쇼츠 episode (not the same thing as the twice-weekly cron)

The Vercel Cron (`app/api/cron/generate-post/route.ts`) writes its own independent rotating-topic
posts — it has no idea a video episode exists. When "올려야지"-ing an episode's *own* blog post
(what the user actually wants per-episode, not the generic cron content), do this manually:

1. Extract 3-4 clean frames from the episode's vertical video with ffmpeg at key beats (one per
   caption/scene change reads well).
2. Upload the frames AND the video file itself to the same public **Vercel Blob** store used for
   Instagram (`scripts/upload-blog-images.mjs <dir>` for images; the video can reuse the same
   Blob URL already produced by `publish-instagram.mjs` if that ran first — check it's still
   live with a HEAD request rather than re-uploading).
3. Write the post as HTML: intro hook → `<video controls poster="...">` embed (Blogger has no
   native video-upload via the API, only HTML content, so a public Blob URL in a plain `<video>`
   tag is the way) → screenshots with captions interleaved with real dental knowledge tied to
   the episode's theme (not just a video description — actual informative content, so it reads
   as a real article and ranks for the topic) → a closing paragraph naming 원주/원주치과 and
   whatever service the episode's theme naturally bridges to (진료 종류에 맞는 로컬 SEO 키워드,
   e.g. 원주임플란트 for anything implant-adjacent, 원주치과추천/정기검진/스케일링 generally).
   Reference example: `scripts/geonchi1-post.html`.
   **Blob 파일명 충돌 주의:** `upload-blog-images.mjs`는 `blog/<파일명>`에 랜덤 접미사 없이 올린다.
   6탄 글이 `blog/01.jpg`~`04.jpg`를 쓰고 있으므로 같은 이름으로 올리면 이전 글 이미지를 덮거나
   업로드가 실패한다. 에피소드별 접두사를 붙일 것(7탄부터 `ep7_01.jpg` 식).
4. Publish with `scripts/publish-geonchi-post.mjs <html-file> "<title>" "label1,label2"` — this
   appends the same `CLINIC_FOOTER` as the cron path (duplicated inline since scripts/ can't
   import the Next.js `lib/blogger.ts` — keep both copies in sync if the footer ever changes).
   **The footer is in THREE places: `lib/blogger.ts`, `scripts/publish-geonchi-post.mjs`,
   `scripts/update-geonchi-post.mjs`** (+ a style-less Naver variant in `naver-blog-core.mjs`).
   Changing `lib/blogger.ts` only reaches the cron after `vercel deploy --prod --yes`.
   **카카오톡 상담 버튼 (2026-09-11 사용자 요청):** 푸터 맨 위에 노란 `#FEE500` 버튼
   "카카오톡으로 상담 문의하기" → `https://pf.kakao.com/_YCjxaX/chat` (홈페이지 퀵메뉴와 같은
   채널; http는 308로 https에 리다이렉트되므로 https로 씀). 인라인 SVG 말풍선 아이콘 포함.
   9/11 이전에 발행된 글에는 없다 — 소급 적용은 사용자가 원할 때만.

## One-off manual blog posts ("치과 관련 글 하나 더 써줘" — not tied to an episode or the cron)

Same publishing mechanism as the episode companion posts above (`scripts/publish-geonchi-post.mjs
<html-file> "<title>" "labels"` — the script name is historical, it's a generic "publish an HTML
post with the clinic footer" tool, not episode-specific), just without the video/screenshots.
Two established voices — pick based on what the user asks for (default to the teal-banner
clinical voice unless they ask for the personal one, or the topic is patient-facing/anxiety-
driven like this 치석 example):

**Clinical/expert voice** (see `scripts/implant-guide-post.html`, `scripts/gum-health-post.html`,
`scripts/implant-prosthesis-post.html`):
teal header banner div, numbered/bulleted sections, a comparison table where it fits the topic,
closing with 표경열 원장's real credentials for E-E-A-T, then the standard "정확한 진단은 상담 후"
close. No mascot, no casual voice — deliberately more clinical/expert than the episode posts.

**Personal 1인칭 voice** (added 2026-09-02, see `scripts/tartar-guide-post.html` — 치석 article,
and `scripts/sensitive-teeth-post.html` — 시린 이 article, 2026-09-08):
user asked for posts that read "진짜 손으로 쓴글처럼" (like something the doctor genuinely wrote
by hand), opening with a specific spoken-style pattern: "안녕하세요, 원주에서 치과를 진료하고
있는 치과의사 표경열입니다." → "환자분들께서 가장 많이 문의주시는 부분 중 하나가 '[주제]'입니다."
→ a line or two of the kind of question patients actually ask → "그래서 오늘은 [주제]에 대해
이야기해볼까 합니다." No teal banner box (drop it entirely for this voice — just a small name
byline + plain h2 title, since a big corporate box undercuts the "handwritten" feel); h3
section headers keep the teal left-border style for scannability, but body prose stays warm,
first-person, 해요체/합니다 conversational mix — not bullet-heavy corporate copy. Close with a
first-person wind-down paragraph (not a generic CTA) plus a line steering toward in-person
confirmation ("정확한 상태는 내원하셔서 확인받아보시길 권해드려요" or similar, in the same
voice) before the credentials box. Same guardrails apply regardless of voice (no efficacy
promises, no before/after, no testimonials, no discounts) — the doctor's own first-person
clinical-experience commentary ("여러 사례를 진료해 온 경험에 비추어 보면...") is fine and is
not a testimonial, since it's the author's voice, not a quoted patient.

**전문가용 콘텐츠를 환자용으로 옮겨 쓰는 패턴 (2026-09-08).** 사용자가 동종업계용 인스타 릴스
(예: @alchada3355의 "임플란트 보철 SCRP" 설명)를 보내며 "이런 내용도 좋다"고 하는 경우가 있다.
그대로 옮기지 말고 **환자가 읽을 수 있는 언어로 다시 쓸 것** — 사용자가 명시적으로 확인해준 방향이다.
약어(SCRP 등)는 한 번 풀어주되 완전히 숨기지는 않고, "내 임플란트는 어떻게 되어 있나"처럼
환자 관점의 질문으로 프레이밍한다. 원장 약력(임플란트 1만례·임상외래교수)과 붙어 E-E-A-T에 유리해서
이런 소재는 적극적으로 받아도 된다. 같은 내용을 블로그 글 + 캐러셀 양쪽으로 내는 것이 기본 패턴.

**After publishing, push the topic onto the Redis history** (`lpush dental-blog:recent-topics
"<short topic label>"` via the same REST pattern used elsewhere) even though this wasn't the
cron that wrote it — otherwise the cron may independently pick the same topic soon after and
duplicate it. The cron only knows what's in that list, not what a human/manual session already
published.

**Label pool (confirmed 2026-08-28)** — pick 3-6 per post from here rather than improvising a new
mix each time, and don't dump all 30 on one post (looks spammy, dilutes SEO signal):
- 브랜드: `원주건강한치과` `건치의하루` `표경열원장`
- 지역: `원주치과` `원주치과추천` `반곡동치과` `원주임플란트` `강원원주치과`
  `국민건강보험공단치과` `원주스케일링` `원주교정치과` `원주소아진료` `원주사랑니`
- 진료/시술: `임플란트` `스케일링` `신경치료` `심미보철` `라미네이트` `치아미백` `잇몸치료`
  `치주치료` `사랑니발치` `충치치료`
- 정보/증상: `치아건강` `구강건강` `치과검진` `정기검진` `잇몸출혈` `시린이` `충치예방`

**Blogger CCL (Creative Commons) setting: leave it unchecked/off.** Confirmed with the user
2026-08-28 — this is a local-SEO/GEO-visibility content strategy, not a share-and-remix blog;
CC-licensing would just make it legal for other sites to republish the content verbatim, diluting
uniqueness rather than helping. Default copyright (all rights reserved) is correct here.

## Naver Blog drafts (Playwright, added 2026-09-05)

Naver has **no blog-writing API** (the old 오픈API 글쓰기 is gone), so this works the same way the
user's Tistory pipeline does: drive a real Chrome with Playwright, fill 스마트에디터 ONE, and stop
at **임시저장**. Publishing stays manual — the user reviews the draft in Naver and hits 발행.

Blog: `blog.naver.com/healthy2275` (the ID is in `index.html`'s footer link, and in
`scripts/naver-blog-config.json`).

| 단계 | 자동/수동 |
| --- | --- |
| 제목·본문(HTML 붙여넣기)·태그 입력 | 자동 |
| 임시저장 | 자동 |
| 발행(공개) | 사용자 수동 |
| 네이버 로그인 | 최초 1회 수동 (크롬 창에서) |

**Files**
- `scripts/naver-blog-core.mjs` — launch/login/frame/fill 공용 모듈. 셀렉터 후보 목록이 여기 있다.
- `scripts/naver-blog-draft.mjs` — 한 편. `node scripts/naver-blog-draft.mjs <html> "<제목>" "태그1,태그2"`
- `scripts/naver-blog-backfill.mjs` — 여러 편 1세션. `node scripts/naver-blog-backfill.mjs scripts/naver-backfill-manifest.json --delay 5`
- `scripts/naver-blog-config.json` — blogId, 프로필 경로, 셀렉터 override
- `scripts/naver-backfill-manifest.json` — 기존 정보성 글 8편(파일/제목/태그). 건치 에피소드 글은
  유튜브 iframe이 붙여넣기에서 날아가므로 **일부러 제외**했다 — 그건 영상 링크를 에디터에서 직접 붙여야 한다.
- npm 스크립트: `npm run naver-draft -- ...`, `npm run naver-backfill -- ...`

옵션: `--inspect`(입력 없이 DOM 진단만) · `--keep-open`(끝나도 창 유지) · `--timeout N`(로그인 대기 초,
기본 300) · `--publish`(임시저장 대신 발행까지 — 기본 아님, 명시할 때만)

**How the body gets in.** 스마트에디터 ONE은 내부 문서 모델이 따로 있어서 `innerHTML` 주입을
무시한다. 그래서 클립보드에 `text/html`을 써넣고 `Ctrl+V` — 에디터의 붙여넣기 핸들러가 자기
컴포넌트로 변환한다. 클립보드 권한이 막히면 평문 타이핑으로 자동 폴백한다. **inline style은
네이버가 대부분 버리므로** Blogger용 HTML의 teal 배너/표 서식은 그대로 살아오지 않는다 —
초안에서 사용자가 다듬는 걸 전제로 한 파이프라인이다. 병원 정보 푸터도 이 때문에 네이버용으로
태그를 최소화한 별도 버전(`CLINIC_FOOTER` in `naver-blog-core.mjs`)을 쓴다.

**운영 함정**
1. **`.naver-profile/`에 네이버 로그인 세션이 들어있다 — .gitignore 필수** (이미 넣어둠).
   `.naver-shots/`(스크린샷)도 같이 무시된다.
2. **배치는 반드시 `naver-blog-backfill.mjs`로 1세션에 몰아서.** 편마다 스크립트를 새로 띄우면
   매번 로그인/캡차를 만난다. 백필은 2편째부터 글쓰기 URL을 다시 열어 이전 본문이 안 섞이게 한다.
3. **"작성 중인 글 불러오기" 팝업은 항상 취소**(`dismissPopups`) — 안 그러면 이전 편 본문 위에 덮어쓴다.
4. **임시저장 개수는 에디터 상단 "저장 N" 카운터로 확인.** 블로그 글 목록에는 발행글만 보인다.
5. **셀렉터가 깨지면 `--inspect`.** 스마트에디터 ONE 클래스명엔 해시가 붙어(`save_btn__xxxxx`)
   배포마다 바뀐다. 스크립트는 해시 없는 부분일치(`[class*='save_btn']`)를 먼저 쓰고, 그래도 안 되면
   `--inspect` 출력의 실제 클래스를 `naver-blog-config.json`의 `selectors`에 넣어 덮어쓴다.
6. 네이버는 자동화 브라우저를 감지한다. 실제 크롬(`channel: "chrome"`) +
   `--disable-blink-features=AutomationControlled`로 완화했지만, 캡차가 뜨면 사용자가 창에서 직접 푼다.

**Status (2026-09-05):** 스크립트/설정/매니페스트 작성 완료, 브라우저 실행–URL 이동–로그인 감지까지
스모크 테스트 통과. **로그인 이후 구간(제목/본문/태그/저장 셀렉터)은 아직 실사용 검증 전** —
첫 실행은 반드시 `--inspect --keep-open`으로 돌려 셀렉터를 확인하고, 어긋나면 config에 override할 것.

## Instagram publishing (Reels)

`scripts/publish-instagram.mjs <video-path> "<caption>"` — run locally with
`node --env-file=.env.local scripts/publish-instagram.mjs ...`. Uploads the local mp4 to a
**Vercel Blob** store (`dental-blog-media`, public access — Instagram fetches the video from a
public URL, it can't take a local file or an authenticated one) and publishes it as a Reel via
`graph.instagram.com`. No draft/review step exists for Reels — `media_publish` makes it live on
the real account immediately, unlike Blogger which at least has `isDraft`. Always confirm with
the user which video + caption before running this.

**Auth flow used** (Instagram API with Instagram Login, not the older Facebook-Page-login flow):
account must be a Business/Creator professional account connected to a Facebook Page; Meta app
must be Business-type with the Instagram product added. `IG_APP_ID`/`IG_APP_SECRET` here are the
**Instagram-specific** app ID/secret (from the app's Instagram → API setup page), which are
**different** from the top-level Facebook App ID/Secret (App Settings → Basic) — don't confuse
the two, we already did once. OAuth authorize/redirect **must use `https://`, even for
localhost** — `http://localhost:.../oauth2callback` gets `Invalid redirect_uri` outright, unlike
Google's Desktop-app convenience which tolerated `http`. The exact redirect URI must also be
registered byte-for-byte in the app's Instagram API setup page. Auth codes expire fast — if
`get-instagram-token.mjs`'s exchange returns "Invalid authorization code", it's very likely
staleness from delay, not a config problem; just redo the approval and exchange within seconds.

**"API access blocked" (OAuthException code 200) — seen once, 2026-08-30, resolved by itself /
user action outside our control.** A day after episode 1 published fine, both the refresh call
and a plain `/me` lookup with the stored token started returning `{"error":{"message":"API
access blocked.","code":200}}` — not a token-expiry error, the whole app/account was blocked.
Nothing on our end fixed it; the user said "다시 연결했어" (reconnected) after checking the Meta
dashboard / Instagram app / Facebook Business account for a restriction notice, and the exact
same stored token started working again minutes later with no new OAuth flow needed. If this
recurs: don't assume the token is dead and jump to re-running `get-instagram-token.mjs` — first
just retry the `/me` call, since it may resolve on the Meta side (a transient automated-activity
flag, most likely) without any credential rotation. Only redo the OAuth dance if retries keep
failing after the user confirms they checked the dashboard.

**Token lifecycle differs from Blogger's refresh_token (which is effectively permanent):**
Instagram's long-lived token expires in ~60 days and must be actively rotated. Rather than a
static Vercel env var that goes stale, it's stored in **Redis** (`instagram:access_token` +
`instagram:token_refreshed_at`) and refreshed in-flight (`lib/instagram.ts`
`getValidAccessToken()`, same logic duplicated inline in the publish script since scripts/ don't
import the Next.js lib) whenever it's been ≥24h since the last refresh — `ig_refresh_token`
rejects tokens younger than 24h. As long as something calls the publish path at least once every
~59 days, the token renews itself indefinitely; if the account ever goes quiet longer than that,
redo the full OAuth dance with `get-instagram-token.mjs`.

## Instagram carousel posts ("카드뉴스" — added 2026-08-31)

Separate content format from the 건치 mascot Reels: a static multi-image swipe post (2-10
images), text-driven, no mascot, used for "신뢰형" credibility content (e.g. an 임플란트 선택
체크리스트 the user asked for after seeing a competing dentist's Instagram carousel as reference).

`scripts/publish-instagram-carousel.mjs <images-dir> "<caption>"` — new script, didn't exist
before this. Pattern: upload each image to Vercel Blob, create one child media container per
image with `is_carousel_item=true`, then one parent container with `media_type=CAROUSEL` and
`children=<comma-separated child ids>` + the caption, poll its `status_code` same as the Reels
flow, then `media_publish` the parent id. Images are read from the directory in filename-sorted
order, so name them `01.png, 02.png, ...` to control slide order. Same `getValidAccessToken()`
24h-refresh pattern duplicated inline as the Reels script.

**Design system for this format** (confirmed with the user 2026-08-31, revised once already —
first draft used the teal/mint brand palette from the blog and Malgun Gothic, user asked for a
full redo): 1080×1350 (4:5) PNGs — **not** the teal/mint brand color used everywhere else (blog
banners, 건치 shorts title cards). Font is **Noto Sans KR**
(`C:/Windows/Fonts/NotoSansKR-VF.ttf`, a variable font — `font.set_variation_by_name("Black"/
"Bold"/"Medium"/"Regular")` in PIL, not Malgun Gothic and not the mascot series' Jua font).
Rendered with the same PIL-overlay approach as the shorts captions (see geonchi-shorts skill) —
draw each slide as a full PNG via `PIL.ImageDraw`/`ImageFont`, no ffmpeg involved here since
there's no video, just static images published directly. A reusable generator (palette dict +
slide-type helpers: title/bullets/checklist-card/closing) lives at
`scripts/gen-med-disclosure-carousel.py` (older/original layout),
`scripts/gen-implant-aftercare-carousel.py` (2026-09-07 layout revision) and
`scripts/gen-implant-prosthesis-carousel.py` (2026-09-08 — **use this one as the base for new
carousels**; aftercare 레이아웃에 아래 두 가지가 더 붙어 있다) — copy and adapt per new carousel
topic rather than rebuilding the PIL layout from scratch each time.
- **불릿 오버플로 자동 축소.** `slide_bullets`가 42px로 배치해보고 하단 푸터(y=1230)를 넘기면
  40 → 38 → 36px로 한 단계씩 줄여 다시 배치한다. 3줄 제목 + 4개 불릿 조합에서 실제로 푸터를
  덮어써서 넣은 장치다 — 새 세트에서도 이 함수를 그대로 가져다 쓸 것.
- **설명용 단면 다이어그램 슬라이드**(`slide_diagram`). 임플란트 3부품(크라운/지대주/픽스처) +
  잇몸·잇몸뼈를 PIL 프리미티브로 그리고 리더 라인으로 라벨을 단다. 스톡 사진 대신 쓰는 표준 패턴.

**Layout conventions, revised 2026-09-07 after user feedback on the 임플란트 시술 후 관리
체크리스트 carousel — apply these to every new carousel, not just that one:**
- **Title AND the small eyebrow label are both horizontally centered** (not left-aligned at
  x=72 like the original `gen-med-disclosure-carousel.py`). `draw_title`/`draw_eyebrow` compute
  each line's width via `textbbox` and center it against the full 1080px canvas width.
- **The whole text block sits in the vertical-middle area of the canvas, not pinned to the top.**
  Concretely: title-only hook slides start the eyebrow around `y=420`, title `y=520`; slides with
  bullets/cards below the title start higher (`y=340` eyebrow / `y=420` title) so the body content
  still fits above the footer. See `gen-implant-aftercare-carousel.py` for the exact per-slide-type
  y-anchors — reuse them rather than re-deriving from scratch.
- **Fonts are bigger than the original med_disclosure_checklist baseline**: eyebrow 40px, hook-slide
  title 84px, bullets/checklist-card title 66-74px, checklist card heading 50px, body/bullet text
  42px, card sub text 36px. Bump further only if the user asks — this is already a deliberate
  increase over the original (title 64 / body 32), don't regress back down.
- **Bullet text auto-wraps** — at 42px, a full-width Korean sentence can overflow the 1080px
  canvas (this happened once, right edge got clipped). `wrap_text()` in
  `gen-implant-aftercare-carousel.py` splits on spaces to fit `max_width`; always route bullet
  strings through it instead of assuming a single line fits.

**Palette rotation (set by the user 2026-09-01, extended 2026-09-07): 진녹색(green) →
네이비(navy) → 와인색(wine) → 황토색(ochre) → repeat**, one palette per carousel post, cycling
in that order. Four palettes, same structure (`BG`/`CARD`/`INK`/`INK_SOFT`/`ACCENT`):
- **navy** (used for 임플란트 상담 체크리스트, 2026-08-31, 1st post — predates the rotation rule):
  bg `#0A1428`, card `#132444`, ink `#F0F4FA`, ink-soft `#A3B3D1`, accent `#7AA8FF`
- **green** (used for 발치 전 복용약물 고지 체크리스트, 2026-09-01, 1st post under the rotation
  rule — so it's the cycle's starting point): bg `#0A1F16`, card `#112D20`, ink `#F0FAF4`,
  ink-soft `#A3C9B3`, accent `#6ED9A0`
- **wine** (used for 소아 치아 관리 체크리스트, 2026-09-04): bg `#200C14`, card `#381622`,
  ink `#FAF1F4`, ink-soft `#CEA3B3`, accent `#E882A0`
- **ochre** (used for 임플란트 시술 후 관리 체크리스트, 2026-09-07 — added to the rotation by
  explicit user request, picked out of turn ahead of navy for this one post): bg `#4E3014`
  (톤업된 밝은 황토색 — an earlier darker `#241608` draft was rejected as too dark), card
  `#7C5228`, ink `#FFF8EE`, ink-soft `#E8C9A3`, accent `#EBB264`

- **골드/노랑(gold)** (2026-09-17 사용자 지정 "캐러셀 노랑색 바탕" — 기존 ochre가 갈색에 가까워
  노란 쪽으로 새로 뽑았다): bg `#3A2C08`, card `#5C4712`, ink `#FFFBEE`, ink-soft `#E9D9A6`,
  accent `#F5C838`. 정의는 `scripts/sinus_lift_diagram.py` 상단(캐러셀·영상이 같은 값을 공유).

navy는 2026-09-08 임플란트 보철 연결 방식(SCRP) 세트에도 다시 썼다 — 사용자가 "바탕은 파랑색"으로
지정해서 순서상 차례와 맞아떨어졌다(`gen-implant-prosthesis-carousel.py`).

**실제 발행 이력 (순서 판단은 이 표를 기준으로 — 로테이션 규칙만 보고 추측하지 말 것):**

| # | 날짜 | 주제 | 팔레트 |
| --- | --- | --- | --- |
| 1 | 2026-08-31 | 임플란트 상담 전 체크리스트 (9장) | navy |
| 2 | 2026-09-02 | 발치 전 복용약물 고지 (8장) | green |
| 3 | 2026-09-04 | 소아 치아 관리 (8장) | wine |
| 4 | 2026-09-08 | 임플란트 보철 연결 방식 / SCRP (9장) | navy |
| 5 | 2026-09-11 | 추석: 명절 음식별 치아 지키는 법 (8장) — https://www.instagram.com/p/DdIr6TylEtB/ | navy (사용자 지정) |

다음 차례는 **ochre** — 마침 대기 중인 시술 후 관리 세트가 ochre라 그대로 나가면 순서가 맞는다.
그 다음은 green → navy → wine 순으로 돌린다.

**Pending (2026-09-08 기준):** ochre "임플란트 시술 후 관리 체크리스트"(8장, navy 상담 체크리스트와
주제가 다름)는 생성·승인 완료했지만 **아직 미발행**이다 —
`assets/instagram_carousels/implant_aftercare_checklist/01.png`-`08.png`.
**사용자가 순서를 못박았다: 건치 에피소드 영상을 먼저 올리고(2026-09-09 예정) 그 다음에 이 캐러셀.**
그러니 다음 세션에서 "지금 올릴까요?"를 먼저 묻지 말고, 건치 영상이 나갔는지부터 확인할 것.
**2026-09-10: 사용자가 순서를 바꿨다 — "7탄부터 올릴꺼야. 황토색은 나중에".** 추석 시즌성 때문에
건치 7탄(추석간식)을 6탄 바로 다음에 연달아 올렸다(릴스 https://www.instagram.com/reel/DdGgkjwCaBQ/ +
블로그 https://healthydentalwonju.blogspot.com/2026/09/7-3.html). 번갈아 올리기 원칙보다 사용자의
명시적 지시가 우선. ochre 캐러셀은 여전히 미발행 — 다음 게시물이 이것이다.

**추석 시즌 세트 (2026-09-11 제작):** 사용자가 주제·색을 직접 골랐다 — 로테이션 예외.
파랑 음식 편은 9/11 발행 완료, 황토 부모님 편은 아직 미발행(사용자가 음식 편을 먼저 고름).
대기 캐러셀: 황토 부모님 편(추석 전 권장) + 황토 임플란트 시술 후 관리. **2026-09-14 건치 8탄(연휴 치통) 릴스+블로그 게시 완료 → 다음 게시는 캐러셀 차례.**
**2026-09-17 사용자 결정: 상악동 거상술(영상+캐러셀) 게시물 다음 순서로 "고향 가면 부모님 치아" 황토 편을 올린다.**
- 황토색 "고향 가면, 부모님 치아 이것만 봐주세요" (8장) — `assets/instagram_carousels/chuseok_parents_teeth/`,
  `scripts/gen-chuseok-parents-carousel.py`
- 파랑(navy) "명절 음식별 치아 지키는 법" (8장) — `assets/instagram_carousels/chuseok_food_guide/`,
  `scripts/gen-chuseok-food-carousel.py`
- 세 번째 "추석 연휴 치과 응급 대처법"은 사용자가 병원 연휴 진료 일정을 파악한 뒤 의뢰하기로 함 —
  일정은 절대 추측해서 넣지 말 것.
  **2026-09-13 사용자 확인 일정: 9/24(목)~9/27(일) 휴진, 그 외엔 평소와 동일(9/28 월 정상 진료).**
  이 일정으로 건치 8탄(연휴 치통 응급 대처)이 먼저 제작됨.
- 새 레이아웃 요소(이 두 스크립트가 최신 기준): 표지·마무리 장 반투명 보름달 모티프, 상단 8px 액센트 라인,
  체크/음식 카드 좌측 골드(또는 은빛) 바, **불릿·카드 슬라이드 모두 블록 전체를 세로 중앙 정렬**
  (기존 고정 y 앵커는 내용이 적으면 하단이 비어 보였음).

**Content rules for this format, learned from user feedback the same session:**
- **No price/discount framing at all** — the first draft said "저렴한 임플란트가 무조건 나쁜 건
  아니다", which even as a neutral-sounding statement still edges toward a 가격 비교/할인 광고
  reading under 의료법. Rewrite it out entirely rather than softening the wording; keep the whole
  piece to process/what-to-check content, never mention pricing.
- **Fact-delivery tone, not persuasive-assertion tone.** Avoid "정답은 ~입니다" framing; prefer
  "환자의 당연한 권리입니다" / "확인해보시면 도움이 됩니다" — objective, informational,
  non-comparative. No efficacy guarantees, no before/after, no testimonials, no superlatives —
  same guardrails as the blog (`lib/anthropic.ts` `GUARDRAILS`), applied by hand since this
  content is hand-authored, not model-generated.
- **Open with empathy before the checklist.** Acknowledge that the reader considering the
  procedure is naturally anxious ("고민되는 게 당연합니다") before moving into checklist
  content — mirrors what made the reference post the user linked effective.
- **Add an explanatory diagram, not a stock photo.** The user asked for "저작권 없는 사진이나
  설명을 돕는 그림" — rather than sourcing external stock photography (licensing risk, and real
  clinical photos raise their own medical-ad concerns), draw an original explanatory diagram with
  PIL primitives (rectangles/ellipses/polygons + leader-line labels) — e.g. a implant
  cross-section showing crown/abutment/fixture/bone. Zero copyright exposure since it's authored
  in-session, and it reads as more credible/clinical than a stock photo would anyway.

## 영상 + 캐러셀 혼합 게시물 (2026-09-17 신규)

인스타 캐러셀은 **이미지와 영상을 한 게시물에 섞을 수 있다.** 사용자 지시("그래피컬한 영상과 캐러셀을
혼합해서 같이 올리자")로 처음 시도한 형식 — 1번 칸에 설명 영상, 2번부터 카드뉴스.

`scripts/publish-instagram-carousel.mjs`를 이 형식에 맞게 고쳐 뒀다 (2026-09-17):
- 파일 필터에 `mp4` 추가. `00_video.mp4` → `01.png` 순으로 정렬되도록 이름을 붙인다.
- mp4는 `media_type=VIDEO` + `video_url`로 자식 컨테이너를 만들고, **인코딩이 끝날 때까지
  (`status_code == FINISHED`) 기다린 뒤에** 부모 캐러셀에 넣는다. 이미지는 즉시 넣어도 된다.
- 영상 첫 프레임이 곧 피드 썸네일이므로, 영상 맨 앞을 타이틀 카드로 고정할 것(페이드인 금지).

### 상악동 거상술 뼈이식 (제작 중 — 다음 세션에서 이어서)

사용자가 참조 릴스를 주고 "뼈이식하는 걸 그래피컬하게 재구현"을 요청했다. 진행 상태와 남은 순서는
**`assets/instagram_carousels/sinus_lift_bonegraft/higgsfield-shot-plan.md`에 전부 적어 뒀다** —
새 세션에서는 그 파일부터 읽을 것.

완성된 것: 캐러셀 8장(골드 팔레트, `gen-sinus-lift-carousel.py`), 캡션(`caption.txt`, 의료광고법 검토
완료), ASMR 오디오(`gen-sinus-lift-anim.py`의 `build_audio()` — numpy로 합성, 사용자 평가 "소리는 좋다").

**영상은 다시 만들어야 한다.** 2D 모식도(`sinus_lift_diagram.py`) → "직관적이지 않다, 3D로" 반려 →
자체 SDF 3D 렌더러(`sinus_lift_3d.py`) → "이건 영 모르겠어" 반려 → **Higgsfield 생성으로 확정.**
시술 설명 영상은 앞으로 처음부터 Higgsfield로 갈 것(2D 도식으로 시작하지 말 것).

ASMR 사운드 합성은 재사용 가치가 있다: 룸톤(로우패스 화이트노이즈) + 장면별 효과음(버 패스,
점막 마찰+크래클, 알갱이 낙하, 천 스침, 상승 패드, 라쳇 클릭)을 numpy로 만들어 `place()`로
타임라인에 배치한다. **cumsum 브라운 노이즈는 쓰지 말 것** — 랜덤워크라 뒤로 갈수록 레벨이 커져
장면별 음량이 들쭉날쭉해진다(실제로 겪음).

**캐러셀을 발행하면 홈페이지 치과지식 페이지에도 반드시 추가 (2026-09-14 사용자 지시 "앞으로 캐러셀 업로드하면,
치과지식 페이지에도 넣어줘").** 저장소 루트 `knowledge/carousels.json` **맨 앞**에 항목 추가 —
`slug`(영문 kebab), `src`(PNG 폴더), `date`, `category`(기존 값 재사용: 임플란트/소아 진료/진료 준비/생활 관리 등),
`title`(표지 문구), `summary`(인스타 캡션을 1~2문장으로 — 의료광고법 기준 유지, 가격·효과 보장 금지),
`instagram`(발행 후 Graph API로 받은 permalink). 그다음 `PYTHONIOENCODING=utf-8 python knowledge/build.py` →
`knowledge.html` + `knowledge/` 커밋·푸시(GitHub Pages 배포). 자세한 구조는 `homepage` 스킬의 치과지식 페이지 절.

After a carousel ships, do the same follow-through as any other manual post: push the topic onto
`dental-blog:recent-topics` in Redis (see the one-off blog post section above), and if a
same-themed article also goes to the blog, upload the same images to Blob (`upload-blog-images.mjs`)
and inline the diagram (not the navy card slides — visual style clashes with the blog's teal/light
theme) into a normal teal-banner article via `publish-geonchi-post.mjs`.

## Threads publishing (canceled 2026-08-28 — kept for reference only, don't resume unasked)

Threads uses a **separate** Meta product/app surface (`THREADS_APP_ID`/`THREADS_APP_SECRET`,
distinct from both the Facebook and Instagram app credentials), OAuth at `threads.net/oauth/authorize`
with scopes `threads_basic threads_content_publish`, publish via the same container pattern at
`graph.threads.net` (`POST /threads` then `POST /threads_publish`). **Meta's docs state that
publishing requires "Tech Provider Verification" before an app can post to production
accounts** — unconfirmed whether this blocks testing with the developer's own account (Instagram
publishing did NOT require an equivalent step for the same account) or only third-party/Advanced
Access. Next session should just attempt the OAuth authorize step (same https-redirect-URI
lesson from Instagram applies) and see whether it's actually blocked before assuming it needs a
week-long verification wait.

## Client-facing status report (Notion) — update after every change, not just when asked

Separate from any internal engineering notes, there is a **client-facing** Notion report at
https://app.notion.com/p/3ca52ea50362816b9c6ec7d0883afee1 ("원주 건강한치과 디지털 마케팅 진행
리포트") — written for the clinic owner, not a developer. Per the user's explicit instruction
(2026-08-29): **update this page whenever new content is published or the system changes**, not
only when asked to. Keep its tone and shape: a status table up top, then one section per
workstream (each stating what was done AND a "💡 기대 효과" business-value line — the client
wants to see the work *and* why it matters, not just a changelog), a "앞으로 진행 예정" list, and
a closing "종합 기대 효과" summary. Business language throughout — no code, no env vars, no
credentials, no internal gotchas (all of that belongs only in this skill file and the separate
internal Notion status page, never here).

**Weekly work log (added 2026-08-29):** the same page also opens with a "🗓️ 주간 작업 일지"
section, day-by-day for the current week, prepended above the workstream summary. Deliberately
granular — break the week's work into many concrete line items rather than 2-3 broad bullets,
per the user's explicit ask that it "하는일이 많아보이게" (make the volume of work visible). Add
a new week's section at the **top** (`position: {"type": "start"}`) each week rather than
replacing the previous one — it's a running log, older weeks stay.

**Daily evening update (added 2026-08-30):** the user asked for an entry every evening, even on
days with no visible content shipped, framed as ongoing internal engine/infra work — since this
report goes to the paying client, inventing work that didn't happen would be misreporting to
them, so this was pushed back on and the user agreed (2026-08-30, "응.. 그래 고마워..") to a
truthful version instead: log what's actually and verifiably true about that day even if nothing
new was built — the automated pipeline running (Blogger cron fired, Instagram token refresh
checked, topic-dedup history checked), rather than fabricated "engine setup" work. A day with
genuinely nothing to report can just say "이번 주는 신규 배포 없음 / 자동화 파이프라인만 가동"
plainly — that in itself is a legitimate, honest signal that the 24/7 automation is working.
Never write a line item for work that did not happen.

## Verifying it's actually working

```bash
cd dental-blog-autopost
npm run dev
# separate terminal:
curl -H "Authorization: Bearer $CRON_SECRET" http://localhost:3000/api/cron/generate-post
```

This publishes a real post to the live blog — delete it from the Blogger dashboard after
confirming. In production, check Vercel's Project → Cron Jobs tab for run history/logs instead
of waiting for the next scheduled fire.

## Setup status log

Keep this updated as steps complete, so a future session picks up where this one left off
instead of re-asking the user to redo finished steps:

- [x] Next.js project scaffolded, `tsc --noEmit` and `next build` both verified locally
- [x] Google Cloud Console: project + Blogger API v3 enabled + OAuth consent screen + OAuth
      client (ended up "Web application" type, not Desktop — redirect URI
      `http://127.0.0.1:53682/oauth2callback` had to be added manually under the client's
      "Authorized redirect URIs" to fix a `redirect_uri_mismatch`)
- [x] `BLOGGER_BLOG_ID` = `9161887851801213789` (found in the public page source's
      `_WidgetManager._SetDataContext` blob — no API key/login needed)
- [x] `BLOGGER_REFRESH_TOKEN` issued via `get-refresh-token.mjs`
- [x] `ANTHROPIC_API_KEY` issued (Sonnet 5 confirmed as the model choice — see model note above)
- [x] Redis: used a **standalone Upstash account** (console.upstash.com), not the Vercel
      Marketplace integration — `vercel integration add upstash/upstash-kv` repeatedly failed
      at its browser-handoff step ("Additional setup required") even after the user logged in;
      abandoned it and had the user create a free Regional database directly on Upstash and
      paste the REST URL/token instead. Root directory setting note: `vercel project update
      --root-directory dental-blog-autopost` broke CLI deploys run from *inside* that folder
      ("Root Directory ... does not exist") — reset to auto-detect (`--auto-detect
      root-directory`) since deploys here go through `vercel deploy --prod` from inside
      `dental-blog-autopost/`, not a GitHub-push-triggered build from repo root.
- [x] Vercel project created (`michelle-d5f1/dental-blog-autopost`), all 8 env vars registered
      to production+preview+development, deployed to
      https://dental-blog-autopost.vercel.app
- [x] First manual curl test confirmed a real post landed on the blog (then deleted via the
      Blogger API + popped back off the Redis history list, to keep the topic available again)
- [x] Cron job confirmed registered (`vercel crons ls`): Mon/Thu 00:00 UTC = 09:00 KST
- [x] 2026-09-08: refresh token 만료로 죽어 있던 크론 복구 — 새 토큰 발급 → `.env.local` +
      Vercel production 갱신 → `vercel deploy --prod` 재배포 → `vercel crons ls` 확인.
      **OAuth 동의화면 프로덕션 전환은 사용자 미완료 상태**(위 refresh token 섹션 참고)
- [x] 2026-09-10 (목): 무인 크론 발행 확인 — 공개 피드에 09:44 KST "입 안 건강이 몸 전체에 미치는
      영향, 알고 계셨나요?"가 사람 개입 없이 올라왔다(9/8 토큰 복구 이후 첫 정기 발행).
