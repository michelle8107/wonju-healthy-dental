# 건치의 하루 13탄 - 위장약(PPI) 오래 먹었는데 임플란트? (건치 질문 + 원장님 실제 사진 말풍선 답변)
# 원장님 사진은 보정 없이 원형 크롭만. 원장님 대사는 자막 + ding (목소리 없음). 상시 표기: AI 캐릭터 가상 상황.
import subprocess, os, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.abspath(__file__))
A = r"D:/OneDrive/Claude_Dental Clinic/assets/geonchi_shorts"
FONT = A + "/fonts/Jua-Regular.ttf"
OUT = W + "/ep13_v3.mp4"
SR = 24000

def run(args, timeout=300):
    p = subprocess.Popen(args)
    try:
        rc = p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)])
        raise
    if rc:
        raise SystemExit(f"failed ({rc}): {args[:6]}")

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f], timeout=60).decode().strip())

# ("clip", file, ss, d) | ("still", file, t, d) | ("logo", d)
SEGS = [
    ("clip", "s1.mp4", 0.0, 5.0),    #  0.0  건치 긴장 (건치 대사 + 원장님 "어디 볼까요?")
    ("clip", "s2.mp4", 0.0, 5.0),    #  5.0  걱정 리액션 (원장님 "임플란트 고려...")
    ("still", "s3.mp4", 0.6, 2.9),   # 10.0  눈물 정지컷 (건치 대사)
    ("clip", "s3.mp4", 0.6, 3.1),    # 12.9  눈물 -> 귀 쫑긋
    ("clip", "s3.mp4", 3.8, 1.2),    # 16.0  희망 미소 (원장님 답변 1)
    ("still", "s3.mp4", 5.0, 6.8),   # 17.2  미소 정지컷
    ("clip", "s4.mp4", 0.0, 3.6),    # 23.0  수첩에 적는 건치 (원장님 답변 2)
    ("still", "s4.mp4", 3.5, 3.2),   # 27.6
    ("clip", "s4.mp4", 3.6, 1.45),   # 28.2  엄지척 (건치 대사)
    ("still", "s4.mp4", 5.0, 2.2),   # 29.65
    ("logo", 3.4),                   # 31.85
]
T_LOGO = round(sum(s[-1] for s in SEGS[:-1]), 3)
TOTAL = round(T_LOGO + SEGS[-1][-1], 3)

DISCLOSURE = "AI 캐릭터를 활용한 가상 상황, 일반적인 건강정보"
TITLE = ("약 복용", 0.0, 1.0)

# 건치 자막 (검은 상자) / 원장님 자막 (흰 상자 + 사진 말풍선)
GEONCHI_CAPS = [
    ("저 많이 썩었나요?", 0.4, 2.5),
    ("저 위장약을 굉장히\n오랫동안 먹었어요", 10.15, 13.4),
    ("약 오래 먹으면\n임플란트 못 하나요?", 13.75, 16.0),
    ("다음 예약 때\n약 목록 정리해 올게요!", 30.95, 34.3),
]
DOCTOR_CAPS = [
    ("어디 볼까요?", 2.65, 4.1),
    ("아이구, 임플란트를 고려해야\n할 것 같아요. 혹시 드시는\n약 있어요?", 5.15, 9.5),
    ("약을 드신다고 못 하는 건 아니에요.\n위산 억제제(PPI)와 임플란트 실패의\n연관성을 보고한 연구가 있지만,\n약이 원인으로 확정된 건 아니에요.", 16.1, 23.8),
    ("약 이름, 복용량과 기간,\n골다공증 약 복용 또는 주사 여부를\n알려 주세요. 약은 임의로\n끊지 마세요.", 24.1, 30.8),
]
END_CAP = ("복용 중인 약을 진료 때 알려 주세요.\n임플란트 가능 여부와 치료 계획은\n진찰 후 개별적으로 판단합니다", T_LOGO + 0.15, TOTAL - 0.15)

NARR = [  # (file, trim a, trim b, tempo, at)
    ("n1.wav", 1.0, 2.9, 1.0, 0.4),
    ("n2.wav", 0.2, 7.13, 1.15, 10.1),
    ("n3.wav", 0.2, 4.0, 1.1, 30.9),
    ("d1.wav", 0.0, 0.94, 1.0, 2.7),
    ("d2.wav", 0.0, 4.14, 1.0, 5.2),
    ("d3.wav", 0.0, 8.32, 1.1, 16.15),
    ("d4.wav", 0.0, 7.43, 1.12, 24.15),
]
DING_AT = []
CHIME_AT = T_LOGO + 0.3

