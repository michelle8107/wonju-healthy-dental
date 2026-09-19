# 건치의 하루 9탄 - 가족이 "이가 좀 아픈 것 같아"라고 할 때
# (콘텐츠 캘린더 D15 공감 리액션 + "통증 정도 != 실제 상태" 정보 + 추석 휴진 안내)
# 휴진 일정은 8탄과 동일한 사용자 확인값: 9/24(목)~9/27(일) 휴진, 9/28(월)부터 정상 진료.
import subprocess, os, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:/OneDrive/Claude_Dental Clinic"
A = ROOT + "/assets/geonchi_shorts"
FONT = A + "/fonts/Jua-Regular.ttf"
OUT = W + "/ep9.mp4"
SR = 24000

def run(args):
    subprocess.run(args, check=True)

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]).decode().strip())

# ---- picture timeline ----
# ("clip", file, ss, dur) | ("hold", dur) -> previous clip's last frame w/ slow push-in | ("logo", dur)
# s2의 표정이 굳는 순간은 원본 3.35s -> 2.75에서 잘라 4.65s(내레이션 2번 직후)에 오게 맞춤.
# s3는 0.25~4.00 설명, 4.10~5.04 따뜻한 미소 구간이라 둘을 나눠 씀.
SEGS = [
    ("clip", "s1.mp4", 0.25, 4.05),   #  0.00  통화, 밝게 웃음
    ("clip", "s2.mp4", 2.75, 2.29),   #  4.05  웃다가 귀 쫑긋, 표정 굳음
    ("hold", 1.60),                   #  6.34  걱정 정지컷
    ("clip", "s3.mp4", 0.25, 3.75),   #  7.94  손가락 들고 설명
    ("hold", 6.40),                   # 11.69  설명 정지컷: 초기 충치 / 신경
    ("clip", "s2.mp4", 3.35, 1.65),   # 18.09  걱정 컷 재사용: 이런 신호면 빨리
    ("hold", 6.70),                   # 19.74  신호 3가지 나열
    ("clip", "s3.mp4", 4.10, 0.94),   # 26.44  따뜻한 미소: 감성 마무리
    ("hold", 3.70),                   # 27.38
    ("logo", 9.40),                   # 31.08  휴진 안내 + 차임
]

# ---- narration: (file, abs start, [(caption, rel_start, rel_end), ...]) ----
NARR = [
    ("n1_t.wav", 0.35, [("엄마한테 전화가 왔어요", 0.0, 1.40),
                        ("“이가 좀 아픈 것 같아”", 1.45, 3.83)]),
    # Jua에는 ‘ ’(U+2018/2019)와 ·(U+00B7), 「」 글리프가 없어 두부로 렌더된다. “ ”는 있음.
    ("n2_t.wav", 4.60, [("근데 그 “좀”이 제일 무서워요", 0.0, 2.77)]),
    ("n3_t.wav", 7.95, [("치아는 아픈 정도랑\n실제 상태가 꼭 비례하지 않아요", 0.0, 4.18)]),
    ("n4_t.wav", 12.55, [("초기 충치는 거의 안 아프고,", 0.0, 1.85),
                         ("신경까지 간 뒤엔 오히려\n통증이 잠깐 사라지기도 해요", 1.95, 5.81)]),
    ("n5_t.wav", 18.80, [("그래서 이런 신호가 있으면\n빨리 오셔야 해요", 0.0, 3.33)]),
    ("n6_t.wav", 22.55, [("가만히 있어도 욱신거리거나,", 0.0, 1.55),
                         ("밤에 더 아프거나,", 1.65, 2.68),
                         ("씹을 때 아프면요", 2.75, 3.94)]),
    ("n7_t.wav", 27.00, [("가족이 “좀 아프다”고 말할 땐,", 0.0, 2.10),
                         ("이미 며칠 참은 거예요", 2.25, 4.07)]),
    ("n8_t.wav", 31.60, [("원주 건강한치과는\n9월 24일(목)~27일(일) 휴진", 0.0, 5.00),
                         ("28일(월)부터 정상 진료해요!", 5.10, 7.46)]),
]
TITLE = ("가족 치통", 0.0, 1.0)
THUMP_AT = 4.65     # 웃음이 굳는 순간
CHIME_AT = 39.25

TOTAL = round(sum(s[-1] for s in SEGS), 3)

# ---- 폰트에 없는 글자가 자막에 섞이면 두부(□)로 렌더되므로 빌드 전에 막는다 ----
def assert_glyphs():
    from fontTools.ttLib import TTFont
    cmap = set()
    for tbl in TTFont(FONT)["cmap"].tables:
        cmap |= set(tbl.cmap.keys())
    text = TITLE[0] + "".join(c for _, _, caps in NARR for c, _, _ in caps)
    missing = sorted({ch for ch in text if ch != "\n" and ord(ch) not in cmap})
    if missing:
        raise SystemExit("Jua 폰트에 없는 글자: " + " ".join(f"{c!r}(U+{ord(c):04X})" for c in missing))

assert_glyphs()

# ---- 긴장 thump: 낮은 사인 2연타(lub-dub), 짧고 빠른 감쇠 ----
def make_thump(path):
    sr = 48000
    d = 1.0
    t = np.arange(int(sr * d)) / sr
    sig = np.zeros_like(t)
    for at, f0, amp in [(0.00, 84, 1.0), (0.34, 74, 0.72)]:
        i = int(at * sr)
        n = int(0.16 * sr)
        tt = np.arange(n) / sr
        f = f0 * np.exp(-tt * 2.2)
        env = np.exp(-tt * 13) * np.minimum(1, tt / 0.004)
        sig[i:i + n] += np.sin(2 * np.pi * np.cumsum(f) / sr) * env * amp
    sig = sig / np.max(np.abs(sig)) * 0.9
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())

make_thump(f"{W}/thump.wav")

# ---- build picture ----
parts, last_clip = [], None
for i, seg in enumerate(SEGS):
    o = f"{W}/p{i}.mp4"
    if seg[0] == "clip":
        _, f, ss, d = seg
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{W}/{f}", "-t", str(d),
             "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24,setsar=1",
             "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", o])
        last_clip = o
    elif seg[0] == "hold":
        d = seg[1]
        lf = f"{W}/last{i}.png"
        run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.05", "-i", last_clip, "-frames:v", "1", "-update", "1", lf])
        n = int(round(d * 24))
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", lf, "-vf",
             f"scale=2880:5120:flags=lanczos,zoompan=z='1+0.08*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
             f":d=1:s=720x1280:fps=24,setsar=1", "-frames:v", str(n),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", o])
    else:
        d = seg[1]
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", A + "/geonchihan_chikwa_logo.png", "-t", str(d),
             "-vf", "fade=t=in:st=0:d=0.3,fps=24,scale=720:1280,setsar=1", "-c:v", "libx264",
             "-pix_fmt", "yuv420p", "-crf", "18", o])
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
    font = ImageFont.truetype(FONT, 150)
    bb = d.textbbox((0, 0), text, font=font, stroke_width=6)
    x = (720 - (bb[2] - bb[0])) / 2 - bb[0]
    d.text((x, 350), text, font=font, fill="white", stroke_width=6, stroke_fill=(0, 0, 0, 179))
    im.save(path)

overlays = []
title_png(TITLE[0], f"{W}/title.png")
overlays.append((f"{W}/title.png", TITLE[1], TITLE[2]))
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
run(args)

# ---- audio mix ----
srcs = [(f, at, 1.0) for f, at, _ in NARR] + [("thump.wav", THUMP_AT, 0.30), (A + "/cute_chime.wav", CHIME_AT, 0.45)]
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
