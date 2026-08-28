---
name: dental-blog-autopost
description: Maintain/extend the 원주 건강한치과 Blogger auto-posting worker (dental-blog-autopost/ subproject) — Claude-generated SEO blog posts published automatically via Vercel Cron. Use when the user asks about the dental blog automation, changing posting schedule/topics/guardrails, debugging why a post didn't publish, or rotating credentials.
---

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
- [ ] Google Cloud Console: project + Blogger API v3 enabled + OAuth consent screen + Desktop
      OAuth client
- [ ] `BLOGGER_BLOG_ID` looked up
- [ ] `BLOGGER_REFRESH_TOKEN` issued via `get-refresh-token.mjs`
- [ ] New `ANTHROPIC_API_KEY` issued
- [ ] Vercel project created (Root Directory = `dental-blog-autopost`) + all env vars registered
      + Upstash Redis marketplace integration added
- [ ] First manual curl test confirmed a real post landed on the blog
- [ ] Confirmed cron job registered in Vercel dashboard and fired once on schedule