def assert_glyphs():
    from fontTools.ttLib import TTFont
    cmap = set()
    for tbl in TTFont(FONT)["cmap"].tables:
        cmap |= set(tbl.cmap.keys())
    text = TITLE[0] + DISCLOSURE + END_CAP[0] + "".join(c[0] for c in GEONCHI_CAPS + DOCTOR_CAPS) + "원장님"
    missing = sorted({ch for ch in text if ch != "\n" and ord(ch) not in cmap})
    if missing:
        raise SystemExit("Jua 폰트에 없는 글자: " + " ".join(f"{c!r}(U+{ord(c):04X})" for c in missing))
assert_glyphs()

def make_ding(path):
    sr = 48000
    t = np.arange(int(sr * 0.7)) / sr
    f = 900 + 1500 * np.minimum(t / 0.12, 1)
    sig = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 7)
    for at, f0 in [(0.10, 2637), (0.17, 3136), (0.24, 3951)]:
        tt = np.clip(t - at, 0, None)
        sig += 0.35 * np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 14) * (t >= at)
    sig = sig / np.max(np.abs(sig)) * 0.8
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())
make_ding(f"{W}/ding.wav")

enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18"]
vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24,setsar=1"
parts = []
for i, seg in enumerate(SEGS):
    o = f"{W}/p{i}.mp4"
    if seg[0] == "clip":
        _, f, ss, d = seg
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{W}/{f}", "-t", str(d), "-vf", vf, "-an"] + enc + [o])
    elif seg[0] == "still":
        _, f, t, d = seg
        lf = f"{W}/still{i}.png"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", f"{W}/{f}", "-frames:v", "1",
             "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280", "-update", "1", lf])
        n = int(round(d * 24))
        run(["ffmpeg", "-v", "error", "-y", "-i", lf, "-vf",
             f"scale=2880:5120:flags=lanczos,zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
             f":d={n}:s=720x1280:fps=24,setsar=1", "-t", str(d)] + enc + [o])
    else:
        d = seg[1]
        n = int(round(d * 24))
        run(["ffmpeg", "-v", "error", "-y", "-i", A + "/geonchihan_chikwa_logo.png", "-vf",
             f"scale=720:1280,setsar=1,loop={n}:1:0,fps=24,fade=t=in:st=0:d=0.3", "-t", str(d)] + enc + [o])
    parts.append(o)
with open(f"{W}/concat.txt", "w", encoding="utf-8") as fh:
    for p in parts:
        fh.write(f"file '{p}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/concat.txt"] + enc + [f"{W}/picture.mp4"])

def fit_font(d, lines, size, maxw=640, minsize=34):
    font = ImageFont.truetype(FONT, size)
    while max(d.textbbox((0, 0), ln, font=font)[2] for ln in lines) > maxw and size > minsize:
        size -= 2
        font = ImageFont.truetype(FONT, size)
    return font, size

def caption_png(text, path, doctor=False):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = text.split("\n")
    font, size = fit_font(d, lines, 46 if len(lines) < 3 else 42)
    n = len(lines)
    box_h = {1: 130, 2: 185, 3: 245, 4: 300}[n]
    box_y = 1125 - box_h if n > 1 else 978
    if n == 1:
        box_y, box_h = 978, 130
    fill = (255, 255, 255, 235) if doctor else (0, 0, 0, int(255 * 0.55))
    ink = (16, 30, 51) if doctor else "white"
    d.rectangle([0, box_y, 720, box_y + box_h], fill=fill)
    line_h = size + 14
    y0 = box_y + (box_h - (line_h * n - 14)) / 2
    for k, ln in enumerate(lines):
        bb = d.textbbox((0, 0), ln, font=font)
        d.text(((720 - (bb[2] - bb[0])) / 2 - bb[0], y0 + k * line_h - bb[1] + (size - (bb[3] - bb[1])) / 2),
               ln, font=font, fill=ink)
    if doctor:
        lab_font = ImageFont.truetype(FONT, 34)
        label = "원장님"
        lw = d.textbbox((0, 0), label, font=lab_font)[2]
        d.rounded_rectangle([30, 70, 30 + lw + 50, 130], 30, fill=(46, 122, 120, 255))
        d.text((55, 74), label, font=lab_font, fill="white")
    im.save(path)

