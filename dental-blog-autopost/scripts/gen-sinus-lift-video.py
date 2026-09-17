# -*- coding: utf-8 -*-
"""
상악동 거상술 + 뼈이식 설명 영상 — Higgsfield 3D 생성 클립 5개 + 자막 + ASMR 합성.
(2D 모식도판 gen-sinus-lift-anim.py를 대체. 자막 스타일·ASMR 합성 헬퍼는 그대로 가져다 쓴다.)

  python gen-sinus-lift-video.py            # 전체 렌더
  python gen-sinus-lift-video.py --still 9  # 9초 지점 한 장만 미리보기

입력: _sinus_hf_clips/shot1.mp4 ~ shot5.mp4 (Higgsfield seedance_2_5, 9:16, 5초)
출력: assets/instagram_carousels/sinus_lift_bonegraft/00_video.mp4 (1080x1350, 24fps)
"""
import importlib.util
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

import sinus_lift_diagram as S

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("anim", os.path.join(HERE, "gen-sinus-lift-anim.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

FPS, SR = A.FPS, A.SR
CLIPS = os.path.join(HERE, "_sinus_hf_clips")
WORK = os.path.join(HERE, "_sinus_hf_frames")
OUT_DIR = A.OUT_DIR

TRIM_IN = 0.25     # 생성 클립 첫 프레임의 모핑 구간 제거
SHOT_LEN = 4.6

INTRO = 2.6
OUTRO = 3.2
SHOT_T0 = [INTRO + i * SHOT_LEN for i in range(5)]
DUR = INTRO + 5 * SHOT_LEN + OUTRO

# (시작, 길이, eyebrow, 제목 줄, 하단 노트)
CAPTIONS = [
    (SHOT_T0[0], 2.3, "여기가 어디냐면", ["위쪽 어금니 위에는", "'상악동'이라는 빈 공간이 있습니다"], None),
    (SHOT_T0[0] + 2.3, 2.3, "뼈이식을 하는 이유", ["남은 뼈가 얇으면", "임플란트를 바로 심기 어렵습니다"], None),
    (SHOT_T0[1], SHOT_LEN, "1단계", ["볼쪽 뼈에 작은 창을 만듭니다"], "측방 접근 (lateral window)"),
    (SHOT_T0[2], SHOT_LEN, "2단계", ["상악동 점막을", "찢어지지 않게 들어올립니다"], None),
    (SHOT_T0[3], SHOT_LEN, "3단계", ["들어올린 공간에", "뼈이식재를 채웁니다"], None),
    (SHOT_T0[4], SHOT_LEN, "4단계", ["뼈가 자리 잡으면", "임플란트를 식립합니다"],
     "※ 치유 기간과 식립 시기는 개인의 상태에 따라 다릅니다"),
]


def clip_frame(shot, u):
    """shot(0~4)의 u초 지점 프레임 → 1080x1350 센터 크롭."""
    path = os.path.join(WORK, "shot%d" % (shot + 1), "f%04d.png" % min(int(u * FPS), int(SHOT_LEN * FPS) - 1))
    return Image.open(path).convert("RGB")


def extract_clips():
    for k in range(5):
        d = os.path.join(WORK, "shot%d" % (k + 1))
        os.makedirs(d, exist_ok=True)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-ss", str(TRIM_IN), "-t", str(SHOT_LEN),
            "-i", os.path.join(CLIPS, "shot%d.mp4" % (k + 1)),
            "-vf", "fps=%d,scale=1080:-2:flags=lanczos,crop=1080:1350" % FPS,
            "-start_number", "0", os.path.join(d, "f%04d.png"),
        ], check=True)


def top_shade(img):
    """자막 가독성용 상단 그라데이션 + 하단 살짝."""
    shade = Image.new("L", (S.W, S.H), 0)
    px = np.zeros((S.H, 1), dtype=np.float32)
    y = np.arange(S.H, dtype=np.float32)
    px[:, 0] = np.clip(1 - y / 520, 0, 1) ** 1.2 * 215 + np.clip((y - 1150) / 200, 0, 1) * 150
    shade = Image.fromarray(np.repeat(px, S.W, axis=1).astype(np.uint8), "L")
    dark = Image.new("RGB", (S.W, S.H), (20, 14, 2))
    return Image.composite(dark, img, shade)


