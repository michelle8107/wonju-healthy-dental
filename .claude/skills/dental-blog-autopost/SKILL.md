---
name: dental-blog-autopost
description: Maintain/extend the 원주 건강한치과 Blogger auto-posting worker AND the Instagram/Threads publishing scripts, all living in the dental-blog-autopost/ subproject. Use when the user asks about the dental blog automation, uploading a 건치 쇼츠 episode to Instagram/Threads, changing posting schedule/topics/guardrails/hashtags, debugging why a post didn't publish, or rotating credentials.
---

## Standing rule: every new 건치 쇼츠 episode goes to Instagram + Blogger

Per the user's explicit instruction (2026-08-28): whenever a new episode is finished (see the
`geonchi-shorts` skill for production), it gets uploaded to **Instagram + Google Blogger**.
Naver Blog and Kakao Channel get manual copy-paste text only (no posting API exists for either —
see below) — write the post text with photo-placement markers like `[사진: ...]`, don't attempt
to automate those two.

- **Naming: never say "소아치과" (implies a specialist pediatric-dentistry designation this
  clinic doesn't hold) — use "소아 진료" instead**, everywhere (post titles, labels, body text).
  Corrected 2026-08-29 after it slipped into a published post's title/label/banner.
- **Naming: the on-screen mascot is always called 건치 in copy/captions/blog text, never
  토순이** (corrected 2026-08-28 — 토순이 was this assistant's placeholder name, never the
  user's; even though the character model is visually a rabbit, the series title "건치의 하루"
  makes 건치 the character's actual name everywhere it's referred to in writing).
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

Google OAuth refresh tokens for this "Desktop app" client don't expire from use, but do expire
if: the user revokes access at https://myaccount.google.com/permissions, the OAuth consent
screen is still in "Testing" mode and 7 days pass without... (actually testing-mode tokens are
generally fine indefinitely for testing users, but re-check current Google policy if this ever
breaks), or nobody's used it in 6 months. Re-run `npm run get-refresh-token` locally
(`dental-blog-autopost/scripts/get-refresh-token.mjs`) — it spins up a localhost server on port
53682, opens the OAuth consent URL, and prints a fresh refresh_token after the browser approval.
Must be run by someone logged into the Google account that manages
healthydentalwonju.blogspot.com.

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
4. Publish with `scripts/publish-geonchi-post.mjs <html-file> "<title>" "label1,label2"` — this
   appends the same `CLINIC_FOOTER` as the cron path (duplicated inline since scripts/ can't
   import the Next.js `lib/blogger.ts` — keep both copies in sync if the footer ever changes).

## One-off manual blog posts ("치과 관련 글 하나 더 써줘" — not tied to an episode or the cron)

Same publishing mechanism as the episode companion posts above (`scripts/publish-geonchi-post.mjs
<html-file> "<title>" "labels"` — the script name is historical, it's a generic "publish an HTML
post with the clinic footer" tool, not episode-specific), just without the video/screenshots:
write a professional/informational article (see `scripts/implant-guide-post.html` and
`scripts/gum-health-post.html` for the established shape — teal header banner div, numbered/
bulleted sections, a comparison table where it fits the topic, closing with 표경열 원장's real
credentials for E-E-A-T, then the standard "정확한 진단은 상담 후" close). No mascot, no casual
voice — this tone is deliberately more clinical/expert than the episode posts. Same guardrails
apply (no efficacy promises, no before/after, no testimonials, no discounts).

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
full redo): 1080×1350 (4:5) PNGs, **navy palette** — bg `#0A1428`, card bg `#132444`, ink
`#F0F4FA`, ink-soft `#A3B3D1`, accent blue `#7AA8FF` — **not** the teal/mint brand color used
everywhere else (blog banners, 건치 shorts title cards). Font is **Noto Sans KR**
(`C:/Windows/Fonts/NotoSansKR-VF.ttf`, a variable font — `font.set_variation_by_name("Black"/
"Bold"/"Medium"/"Regular")` in PIL, not Malgun Gothic and not the mascot series' Jua font).
Rendered with the same PIL-overlay approach as the shorts captions (see geonchi-shorts skill) —
draw each slide as a full PNG via `PIL.ImageDraw`/`ImageFont`, no ffmpeg involved here since
there's no video, just static images published directly.

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
- [ ] Not yet confirmed: an actual unattended scheduled fire (next Mon/Thu) — everything above
      was a manual trigger. If asked to verify later, check Vercel dashboard → Project → Cron
      Jobs → run history rather than re-triggering manually.
