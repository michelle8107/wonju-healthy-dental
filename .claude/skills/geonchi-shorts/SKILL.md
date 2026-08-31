---
name: geonchi-shorts
description: Produce a new episode of the "건치의 하루" (토순이) vertical short-form video series for 원주 건강한치과 — character-consistent bunny mascot, Higgsfield video generation, 토순이 voice narration, synced Jua-font captions, SFX, and logo outro. Use when the user asks for a new 건치/토순이 episode, "N탄", or a similar short-form dental clinic mascot video.
---

# 건치의 하루 (토순이) Shorts — Production Skill

Vertical (9:16) short-form video series starring a cute white bunny mascot for 원주 건강한치과.
Each episode is ~14-16s: a relatable dental-anxiety/procrastination beat, a comedic reversal, a
reassurance line, and a branded logo outro.

**Naming (corrected 2026-08-28): the character's name in any user-facing text — captions, blog
posts, Instagram captions, anything a reader sees — is 건치, never 토순이.** "토순이" was this
assistant's own placeholder nickname from early sessions, not something the user ever approved;
it survives only as internal asset filenames/voice names below (`tosuni_reference.jpg`, the
Higgsfield voice literally named "토순이-2") because renaming those isn't worth the churn — don't
let that leak into anything a reader sees.

Reusable assets live in `assets/geonchi_shorts/`:
- `tosuni_reference.jpg` — clean, caption-free reference image of the bunny character (for video-gen character consistency)
- `fonts/Jua-Regular.ttf` — the caption font (Google Fonts "Jua")
- `geonchihan_chikwa_logo.png` — clean bright frame of the 건강한치과 logo card (for the outro)
- `cute_chime.wav` — synthesized cheerful chime for when the logo appears

