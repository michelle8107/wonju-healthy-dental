# -*- coding: utf-8 -*-
"""
상악동 거상술 + 뼈이식 모식도 애니메이션 (1080x1350, 24fps, ~30초)
캐러셀 1번 슬롯에 들어가는 그래피컬 영상. ASMR 사운드 동기 합성.

  python gen-sinus-lift-anim.py            # 프레임 + 오디오 + mp4
  python gen-sinus-lift-anim.py --still 12 # 12초 지점 한 장만 미리보기

출력: assets/instagram_carousels/sinus_lift_bonegraft/00_video.mp4
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw

import sinus_lift_diagram as S

FPS = 24
SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "..", "assets", "instagram_carousels", "sinus_lift_bonegraft")
WORK = os.path.join(HERE, "_sinus_anim_frames")

# ── 장면표 (start, dur, eyebrow, title lines, note) ───────────────────
SCENES = [
    (0.0, 2.8, None, ["임플란트 뼈이식,", "이렇게 합니다"], "상악동 거상술 · 측방 접근 모식도"),
    (2.8, 3.2, "여기가 어디냐면", ["위쪽 어금니 위에는", "'상악동'이라는 빈 공간이 있습니다"], None),
    (6.0, 2.8, "뼈이식을 하는 이유", ["상악동 아래 남은 뼈가 얇으면", "임플란트를 바로 심기 어렵습니다"], None),
    (8.8, 3.0, "1단계", ["볼쪽 뼈에 작은 창을 만듭니다"], "측방 접근 (lateral window)"),
    (11.8, 3.4, "2단계", ["상악동 점막을", "찢어지지 않게 들어올립니다"], None),
    (15.2, 3.4, "3단계", ["들어올린 공간에", "뼈이식재를 채웁니다"], None),
    (18.6, 2.6, "4단계", ["창을 차폐막으로 덮고", "잇몸을 봉합합니다"], None),
    (21.2, 3.0, "5단계", ["치유 기간을 거치며", "이식재가 뼈로 바뀝니다"], "※ 필요한 기간은 개인의 상태에 따라 다릅니다"),
    (24.2, 3.2, "6단계", ["자리 잡은 뼈에", "임플란트를 식립합니다"], "※ 뼈 상태에 따라 식립을 함께 하기도 합니다"),
    (27.4, 3.0, None, ["원주 건강한치과"], None),
]
DUR = SCENES[-1][0] + SCENES[-1][1]

# 파라미터 애니메이션 구간 (이름: 시작, 끝)
PARAM_WINDOWS = {
    "anat": (2.6, 3.5),
    "window": (9.1, 11.3),
    "lift": (12.1, 14.8),
    "graft": (15.5, 18.2),
    "cover": (18.9, 20.8),
    "mature": (21.5, 23.9),
    "implant": (24.6, 27.0),
}


def p(name, t):
    a, b = PARAM_WINDOWS[name]
    return S.ease((t - a) / (b - a)) if b > a else 0.0


def scene_at(t):
    for i, sc in enumerate(SCENES):
        if sc[0] <= t < sc[0] + sc[1]:
            return i, sc
    return len(SCENES) - 1, SCENES[-1]


def fade(t, start, dur, fin=0.35, fout=0.3):
    """장면 안에서의 자막 페이드."""
    u = t - start
    if u < fin:
        return S.ease(u / fin)
    if u > dur - fout:
        return S.ease(max(0.0, (dur - u) / fout))
    return 1.0


# ── 자막/프레임 ──────────────────────────────────────────────────────
def draw_eyebrow(d, text, y, a):
    f = S.font(36, "Bold")
    tw = S.text_w(d, text, f)
    x = (S.W - (12 + 22 + tw)) // 2
    d.rectangle([x, y, x + 12, y + 42], fill=S.ACCENT + (a,))
    d.text((x + 34, y - 2), text, font=f, fill=S.ACCENT + (a,))


def draw_lines(d, lines, y, size, a, weight="Bold", color=None, lh=None):
    f = S.font(size, weight)
    lh = lh or int(size * 1.34)
    color = color or S.INK
    for i, line in enumerate(lines):
        d.text(((S.W - S.text_w(d, line, f)) // 2, y + i * lh), line, font=f, fill=color + (a,))
    return y + len(lines) * lh


def render_frame(t):
    idx, (start, dur, eyebrow, title, note) = scene_at(t)
    st = {k: p(k, t) for k in PARAM_WINDOWS}
    img, _ = S.new_canvas()

    intro, outro = idx == 0, idx == len(SCENES) - 1
    if outro:
        st["anat"] = 1.0 - S.ease((t - start) / 0.8)
    if not intro and st["anat"] > 0.01:
        img = S.draw_anatomy(img, st)
    if idx == 2:
        img = S.draw_height_arrow(img, fade(t, start, dur) * 0.95)
    if idx == 1:
        a = fade(t, start, dur)
        img = S.draw_label(img, "잇몸뼈 (치조골)", (720, 812), (700, 1048), side="left", alpha=a)
        img = S.draw_label(img, "잇몸", (420, 900), (196, 1120), side="right", alpha=a)
    if idx == 4:
        img = S.draw_label(img, "상악동 점막", (676, 664), (688, 1048), side="left",
                           alpha=fade(t, start, dur))

    layer = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a = int(255 * (1.0 if intro and t < 0.4 else fade(t, start, dur)))

    if idx == 1 and a > 0:  # 상악동 공기 공간 안에 직접 라벨
        f = S.font(40, "Bold")
        d.text(((S.W - S.text_w(d, "상악동", f)) // 2, 500), "상악동", font=f, fill=S.INK + (a,))
        f2 = S.font(30)
        d.text(((S.W - S.text_w(d, "(공기가 차 있는 빈 공간)", f2)) // 2, 556),
               "(공기가 차 있는 빈 공간)", font=f2, fill=S.INK_SOFT + (a,))

    if intro:
        draw_eyebrow(d, "원주 건강한치과 · 모식도", 470, a)
        bottom = draw_lines(d, title, 552, 84, a)
        x = (S.W - 150) // 2
        d.rectangle([x, bottom + 26, x + 150, bottom + 36], fill=S.ACCENT + (a,))
        f = S.font(36)
        d.text(((S.W - S.text_w(d, note, f)) // 2, bottom + 76), note, font=f, fill=S.INK_SOFT + (a,))
    elif outro:
        draw_eyebrow(d, "상악동 거상술 · 뼈이식", 452, a)
        bottom = draw_lines(d, title, 534, 78, a)
        x = (S.W - 150) // 2
        d.rectangle([x, bottom + 26, x + 150, bottom + 36], fill=S.ACCENT + (a,))
        f = S.font(34)
        for i, line in enumerate(["이 영상은 일반적인 정보 제공을 위한 것으로,",
                                  "실제 치료 방법과 기간은 검사 결과에 따라 달라집니다."]):
            d.text(((S.W - S.text_w(d, line, f)) // 2, bottom + 80 + i * 50), line,
                   font=f, fill=S.INK_SOFT + (a,))
        f2 = S.font(32)
        d.text(((S.W - S.text_w(d, "원주시 건강로 21, 2층 · TEL 033-734-2275", f2)) // 2, bottom + 216),
               "원주시 건강로 21, 2층 · TEL 033-734-2275", font=f2, fill=S.INK_SOFT + (a,))
    else:
        if eyebrow:
            draw_eyebrow(d, eyebrow, 120, a)
        draw_lines(d, title, 190, 54, a, lh=76)
        if note:
            f = S.font(30)
            d.text(((S.W - S.text_w(d, note, f)) // 2, 1148), note, font=f, fill=S.INK_SOFT + (a,))

    # 하단 고정 요소
    if not intro:
        f = S.font(28)
        d.text((72, 1258), "원주 건강한치과 · 표경열 원장", font=f, fill=S.INK_SOFT + (190,))
    d.rectangle([0, S.H - 8, int(S.W * min(1.0, t / DUR)), S.H], fill=S.ACCENT + (255,))

    base = img.convert("RGBA")
    base.alpha_composite(layer)
    return base.convert("RGB")


# ── ASMR 오디오 ──────────────────────────────────────────────────────
rng = np.random.default_rng(20260917)


def fir_lowpass(sig, fc, taps=201):
    n = np.arange(taps) - (taps - 1) / 2
    h = np.sinc(2 * fc / SR * n) * np.hanning(taps)
    return np.convolve(sig, h / h.sum(), mode="same")


def fir_bandpass(sig, lo, hi, taps=201):
    return fir_lowpass(sig, hi, taps) - fir_lowpass(sig, lo, taps)


def noise(n):
    return rng.standard_normal(n)


def env(n, attack, release):
    """0..1 구간 엔벨로프 (샘플 수 기준 비율)."""
    e = np.ones(n)
    a, r = max(1, int(n * attack)), max(1, int(n * release))
    e[:a] = np.linspace(0, 1, a) ** 1.5
    e[-r:] = np.linspace(1, 0, r) ** 1.5
    return e


def place(track, sig, t0, gain=1.0):
    i = int(t0 * SR)
    j = min(len(track), i + len(sig))
    if i < len(track):
        track[i:j] += sig[: j - i] * gain


def build_audio():
    n = int(DUR * SR)
    t = np.arange(n) / SR
    track = np.zeros(n)

    # 룸톤: 아주 낮고 일정한 어두운 노이즈
    # (cumsum 브라운 노이즈는 랜덤워크라 뒤로 갈수록 레벨이 커져 장면별 음량이 들쭉날쭉해진다)
    room = fir_lowpass(noise(n), 260)
    room -= room.mean()
    room /= np.max(np.abs(room)) + 1e-9
    track += room * 0.085

    # 따뜻한 패드 (아주 약하게, 천천히 흔들리며)
    pad = (np.sin(2 * np.pi * 110 * t) * 0.6 + np.sin(2 * np.pi * 164.8 * t) * 0.35
           + np.sin(2 * np.pi * 220.5 * t) * 0.2)
    track += pad * (0.020 + 0.010 * np.sin(2 * np.pi * 0.06 * t)) * np.clip(t / 2.5, 0, 1)

    # 장면 전환 틱
    for (start, _, _, _, _) in SCENES[1:]:
        m = int(0.22 * SR)
        tick = np.sin(2 * np.pi * 1180 * np.arange(m) / SR) * np.exp(-np.arange(m) / (SR * 0.035))
        place(track, fir_lowpass(tick, 2600, 81), start - 0.05, 0.05)

    # 1단계: 창 형성 — 부드러운 버(bur) 패스 3회
    for k, t0 in enumerate((9.25, 10.05, 10.8)):
        m = int(0.62 * SR)
        x = np.arange(m) / SR
        bur = fir_bandpass(noise(m), 320, 1150, 161)
        bur *= 1 + 0.35 * np.sin(2 * np.pi * 34 * x)          # 회전 떨림
        bur *= env(m, 0.22, 0.45) * (0.85 - 0.12 * k)
        place(track, bur, t0, 0.085)

    # 2단계: 점막 거상 — 아주 여린 마찰 + 미세 크래클
    m = int(2.6 * SR)
    lift = fir_bandpass(noise(m), 1400, 5200, 161) * env(m, 0.35, 0.45)
    lift *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.5 * np.arange(m) / SR)
    place(track, lift, 12.1, 0.045)
    for _ in range(26):
        t0 = 12.3 + rng.random() * 2.3
        m2 = int(0.05 * SR)
        cr = fir_bandpass(noise(m2), 2200, 7000, 81) * np.exp(-np.arange(m2) / (SR * 0.010))
        place(track, cr, t0, 0.05 * rng.random())

    # 3단계: 뼈이식재 채우기 — 알갱이 쏟아지는 소리
    for _ in range(90):
        t0 = 15.5 + rng.random() ** 0.8 * 2.5
        m2 = int(0.045 * SR)
        g = fir_bandpass(noise(m2), 900, 6500, 81) * np.exp(-np.arange(m2) / (SR * 0.008))
        place(track, g, t0, 0.075 * (0.4 + rng.random()))
    m = int(2.6 * SR)
    place(track, fir_lowpass(noise(m), 700, 161) * env(m, 0.3, 0.5), 15.5, 0.030)

    # 4단계: 차폐막 덮기 + 봉합 — 천 스치는 소리 2회 + 실 당김 3회
    for t0 in (19.0, 19.9):
        m = int(0.8 * SR)
        sw = fir_bandpass(noise(m), 500, 3000, 161) * env(m, 0.4, 0.5)
        place(track, sw, t0, 0.055)
    for t0 in (20.0, 20.32, 20.62):
        m = int(0.18 * SR)
        th = fir_bandpass(noise(m), 1800, 6000, 81) * np.exp(-np.arange(m) / (SR * 0.035))
        place(track, th, t0, 0.05)

    # 5단계: 치유 — 따뜻한 상승 패드
    m = int(3.0 * SR)
    x = np.arange(m) / SR
    heal = (np.sin(2 * np.pi * 174.6 * x) + 0.6 * np.sin(2 * np.pi * 261.6 * x)
            + 0.35 * np.sin(2 * np.pi * 349.2 * x))
    place(track, heal * env(m, 0.45, 0.4), 21.3, 0.045)

    # 6단계: 임플란트 식립 — 느린 라쳇 클릭 + 낮은 착지음
    click_t = 24.7
    step = 0.30
    while click_t < 26.5:
        m = int(0.12 * SR)
        c = fir_bandpass(noise(m), 700, 4200, 81) * np.exp(-np.arange(m) / (SR * 0.016))
        place(track, c, click_t, 0.075)
        click_t += step
        step *= 0.92
    m = int(0.9 * SR)
    x = np.arange(m) / SR
    thunk = np.sin(2 * np.pi * 88 * x) * np.exp(-x / 0.22)
    place(track, fir_lowpass(thunk, 900, 81), 26.55, 0.09)

    # 마스터: 부드럽게 눌러주고 페이드
    track = fir_lowpass(track, 12000, 81)
    track = np.tanh(track * 2.8) / 2.8
    peak = np.max(np.abs(track)) + 1e-9
    track *= 0.90 / peak
    fin, fout = int(0.6 * SR), int(1.2 * SR)
    track[:fin] *= np.linspace(0, 1, fin)
    track[-fout:] *= np.linspace(1, 0, fout)

    # 살짝 넓은 스테레오 (ASMR 느낌)
    delay = int(0.006 * SR)
    left = track.copy()
    right = np.concatenate([np.zeros(delay), track[:-delay]]) * 0.96 + track * 0.04
    stereo = np.stack([left, right], axis=1)
    return np.clip(stereo, -1, 1)


def write_wav(path, stereo):
    data = (stereo * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def main():
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        out = os.path.join(WORK, "still_%05.1f.png" % t)
        os.makedirs(WORK, exist_ok=True)
        render_frame(t).save(out)
        print("saved", out)
        return

    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    total = int(DUR * FPS)
    for i in range(total):
        render_frame(i / FPS).save(os.path.join(WORK, "f%05d.png" % i))
        if i % 60 == 0:
            print("frame %d/%d" % (i, total))

    wav = os.path.join(WORK, "asmr.wav")
    write_wav(wav, build_audio())
    print("audio:", wav)

    mp4 = os.path.join(OUT_DIR, "00_video.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(WORK, "f%05d.png"),
        "-i", wav,
        "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", mp4,
    ], check=True)
    print("done:", mp4)


if __name__ == "__main__":
    main()
