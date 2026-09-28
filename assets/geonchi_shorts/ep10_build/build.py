# 건치의 하루 10탄 - 퇴근하면 닫혀 있고, 점심엔 붐비고... 공휴일 정상진료 발견!
# 사용자 확인 일정(2026-09-28): 10/3(토) 개천절, 10/5(월) 대체공휴일, 10/9(금) 한글날 정상진료,
# 10/14(수)~10/18(일) 학회 세미나로 휴진.
import subprocess, os, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont
from card import card

W = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:/OneDrive/Claude_Dental Clinic"
A = ROOT + "/assets/geonchi_shorts"
FONT = A + "/fonts/Jua-Regular.ttf"
OUT = W + "/ep10.mp4"
SR = 24000

def run(args, timeout=300):
    # 시간 초과 시 프로세스 트리 전체 종료 (전역 CLAUDE.md 규칙)
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

# ---- picture timeline ----
# ("clip", file, ss, dur) | ("hold", dur): 직전 클립 마지막 프레임 슬로우 줌
# ("still", file, t, dur): 해당 파일 t초 프레임 슬로우 줌 | ("logo", dur)
SEGS = [
    ("clip", "s1.mp4", 1.60, 3.44),   #  0.00  야근 중 볼 잡고 아파함
    ("hold", 2.50),                   #  3.44
    ("clip", "s2.mp4", 0.25, 4.79),   #  5.94  밤길 달려가 닫힌 문
    ("clip", "s3.mp4", 0.60, 4.44),   # 10.73  점심시간 꽉 찬 대기실
    ("hold", 1.70),                   # 15.17
    ("still", "s4.mp4", 0.30, 1.60),  # 16.87  소파에서 폰 (시무룩)
    ("clip", "s4.mp4", 0.25, 4.79),   # 18.47  -> 20.47 눈 반짝(엇!) -> 점프
    ("hold", 5.90),                   # 23.26  점프 정지컷 + 10월 진료 안내 카드
    ("clip", "s4.mp4", 3.00, 2.04),   # 29.16  다시 신나서 점프
    ("hold", 2.00),                   # 31.20
    ("logo", 11.60),                  # 33.20  학회 휴진 안내 + 차임
]

NARR = [
    ("n1_t.wav", 1.00, [("아야, 이가 욱신거려요", 0.0, 1.71),
                        ("근데 퇴근은 아직 멀었어요", 2.00, 4.61)]),
    ("n2_t.wav", 6.10, [("퇴근하자마자 달려왔는데,", 0.0, 1.91),
                        ("벌써 문이 닫혀 있어요", 2.20, 3.80)]),
    ("n3_t.wav", 10.95, [("점심시간에 가 보면,", 0.0, 1.66),
                         ("병원도 점심시간이거나\n사람이 너무 많아요", 1.98, 5.42)]),
    ("n4_t.wav", 16.95, [("쉬는 날 진료하는 치과는 없을까?", 0.0, 3.23),
                         ("엇!", 3.40, 4.15)]),
    ("n5_t.wav", 21.50, [("건강한치과는 10월 3일, 5일, 9일", 0.0, 4.15),
                         ("공휴일에도 정상 진료한대요!", 4.40, 7.10)]),
    ("n6_t.wav", 29.35, [("와! 밀린 치료 다 해야겠어요!\n스케일링도 하고, 충치 치료도 하고!", 0.0, 3.76)]),
    ("n7_t.wav", 33.60, [("10월 14일부터 18일까지는\n학회 세미나로 쉬어요", 0.0, 4.31)]),
    ("n8_t.wav", 38.20, [("공부를 쉬지 않는 건강한치과예요!", 0.0, 2.95),
                         ("미리 예약하고 오세요!", 3.27, 4.84)]),
]
TITLE = ("공휴일 진료", 0.0, 1.0)
CARD_AT = (21.40, 29.10)       # 10월 진료 안내 카드 표시 구간
DING_AT = 20.35       # "엇!" 반짝 효과음
CHIME_AT = 43.20

TOTAL = round(sum(s[-1] for s in SEGS), 3)

def assert_glyphs(extra=""):
    from fontTools.ttLib import TTFont
    cmap = set()
    for tbl in TTFont(FONT)["cmap"].tables:
        cmap |= set(tbl.cmap.keys())
    text = TITLE[0] + extra + "".join(c for _, _, caps in NARR for c, _, _ in caps)
    missing = sorted({ch for ch in text if ch != "\n" and ord(ch) not in cmap})
    if missing:
        raise SystemExit("Jua 폰트에 없는 글자: " + " ".join(f"{c!r}(U+{ord(c):04X})" for c in missing))

assert_glyphs(card(f"{W}/card.png"))

# ---- "엇!" 반짝: 빠르게 올라가는 사인 스윕 + 고음 반짝이 ----
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

