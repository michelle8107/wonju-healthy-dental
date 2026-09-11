# 건치의 하루 7탄 v2 - 추석 간식 (D10), 정보 강화판
# 영상은 v1 씬 그대로, 설명 대사 구간은 앞 씬 마지막 프레임을 슬로우 줌 정지컷으로 늘려서 확보.
import subprocess, os, sys, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:/OneDrive/Claude_Dental Clinic"
A = ROOT + "/assets/geonchi_shorts"
FONT = A + "/fonts/Jua-Regular.ttf"
OUT = W + "/ep7_v2.mp4"
SR = 24000

def run(args):
    subprocess.run(args, check=True)

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]).decode().strip())

# ---- picture timeline ----
# ("clip", file, ss, dur) | ("hold", dur)  -> freezes previous clip's last frame w/ slow push-in | ("logo", dur)
SEGS = [
    ("clip", "s1.mp4", 0.25, 4.5),
    ("clip", "s2b.mp4", 0.84, 4.2),
    ("hold", 6.75),            # 걱정하는 건치 + 왜 달라붙으면 안 좋은지
    ("clip", "s3.mp4", 0.25, 4.5),
    ("hold", 2.9),             # 엄지척 + 자기 전 양치
    ("logo", 10.45),           # 같은 자리에 낀다면 + 검진 권유 + 차임
]

# ---- narration: (file, abs start, [(caption, rel_start, rel_end), ...]) ----
NARR = [
    ("l1_t.wav", 0.15, [("추석이다!", 0.0, 0.75), ("송편에 약과까지, 멈출 수가 없어요!", 1.19, 4.18)]),
    ("l2_t.wav", 5.90, [("앗! 이에 끈적하게 달라붙었어요!", 0.0, 2.94)]),
    ("n3_t.wav", 9.10, [("끈적한 간식은 이에 오래 붙어 있어서,", 0.0, 2.89),
                        ("충치균이 좋아하는 당분도 오래 남아요", 3.13, 6.20)]),
    ("l3_t.wav", 15.65, [("이럴 땐 물 한 모금으로 가글가글!", 0.0, 2.10), ("3초면 끝이에요", 2.43, 3.94)]),
    ("n6b_t.wav", 20.05, [("자기 전엔 꼭 양치하고 자세요!", 0.0, 2.56)]),
    ("n4_t.wav", 23.10, [("자꾸 같은 자리에 끼나요?", 0.0, 1.46), ("충치나 때운 곳의 틈,", 1.73, 3.38),
                         ("벗겨진 실란트(치아 홈 코팅)\n때문일 수도 있어요", 3.66, 5.68)]),
    ("n7_t.wav", 29.05, [("추석 지나면\n치과 검진도 한 번 받아보세요!", 0.0, 2.94)]),
]
TITLE = ("추석 간식", 0.0, 1.0)
BOING_AT = 5.90
CHIME_AT = 32.05

TOTAL = sum(s[-1] for s in SEGS)

# ---- build picture ----
parts, last_clip = [], None
for i, seg in enumerate(SEGS):
    o = f"{W}/v2p{i}.mp4"
    if seg[0] == "clip":
        _, f, ss, d = seg
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{W}/{f}", "-t", str(d),
             "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24,setsar=1",
             "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", o])
        last_clip = o
    elif seg[0] == "hold":
        d = seg[1]
        lf = f"{W}/v2last{i}.png"
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
with open(f"{W}/v2concat.txt", "w", encoding="utf-8") as fh:
    for p in parts:
        fh.write(f"file '{p}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/v2concat.txt",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", f"{W}/v2picture.mp4"])

# ---- captions (PIL) ----
def caption_png(text, path):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = text.split("\n")
    size = 46
    font = ImageFont.truetype(FONT, size)
    widest = lambda f: max(d.textbbox((0, 0), ln, font=f)[2] for ln in lines)
    while widest(font) > 660 and size > 38:
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
title_png(TITLE[0], f"{W}/v2title.png")
overlays.append((f"{W}/v2title.png", TITLE[1], TITLE[2]))
ci = 0
for f, at, caps in NARR:
    for text, rs, re_ in caps:
        pth = f"{W}/v2cap{ci}.png"; ci += 1
        caption_png(text, pth)
        overlays.append((pth, round(at + rs, 2), round(at + re_, 2)))

args = ["ffmpeg", "-v", "error", "-y", "-i", f"{W}/v2picture.mp4"]
for pth, _, _ in overlays:
    args += ["-i", pth]
chain, prev = [], "[0:v]"
for k, (_, s, e) in enumerate(overlays, start=1):
    lab = f"[v{k}]"
    chain.append(f"{prev}[{k}:v]overlay=0:0:enable='between(t,{s},{e})'{lab}")
    prev = lab
args += ["-filter_complex", ";".join(chain), "-map", prev, "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-crf", "18", f"{W}/v2captioned.mp4"]
run(args)

# ---- audio mix (boing.wav from v1 build) ----
srcs = [(f, at, 1.0) for f, at, _ in NARR] + [("boing.wav", BOING_AT, 0.45), (A + "/cute_chime.wav", CHIME_AT, 0.45)]
args = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", str(TOTAL), "-i", f"anullsrc=r={SR}:cl=mono"]
for f, _, _ in srcs:
    args += ["-i", f if os.path.isabs(f) else f"{W}/{f}"]
fl, labs = [], ["[0:a]"]
for k, (f, at, vol) in enumerate(srcs, start=1):
    ms = int(at * 1000)
    fl.append(f"[{k}:a]aformat=sample_rates={SR}:channel_layouts=mono,volume={vol},adelay={ms}|{ms}[a{k}]")
    labs.append(f"[a{k}]")
fl.append("".join(labs) + f"amix=inputs={len(labs)}:duration=first:normalize=0,atrim=0:{TOTAL}[aout]")
args += ["-filter_complex", ";".join(fl), "-map", "[aout]", "-c:a", "pcm_s16le", f"{W}/v2mix.wav"]
run(args)

run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/v2captioned.mp4", "-i", f"{W}/v2mix.wav",
     "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT])

# sanity: narration must not overlap and must end before its caption window / next line
for (f, at, caps), nxt in zip(NARR, NARR[1:] + [(None, TOTAL, None)]):
    end = at + dur(f"{W}/{f}")
    print(f"{f:10s} {at:6.2f} -> {end:6.2f}  next {nxt[1]:6.2f}  {'OVERLAP' if end > nxt[1] else 'ok'}")
print("done", OUT, TOTAL)