def title_card(t, outro):
    img, _ = S.new_canvas()
    layer = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if outro:
        a = int(255 * S.ease((t - (DUR - OUTRO)) / 0.4))
        A.draw_eyebrow(d, "상악동 거상술 · 뼈이식", 452, a)
        bottom = A.draw_lines(d, ["원주 건강한치과"], 534, 78, a)
        x = (S.W - 150) // 2
        d.rectangle([x, bottom + 26, x + 150, bottom + 36], fill=S.ACCENT + (a,))
        f = S.font(34)
        for i, line in enumerate(["이 영상은 이해를 돕기 위해 AI로 생성한 3D 애니메이션으로,",
                                  "실제 해부 구조·치료 방법·기간은 검사 결과에 따라 다릅니다."]):
            d.text(((S.W - S.text_w(d, line, f)) // 2, bottom + 80 + i * 50), line,
                   font=f, fill=S.INK_SOFT + (a,))
        f2 = S.font(32)
        addr = "원주시 건강로 21, 2층 · TEL 033-734-2275"
        d.text(((S.W - S.text_w(d, addr, f2)) // 2, bottom + 216), addr, font=f2, fill=S.INK_SOFT + (a,))
    else:
        # 첫 프레임 = 피드 썸네일 → 페이드인 없이 완성된 상태로 시작
        A.draw_eyebrow(d, "원주 건강한치과 · 3D 애니메이션", 470, 255)
        bottom = A.draw_lines(d, ["임플란트 뼈이식,", "이렇게 합니다"], 552, 84, 255)
        x = (S.W - 150) // 2
        d.rectangle([x, bottom + 26, x + 150, bottom + 36], fill=S.ACCENT + (255,))
        f = S.font(36)
        note = "상악동 거상술 · 측방 접근"
        d.text(((S.W - S.text_w(d, note, f)) // 2, bottom + 76), note, font=f, fill=S.INK_SOFT + (255,))
    base = img.convert("RGBA")
    base.alpha_composite(layer)
    return base.convert("RGB")


def render_frame(t):
    if t < INTRO:
        img = title_card(t, False)
        if t > INTRO - 0.3:  # 첫 컷으로 짧은 크로스페이드
            img = Image.blend(img, top_shade(clip_frame(0, 0)), (t - (INTRO - 0.3)) / 0.3)
    elif t >= DUR - OUTRO:
        img = title_card(t, True)
    else:
        shot = min(4, int((t - INTRO) / SHOT_LEN))
        img = top_shade(clip_frame(shot, t - SHOT_T0[shot]))
        layer = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for start, dur, eyebrow, title, note in CAPTIONS:
            if start <= t < start + dur:
                a = int(255 * A.fade(t, start, dur))
                A.draw_eyebrow(d, eyebrow, 110, a)
                A.draw_lines(d, title, 180, 56, a, lh=78)
                if note:
                    f = S.font(30)
                    d.text(((S.W - S.text_w(d, note, f)) // 2, 1180), note, font=f, fill=S.INK_SOFT + (a,))
        f = S.font(28)
        d.text((72, 1262), "원주 건강한치과 · 표경열 원장", font=f, fill=S.INK_SOFT + (200,))
        base = img.convert("RGBA")
        base.alpha_composite(layer)
        img = base.convert("RGB")
    d = ImageDraw.Draw(img)
    d.rectangle([0, S.H - 8, int(S.W * min(1.0, t / DUR)), S.H], fill=S.ACCENT)
    return img


def build_audio():
    """gen-sinus-lift-anim.py의 ASMR 사운드를 새 컷 타이밍에 맞춰 재배치."""
    rng, noise, env, place = A.rng, A.noise, A.env, A.place
    lp, bp = A.fir_lowpass, A.fir_bandpass
    n = int(DUR * SR)
    t = np.arange(n) / SR
    track = np.zeros(n)

    room = lp(noise(n), 260)
    room -= room.mean()
    room /= np.max(np.abs(room)) + 1e-9
    track += room * 0.085
    pad = (np.sin(2 * np.pi * 110 * t) * 0.6 + np.sin(2 * np.pi * 164.8 * t) * 0.35
           + np.sin(2 * np.pi * 220.5 * t) * 0.2)
    track += pad * (0.020 + 0.010 * np.sin(2 * np.pi * 0.06 * t)) * np.clip(t / 2.5, 0, 1)

    for t0 in SHOT_T0 + [DUR - OUTRO]:
        m = int(0.22 * SR)
        tick = np.sin(2 * np.pi * 1180 * np.arange(m) / SR) * np.exp(-np.arange(m) / (SR * 0.035))
        place(track, lp(tick, 2600, 81), t0 - 0.05, 0.05)

    s1, s2, s3, s4 = SHOT_T0[1:]
    # 1단계: 창 형성 — 버 패스 3회
    for k, off in enumerate((0.5, 1.6, 2.7)):
        m = int(0.62 * SR)
        x = np.arange(m) / SR
        bur = bp(noise(m), 320, 1150, 161) * (1 + 0.35 * np.sin(2 * np.pi * 34 * x))
        place(track, bur * env(m, 0.22, 0.45) * (0.85 - 0.12 * k), s1 + off, 0.085)

    # 2단계: 점막 거상 — 여린 마찰 + 크래클
    m = int(3.4 * SR)
    lift = bp(noise(m), 1400, 5200, 161) * env(m, 0.35, 0.45)
    lift *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.5 * np.arange(m) / SR)
    place(track, lift, s2 + 0.4, 0.045)
    for _ in range(30):
        m2 = int(0.05 * SR)
        cr = bp(noise(m2), 2200, 7000, 81) * np.exp(-np.arange(m2) / (SR * 0.010))
        place(track, cr, s2 + 0.6 + rng.random() * 3.0, 0.05 * rng.random())

    # 3단계: 뼈이식재 — 알갱이 쏟아지는 소리
    for _ in range(110):
        m2 = int(0.045 * SR)
        g = bp(noise(m2), 900, 6500, 81) * np.exp(-np.arange(m2) / (SR * 0.008))
        place(track, g, s3 + 0.3 + rng.random() ** 0.8 * 3.6, 0.075 * (0.4 + rng.random()))
    m = int(3.8 * SR)
    place(track, lp(noise(m), 700, 161) * env(m, 0.3, 0.5), s3 + 0.3, 0.030)

    # 4단계: 임플란트 식립 — 라쳇 클릭 + 착지음
    click_t, step = s4 + 0.5, 0.34
    while click_t < s4 + 3.3:
        m = int(0.12 * SR)
        c = bp(noise(m), 700, 4200, 81) * np.exp(-np.arange(m) / (SR * 0.016))
        place(track, c, click_t, 0.075)
        click_t += step
        step *= 0.93
    m = int(0.9 * SR)
    x = np.arange(m) / SR
    place(track, lp(np.sin(2 * np.pi * 88 * x) * np.exp(-x / 0.22), 900, 81), s4 + 3.4, 0.09)

    # 아웃트로: 따뜻한 패드
    m = int(OUTRO * SR)
    x = np.arange(m) / SR
    heal = (np.sin(2 * np.pi * 174.6 * x) + 0.6 * np.sin(2 * np.pi * 261.6 * x)
            + 0.35 * np.sin(2 * np.pi * 349.2 * x))
    place(track, heal * env(m, 0.35, 0.5), DUR - OUTRO, 0.045)

    track = lp(track, 12000, 81)
    track = np.tanh(track * 2.8) / 2.8
    track *= 0.90 / (np.max(np.abs(track)) + 1e-9)
    fin, fout = int(0.6 * SR), int(1.2 * SR)
    track[:fin] *= np.linspace(0, 1, fin)
    track[-fout:] *= np.linspace(1, 0, fout)
    delay = int(0.006 * SR)
    right = np.concatenate([np.zeros(delay), track[:-delay]]) * 0.96 + track * 0.04
    return np.clip(np.stack([track, right], axis=1), -1, 1)


def main():
    if not os.path.exists(os.path.join(WORK, "shot5", "f0000.png")):
        extract_clips()
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        out = os.path.join(WORK, "still_%05.1f.png" % t)
        render_frame(t).save(out)
        print("saved", out)
        return

    out_frames = os.path.join(WORK, "out")
    os.makedirs(out_frames, exist_ok=True)
    total = int(DUR * FPS)
    for i in range(total):
        render_frame(i / FPS).save(os.path.join(out_frames, "f%05d.png" % i))
        if i % 96 == 0:
            print("frame %d/%d" % (i, total))

    wav = os.path.join(WORK, "asmr.wav")
    A.write_wav(wav, build_audio())
    mp4 = os.path.join(OUT_DIR, "00_video.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
        "-i", os.path.join(out_frames, "f%05d.png"), "-i", wav,
        "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", mp4,
    ], check=True)
    print("done:", mp4, "(%.1fs)" % DUR)


if __name__ == "__main__":
    main()