def title_png(text, path):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    size = 150
    font = ImageFont.truetype(FONT, size)
    while d.textbbox((0, 0), text, font=font, stroke_width=6)[2] > 660:
        size -= 6
        font = ImageFont.truetype(FONT, size)
    bb = d.textbbox((0, 0), text, font=font, stroke_width=6)
    d.text(((720 - (bb[2] - bb[0])) / 2 - bb[0], 350), text, font=font, fill="white",
           stroke_width=6, stroke_fill=(0, 0, 0, 179))
    im.save(path)

def disclosure_png(path):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, 26)
    bb = d.textbbox((0, 0), DISCLOSURE, font=font)
    x = (720 - (bb[2] - bb[0])) / 2 - bb[0]
    d.text((x, 1175), DISCLOSURE, font=font, fill="white", stroke_width=3, stroke_fill=(0, 0, 0, 200))
    im.save(path)

overlays = []
title_png(TITLE[0], f"{W}/title.png"); overlays.append((f"{W}/title.png", TITLE[1], TITLE[2]))
disclosure_png(f"{W}/disc.png"); overlays.append((f"{W}/disc.png", 1.0, TOTAL))
for i, (t, s, e) in enumerate(GEONCHI_CAPS):
    caption_png(t, f"{W}/gcap{i}.png"); overlays.append((f"{W}/gcap{i}.png", s, e))
for i, (t, s, e) in enumerate(DOCTOR_CAPS):
    caption_png(t, f"{W}/dcap{i}.png", doctor=True); overlays.append((f"{W}/dcap{i}.png", s, e))
caption_png(END_CAP[0], f"{W}/endcap.png"); overlays.append((f"{W}/endcap.png", END_CAP[1], END_CAP[2]))

args = ["ffmpeg", "-v", "error", "-y", "-i", f"{W}/picture.mp4"]
for pth, _, _ in overlays:
    args += ["-i", pth]
chain, prev = [], "[0:v]"
for k, (_, s, e) in enumerate(overlays, start=1):
    chain.append(f"{prev}[{k}:v]overlay=0:0:enable='between(t,{round(s,2)},{round(e,2)})'[v{k}]")
    prev = f"[v{k}]"
run(args + ["-filter_complex", ";".join(chain), "-map", prev] + enc + [f"{W}/captioned.mp4"], timeout=900)

args = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", str(TOTAL), "-i", f"anullsrc=r={SR}:cl=mono"]
ins = [f"{W}/{f}" for f, *_ in NARR] + [f"{W}/ding.wav"] * len(DING_AT) + [A + "/cute_chime.wav"]
for f in ins:
    args += ["-i", f]
fl, labs = [], ["[0:a]"]
k = 1
for f, a, b, tempo, at in NARR:
    ms = int(at * 1000)
    fl.append(f"[{k}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={tempo},aformat=sample_rates={SR}:channel_layouts=mono,adelay={ms}|{ms}[a{k}]")
    labs.append(f"[a{k}]"); k += 1
for at in DING_AT:
    ms = int(at * 1000)
    fl.append(f"[{k}:a]aformat=sample_rates={SR}:channel_layouts=mono,volume=0.3,adelay={ms}|{ms}[a{k}]")
    labs.append(f"[a{k}]"); k += 1
ms = int(CHIME_AT * 1000)
fl.append(f"[{k}:a]aformat=sample_rates={SR}:channel_layouts=mono,volume=0.45,adelay={ms}|{ms}[a{k}]")
labs.append(f"[a{k}]")
fl.append("".join(labs) + f"amix=inputs={len(labs)}:duration=first:normalize=0,atrim=0:{TOTAL}[aout]")
run(args + ["-filter_complex", ";".join(fl), "-map", "[aout]", "-c:a", "pcm_s16le", f"{W}/mix.wav"])
run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/captioned.mp4", "-i", f"{W}/mix.wav", "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT])
print("done", OUT, dur(OUT), "total", TOTAL, "chime end", round(CHIME_AT + dur(A + "/cute_chime.wav"), 2))
