# 건치의 하루 7탄 - 추석 간식 관리법 (D10) build
import subprocess, os, numpy as np, wave
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:/OneDrive/Claude_Dental Clinic"
A = ROOT + "/assets/geonchi_shorts"
FONT = A + "/fonts/Jua-Regular.ttf"
OUT = W + "/ep7_draft.mp4"  # copied to output/ once the final scene-2 take is picked

def run(args):
    subprocess.run(args, check=True)

# ---- timeline ----
import sys
S2 = sys.argv[1] if len(sys.argv) > 1 else "s2.mp4"
S2_SS = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8
L2_AT = float(sys.argv[3]) if len(sys.argv) > 3 else 5.45  # "앗!" on the freeze beat
SCENES = [("s1.mp4", 0.25, 4.5), (S2, S2_SS, 4.2), ("s3.mp4", 0.25, 4.5)]
LOGO_START = sum(d for _, _, d in SCENES)  # 13.2
LOGO_DUR = 7.7
TOTAL = LOGO_START + LOGO_DUR  # 20.9

L2_DUR = 2.94
NARR = [("l1_t.wav", 0.15), ("l2_t.wav", L2_AT), ("l3_t.wav", 8.95),
        ("l4_t.wav", 13.45), ("l5_t.wav", 16.45)]
CAPS = [  # text, start, end (= trimmed narration speech windows)
    ("추석이다!", 0.15, 0.90),
    ("송편에 약과까지, 멈출 수가 없어요!", 1.34, 4.33),
    ("앗! 이에 끈적하게 달라붙었어요!", L2_AT, round(L2_AT + L2_DUR, 2)),
    ("이럴 땐 물 한 모금으로 가글가글!", 8.95, 11.05),
    ("3초면 끝이에요", 11.38, 12.89),
    ("그리고 양치는 꼭 잊지 마세요!", 13.45, 16.17),
    ("명절에 다시 볼 사람, 저장해두세요!", 16.45, 19.63),
]
TITLE = ("추석 간식", 0.0, 1.0)
CHIME_AT = 19.70
BOING_AT = L2_AT

# ---- video: trim scenes + logo, concat ----
parts = []
for i, (f, ss, d) in enumerate(SCENES):
    o = f"{W}/p{i}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", f"{W}/{f}", "-t", str(d),
         "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24,setsar=1",
         "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", o])
    parts.append(o)
logo = f"{W}/p_logo.mp4"
run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", A + "/geonchihan_chikwa_logo.png", "-t", str(LOGO_DUR),
     "-vf", "fade=t=in:st=0:d=0.3,fps=24,scale=720:1280,setsar=1", "-c:v", "libx264", "-pix_fmt", "yuv420p",
     "-crf", "18", logo])
parts.append(logo)
with open(f"{W}/concat.txt", "w", encoding="utf-8") as fh:
    for p in parts:
        fh.write(f"file '{p}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/concat.txt",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", f"{W}/picture.mp4"])

# ---- caption / title PNGs (PIL, drawtext segfaults on this machine) ----
def caption_png(text, path):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    size = 46
    font = ImageFont.truetype(FONT, size)
    while d.textbbox((0, 0), text, font=font)[2] > 660 and size > 38:
        size -= 2
        font = ImageFont.truetype(FONT, size)
    d.rectangle([0, 978, 720, 978 + 130], fill=(0, 0, 0, int(255 * 0.55)))
    bb = d.textbbox((0, 0), text, font=font)
    x = (720 - (bb[2] - bb[0])) / 2 - bb[0]
    y = 978 + (130 - (bb[3] - bb[1])) / 2 - bb[1]
    d.text((x, y), text, font=font, fill="white")
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
for i, (t, s, e) in enumerate(CAPS):
    pth = f"{W}/cap{i}.png"
    caption_png(t, pth)
    overlays.append((pth, s, e))

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

# ---- SFX: cartoon "boing" freeze sting ----
SR = 24000
t = np.arange(int(SR * 0.45)) / SR
freq = 700 * np.exp(-t * 3.2) + 180
phase = 2 * np.pi * np.cumsum(freq) / SR
boing = np.sin(phase) * (1 + 0.35 * np.sin(2 * np.pi * 14 * t)) * np.exp(-t * 6.5)
boing = (boing / np.abs(boing).max() * 0.6 * 32767).astype(np.int16)
with wave.open(f"{W}/boing.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(boing.tobytes())

# ---- audio mix ----
srcs = NARR + [("boing.wav", BOING_AT), (A + "/cute_chime.wav", CHIME_AT)]
args = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", str(TOTAL), "-i", f"anullsrc=r={SR}:cl=mono"]
for f, _ in srcs:
    args += ["-i", f if os.path.isabs(f) else f"{W}/{f}"]
fl, labs = [], ["[0:a]"]
for k, (f, at) in enumerate(srcs, start=1):
    vol = 1.0 if f.startswith("l") else 0.45
    ms = int(at * 1000)
    fl.append(f"[{k}:a]aformat=sample_rates={SR}:channel_layouts=mono,volume={vol},adelay={ms}|{ms}[a{k}]")
    labs.append(f"[a{k}]")
fl.append("".join(labs) + f"amix=inputs={len(labs)}:duration=first:normalize=0,atrim=0:{TOTAL}[aout]")
args += ["-filter_complex", ";".join(fl), "-map", "[aout]", "-c:a", "pcm_s16le", f"{W}/mix.wav"]
run(args)

run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/captioned.mp4", "-i", f"{W}/mix.wav",
     "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT])
print("done", OUT, TOTAL)