def zoom_still(img, d, o):
    # 이미지 한 장 입력 + zoompan d=프레임수, -t로 길이 고정 (-loop 1 과 zoompan 동시 사용 금지)
    n = int(round(d * 24))
    run(["ffmpeg", "-v", "error", "-y", "-i", img, "-vf",
         f"scale=2880:5120:flags=lanczos,zoompan=z='1+0.08*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
         f":d={n}:s=720x1280:fps=24,setsar=1", "-t", str(d),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", o])

parts, last_clip = [], None
for i, seg in enumerate(SEGS):
    o = f"{W}/p{i}.mp4"
    if seg[0] == "clip":
        _, f, ss, d = seg
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{W}/{f}", "-t", str(d),
             "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24,setsar=1",
             "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", o])
        last_clip = o
    elif seg[0] in ("hold", "still"):
        lf = f"{W}/last{i}.png"
        if seg[0] == "hold":
            d = seg[1]
            run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.05", "-i", last_clip, "-frames:v", "1", "-update", "1", lf])
        else:
            _, f, t, d = seg
            run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", f"{W}/{f}", "-frames:v", "1",
                 "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280", "-update", "1", lf])
        zoom_still(lf, d, o)
    else:
        d = seg[1]
        n = int(round(d * 24))
        run(["ffmpeg", "-v", "error", "-y", "-i", A + "/geonchihan_chikwa_logo.png",
             "-vf", f"scale=720:1280,setsar=1,loop={n}:1:0,fps=24,fade=t=in:st=0:d=0.3", "-t", str(d),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", o])
    parts.append(o)
with open(f"{W}/concat.txt", "w", encoding="utf-8") as fh:
    for p in parts:
        fh.write(f"file '{p}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/concat.txt",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", f"{W}/picture.mp4"])

# ---- captions (PIL; drawtext는 이 머신에서 segfault - 스킬 문서 참고) ----
def caption_png(text, path):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = text.split("\n")
    size = 46
    font = ImageFont.truetype(FONT, size)
    widest = lambda f: max(d.textbbox((0, 0), ln, font=f)[2] for ln in lines)
    while widest(font) > 660 and size > 34:
        size -= 2
        font = ImageFont.truetype(FONT, size)
    if len(lines) == 1:
        box_y, box_h = 978, 130
    else:
        box_y, box_h = 940, 185
    d.rectangle([0, box_y, 720, box_y + box_h], fill=(0, 0, 0, int(255 * 0.55)))
    line_h = size + 14
    block_h = line_h * len(lines) - 14
    y0 = box_y + (box_h - block_h) / 2
    for k, ln in enumerate(lines):
        bb = d.textbbox((0, 0), ln, font=font)
        x = (720 - (bb[2] - bb[0])) / 2 - bb[0]
        d.text((x, y0 + k * line_h - bb[1] + (size - (bb[3] - bb[1])) / 2), ln, font=font, fill="white")
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
    x = (720 - (bb[2] - bb[0])) / 2 - bb[0]
    d.text((x, 350), text, font=font, fill="white", stroke_width=6, stroke_fill=(0, 0, 0, 179))
    im.save(path)

overlays = []
title_png(TITLE[0], f"{W}/title.png")
overlays.append((f"{W}/title.png", TITLE[1], TITLE[2]))
overlays.append((f"{W}/card.png", CARD_AT[0], CARD_AT[1]))
ci = 0
for f, at, caps in NARR:
    for text, rs, re_ in caps:
        pth = f"{W}/cap{ci}.png"; ci += 1
        caption_png(text, pth)
        overlays.append((pth, round(at + rs, 2), round(at + re_, 2)))

args = ["ffmpeg", "-v", "error", "-y", "-i", f"{W}/picture.mp4"]
for pth, _, _ in overlays:
    args += ["-i", pth]
chain, prev = [], "[0:v]"
for k, (_, s, e) in enumerate(overlays, start=1):
    lab = f"[v{k}]"
    chain.append(f"{prev}[{k}:v]overlay=0:0:enable='between(t,{s},{e})'{lab}")
    prev = lab
args += ["-filter_complex", ";".join(chain), "-map", prev, "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-crf", "18", f"{W}/captioned.mp4"]
run(args, timeout=600)

# ---- audio mix ----
srcs = [(f, at, 1.0) for f, at, _ in NARR] + [("ding.wav", DING_AT, 0.35), (A + "/cute_chime.wav", CHIME_AT, 0.45)]
args = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", str(TOTAL), "-i", f"anullsrc=r={SR}:cl=mono"]
for f, _, _ in srcs:
    args += ["-i", f if os.path.isabs(f) else f"{W}/{f}"]
fl, labs = [], ["[0:a]"]
for k, (f, at, vol) in enumerate(srcs, start=1):
    ms = int(at * 1000)
    fl.append(f"[{k}:a]aformat=sample_rates={SR}:channel_layouts=mono,volume={vol},adelay={ms}|{ms}[a{k}]")
    labs.append(f"[a{k}]")
fl.append("".join(labs) + f"amix=inputs={len(labs)}:duration=first:normalize=0,atrim=0:{TOTAL}[aout]")
args += ["-filter_complex", ";".join(fl), "-map", "[aout]", "-c:a", "pcm_s16le", f"{W}/mix.wav"]
run(args)

run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/captioned.mp4", "-i", f"{W}/mix.wav",
     "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT])

# sanity: 내레이션이 다음 줄과 겹치지 않고, 자막 창이 오디오보다 오래 남지 않는지
for (f, at, caps), nxt in zip(NARR, NARR[1:] + [(None, CHIME_AT, None)]):
    d = dur(f"{W}/{f}")
    end = at + d
    cap_end = at + caps[-1][2]
    flag = "OVERLAP" if end > nxt[1] else ("CAP>AUDIO" if cap_end > end + 0.05 else "ok")
    print(f"{f:10s} {at:6.2f} -> {end:6.2f}  cap_end {cap_end:6.2f}  next {nxt[1]:6.2f}  {flag}")
print("chime end", round(CHIME_AT + dur(A + "/cute_chime.wav"), 2), "total", TOTAL)
print("done", OUT, dur(OUT))