Past episodes: `output/shorts_yeyak_miruji_final_v3.mp4` (1탄 - 예약 미루기),
`output/geonchi2_scaling.mp4` (2탄 - 스케일링 예약 vs 실제),
`output/건치의하루 3편.mp4` (3탄 - 양치할 때 vs 안 할 때 치아 비교 — actual filename on disk,
not `geonchi3_yangchi.mp4` as previously logged here. Made 8/28, before the title-card feature
below existed, so it originally published to Instagram with no title card. 2026-08-31: caught by
the user after publish, retrofitted by overlaying a "양치" title PNG (same PIL method as below)
onto the existing final mux with `enable='between(t,0,13.3)'` — cut off just before the logo
fade-to-black at 13.5s — then re-published as a new Reel. The old untitled Reel was left live on
Instagram (deleting a published post wasn't confirmed) and the old file kept as
`건치의하루 3편_제목없음_구버전.mp4` for reference. Episodes 4탄/5탄 below already had the title
card baked in from generation, so this was a one-off backfill, not a pipeline gap.),
`output/geonchi4_saranghi.mp4` (4탄 - 사랑니 발치 공포 vs 실제, 18.9s — longer than the usual
14-16s since this one needed a 4-line narration; logo card was extended to 5.8s to hold the last
two lines + chime without cramming. 2026-08-30 fix: scene 2 originally showed a rotary
drill/handpiece, which is wrong for an extraction scene — user caught it via annotated screenshot.
Regenerated just that scene with an explicit "extraction forceps, NOT a drill/handpiece" prompt,
re-trimmed to the same 4.125s, rebuilt the concat/captions/mux with identical timings since only
the visual changed. Lesson: double-check that AI-generated medical/dental tools in a scene prompt
actually match the procedure being depicted — a generic "dental tool" prompt can render a drill by
default even in a scene explicitly about extraction). `output/geonchi5_new_semester.mp4` (5탄 -
새 학기 아이 치아검진 체크리스트, from content-calendar D19, 17.5s. Scene 2 first draft came back
as a hyper-realistic macro mouth-interior shot — cute but off-brand and mildly disturbing;
regenerated with an explicit "keep the bunny's whole cute face in frame, medium shot, not
photorealistic" prompt instead of describing the mouth interior, which fixed it. Also: this
session's `drawtext` filter segfaults unconditionally on this machine regardless of fontconfig
setup (see Captions section below) — worked around by rendering captions/title as PIL PNG overlays
instead of drawtext; that workaround is now the default approach, don't retry drawtext first).
Content-calendar concepts to draw from live in `output/geonchi-content-calendar.html` (formats
A/B/C, 4-week plan). Track which concepts have been used so future episodes don't repeat one.
Used so far: D1(1탄 예약미루기), D12(2탄 스케일링), 3탄(양치비교, custom), 4탄(사랑니, custom),
D19(5탄 새학기검진). Still unused: D3, D5, D8, D10, D15, D17, D22, D24, D26, D27.

## Voice

Higgsfield custom voice "토순이-2": `voice_type: element`, `voice_id: 6d821a21-c7ea-4883-88db-cb66c9df7417`.
Model `seed_audio`. Re-check `list_voices` if the id ever 404s (voices can be recreated).

Generate each line as a **separate** TTS call (not one giant paragraph) — this makes it possible
to time-align each line to its own scene/caption. Use `generate_audio_batch` for 2-12 lines at once.

TTS output ALWAYS has variable leading/trailing silence, sometimes 1-2s of it, and any "..."
in the prompt inserts a long dramatic pause (0.7-1.7s) — regenerate with fewer/no ellipses if a
line comes back far longer than its natural speech would need. Workflow per line:
1. `ffmpeg -i line.wav -af silencedetect=noise=-35dB:d=0.12 -f null -` → read the printed
   `silence_start`/`silence_end` pairs to find where real speech starts and ends.
2. `atrim=<start>:<end>,asetpts=PTS-STARTPTS` to cut the dead air.
3. `atempo=X` (typically 1.1-1.35) to fit the line into its scene's time budget without sounding
   too rushed or too slow. Never exceed ~1.4x or it starts sounding chipmunk-y.

## Video generation (new scenes)

Model: `seedance_2_5`, `mode: "omni_reference"` (required — plain `image` role errors with
"mode 't2v' does not accept reference media"), `medias: [{value: <uploaded_ref_media_id>,
role: "image_references"}]`, `aspect_ratio: "9:16"`, `generate_audio: false` (we add our own
narration/SFX). Cost ≈32.5 credits per 5s clip — check with `get_cost:true` before a batch if
unsure of current pricing. Use `generate_video_batch` to submit all scenes for an episode in
parallel (one `index` per scene), then `jobs_wait` — video jobs take 3-8+ minutes, so poll with
`ScheduleWakeup` (60-100s intervals) rather than blocking synchronously.

Upload the reference image fresh each session via `media_upload` → curl PUT → `media_confirm`
(media_ids don't persist across sessions/uploads). Use `assets/geonchi_shorts/tosuni_reference.jpg`.

Prompt pattern per scene: re-describe the character fully every time ("a cute fluffy white
bunny character with pink cheeks and a small blue toothbrush clip on its head") plus the
scene's specific action/setting/expression. Keep the art style phrase consistent across scenes
and across episodes: "cute 3D pixar-like render style". Generated clips come back ~5s each —
trim ~0.2-0.3s off the front (avoids a morphing/settling first frame) to the desired scene
length with `-ss <in> -t <dur>`.

## Structure template

1. **Setup** (~4s): the relatable everyday beat (booking confidently, ignoring a reminder, etc.)
2. **Turn** (~4-4.5s): the comedic reversal/anxiety beat — give this one slightly more time
3. **Payoff** (~4s, can split into 2 lines): relief + the reassurance message (this is the one
   line that should land near-verbatim from the content-calendar's suggested CTA/안심 멘트)
4. **Logo outro** (~3s): static `geonchihan_chikwa_logo.png`, held via
   `ffmpeg -loop 1 -i logo.png -t 3.0 -vf "fade=t=in:st=0:d=0.3,fps=24"` (NOT extracted from an
   old episode's fade — that region dips dark/gray mid-transition; a fresh static hold from the
   clean PNG avoids that). Chime SFX starts right as the outro begins or right after the last
   narration line ends, whichever is later, and must finish before the video's final ~0.3-0.5s.

Concatenate scenes with the ffmpeg concat demuxer (`-f concat -safe 0`, re-encode — don't stream
copy across differently-generated sources).

## Episode title overlay (added 2026-08-30)

Every episode also gets a short punchy title card text (not the series name "건치의 하루" —
a short 2-4 char label naming *that episode's* theme, e.g. "사랑니", "양치", "예약미루기 달인"),
Jua font, white fill with `borderw=6:bordercolor=black@0.7`, `fontsize=150`, horizontally
centered, `y=350`. Applies across all 3 story scenes but must be turned off during the logo
outro (`enable='between(t,0,<logo_start_time>)'`) — the white fill is only visible against the
black border on the live-action scenes; over the white logo card background it becomes an
illegible hollow outline.

## Captions

**Rendering method (2026-08-31): use PIL, not ffmpeg drawtext.** On this machine ffmpeg's
`drawtext` filter segfaults unconditionally — with or without a fontconfig config file, with any
font directory (even one containing only Jua-Regular.ttf), with `text_shaping=0`, with plain ASCII
text. It's a crash in this ffmpeg build's font/text-shaping stack, not a prompt or config mistake —
don't waste time re-diagnosing it. The working approach: for each caption/title, render a full
720x1280 transparent RGBA PNG in Python (`PIL.ImageDraw`, `ImageFont.truetype` on the Jua ttf
directly — no fontconfig involved) with the box + text already baked in, then composite each one
onto the picture-locked video via ffmpeg's `overlay` filter with its own
`enable='between(t,START,END)'` window (chain multiple `overlay` calls, one per caption/title).
`ImageFont.truetype(path, size)` + `draw.textbbox` for centering + `draw.text(..., stroke_width=,
stroke_fill=)` for the title's outline covers everything drawtext would have done.

Jua font (`assets/geonchi_shorts/fonts/Jua-Regular.ttf`), white text, semi-transparent black box
(`color=black@0.55`, NOT fully opaque — that reads as a harsh block; fully transparent-less
0.55 was confirmed as the right balance by the user). Box: `x=0:y=978:w=720:h=130` for one
line (`fontsize` 44-50, text `y=1018-1020`), taller (`h=185`, `y=940`) if a caption needs two
lines.

**Critical sync rule** (learned the hard way across 1탄/2탄 revisions): the caption's
`enable='between(t,START,END)'` window must match the *actual trimmed+tempo'd narration audio's*
start/end for that line — not the underlying video scene's boundaries. Compute audio timings
first, then set caption windows to those same numbers. Never leave a caption box visible with no
text in it (no orphan `drawbox` — every box must be paired 1:1 with the text it holds and the
same enable window), and never show a box+caption while a *different* line is being spoken.

If reusing/editing an EXISTING baked video that already has its own burned-in captions in a
different font/design that need removing: don't paint a flat opaque box over the whole caption
band (it's fine for a spot you'll cover with new text, but for a spot you want just *emptied*
— no caption, no box — instead crop that tight region, `boxblur` it heavily, and overlay it
back at the same coordinates. That erases the old text without leaving a visible rectangle.
Fresh Higgsfield-generated scenes don't have this problem — they have no baked captions to begin
with.

## SFX

Higgsfield's audio tool is TTS-only — it explicitly refuses music/SFX prompts. For crunch/chew,
heartbeat, chime, etc., synthesize directly:
- **Chime/cute stinger**: 2-3 short sine tones (e.g. 1046→1568→2093 Hz), each with a fast
  `afade=t=out` decay, layered with small `adelay` offsets via `amix`.
- **Crunch/crackle**: numpy — bandpass-filtered noise bursts (FFT mask to a frequency band,
  `irfft` back) with fast exponential decay envelopes, layered as several micro-clicks per
  "bite" plus a low sine thump underneath for body. Flat/simple repeated noise bursts sound
  fake and were rejected once already — favor irregular timing/amplitude (`rng.uniform`) over
  a metronomic pattern.
- **Heartbeat/tension**: paired low sine thumps (~70-90Hz, ~90ms, sharp decay) at irregular
  "lub-dub" intervals, optionally accelerating slightly across the scene.

Mix everything with one `anullsrc`-based base track + `adelay`/`amix`, matching the full video
duration, then mux onto the picture-locked video (`-map 0:v -map 1:a -c:v copy -c:a aac -shortest`).

## Process checklist for a new episode

1. Ask the user (briefly, via AskUserQuestion) which content-calendar concept to use if not
   specified — don't silently reuse a beat from a prior episode.
2. Upload `tosuni_reference.jpg`, write 3 scene prompts, submit `generate_video_batch`.
3. While waiting (schedule wakeups, don't block): draft the narration lines per scene.
4. Once video jobs land: download, trim, generate/trim/tempo the narration lines, synthesize SFX.
5. Concat scenes + fresh logo outro. Render captions (sync rule above). Mix audio. Mux final.
6. Extract a couple of verification frames at scene-transition and caption-transition timestamps
   before sending — this has caught a wrong logo frame and caption ghosting in past episodes.
7. Send the file with `SendUserFile`, and briefly log the new episode + concept used at the
   bottom of this file's "Past episodes" list so the next session doesn't repeat it.
8. **Standing rule (2026-08-28, Threads dropped same day): every finished episode also gets
   published**, not just handed to the user — Instagram Reels + a Blogger post, via the
   `dental-blog-autopost` skill (that skill owns the credentials, scripts, and the
   Instagram-hashtag rules — read it before publishing, don't improvise the caption style here).
   Threads was scoped in and then explicitly canceled by the user the same day (Meta app was
   created but OAuth/publishing was never finished) — don't resume it unless asked again.
