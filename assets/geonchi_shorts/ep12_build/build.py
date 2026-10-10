# 건치의 하루 12탄 - 회식 후 입냄새/치아관리 (D26). s2(깨어나는 컷)는 3회 생성 실패 -> s1 마지막 프레임 정지컷으로 대체
import subprocess, os
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.abspath(__file__))
A = r"D:/OneDrive/Claude_Dental Clinic/assets/geonchi_shorts"
FONT = A + "/fonts/Jua-Regular.ttf"
OUT = W + "/ep12_v1.mp4"
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

# 구간: clip(s1) 5.05 / still(s1 끝 프레임) 8.2 / clip(s3) 5.05 / logo 3.4
S1, STILL, S3, LOGO = 5.05, 8.2, 5.05, 3.4
T_STILL = S1
T_S3 = S1 + STILL
T_LOGO = T_S3 + S3
TOTAL = round(T_LOGO + LOGO, 3)

# (파일, trim 시작, trim 끝, tempo, 배치 시각)
NARR = [("n1.wav", 0.20, 5.30, 1.0, 0.0),
        ("n2.wav", 1.40, 10.15, 1.1, S1 + 0.25),
        ("n3.wav", 0.40, 5.10, 1.1, T_S3 + 0.0)]
n2 = NARR[1][4]
CAPS = [("회식 끝! 너무 피곤해서\n그냥 자고 싶어요", 0.25, 4.7),
        ("술자리 뒤엔 입이 마르기 쉬워서\n입냄새가 더 나기 쉬워요", n2 + 0.05, n2 + 4.6),
        ("자기 전에 물을\n한 컵 마셔 주세요!", n2 + 4.95, n2 + 7.9),
        ("양치랑 치실,\n혀도 살살 닦아 주세요!", T_S3 + 0.1, T_S3 + 4.3)]
TITLE = ("회식 후", 0.0, 1.0)
CHIME_AT = T_LOGO + 0.2

def assert_glyphs():
    from fontTools.ttLib import TTFont
    cmap = set()
    for tbl in TTFont(FONT)["cmap"].tables:
        cmap |= set(tbl.cmap.keys())
    text = TITLE[0] + "".join(c[0] for c in CAPS)
    missing = sorted({ch for ch in text if ch != "\n" and ord(ch) not in cmap})
    if missing:
        raise SystemExit("Jua 폰트에 없는 글자: " + " ".join(f"{c!r}(U+{ord(c):04X})" for c in missing))
assert_glyphs()

enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18"]
vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24,setsar=1"
run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/s1.mp4", "-t", str(S1), "-vf", vf, "-an"] + enc + [f"{W}/p0.mp4"])
run(["ffmpeg", "-v", "error", "-y", "-ss", "4.95", "-i", f"{W}/s1.mp4", "-frames:v", "1", "-vf",
     "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280", "-update", "1", f"{W}/last.png"])
n = int(round(STILL * 24))
run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/last.png", "-vf",
     f"scale=2880:5120:flags=lanczos,zoompan=z='1+0.08*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
     f":d={n}:s=720x1280:fps=24,setsar=1", "-t", str(STILL)] + enc + [f"{W}/p1.mp4"])
run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/s3.mp4", "-t", str(S3), "-vf", vf, "-an"] + enc + [f"{W}/p2.mp4"])
nl = int(round(LOGO * 24))
run(["ffmpeg", "-v", "error", "-y", "-i", A + "/geonchihan_chikwa_logo.png", "-vf",
     f"scale=720:1280,setsar=1,loop={nl}:1:0,fps=24,fade=t=in:st=0:d=0.3", "-t", str(LOGO)] + enc + [f"{W}/p3.mp4"])
with open(f"{W}/concat.txt", "w", encoding="utf-8") as fh:
    for i in range(4):
        fh.write(f"file '{W}/p{i}.mp4'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/concat.txt"] + enc + [f"{W}/picture.mp4"])

def caption_png(text, path):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = text.split("\n")
    size = 46
    font = ImageFont.truetype(FONT, size)
    while max(d.textbbox((0, 0), ln, font=font)[2] for ln in lines) > 660 and size > 34:
        size -= 2
        font = ImageFont.truetype(FONT, size)
    box_y, box_h = (978, 130) if len(lines) == 1 else (940, 185)
    d.rectangle([0, box_y, 720, box_y + box_h], fill=(0, 0, 0, int(255 * 0.55)))
    line_h = size + 14
    y0 = box_y + (box_h - (line_h * len(lines) - 14)) / 2
    for k, ln in enumerate(lines):
        bb = d.textbbox((0, 0), ln, font=font)
        d.text(((720 - (bb[2] - bb[0])) / 2 - bb[0], y0 + k * line_h - bb[1] + (size - (bb[3] - bb[1])) / 2),
               ln, font=font, fill="white")
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

title_png(TITLE[0], f"{W}/title.png")
overlays = [(f"{W}/title.png", TITLE[1], TITLE[2])]
for i, (t, s, e) in enumerate(CAPS):
    caption_png(t, f"{W}/cap{i}.png")
    overlays.append((f"{W}/cap{i}.png", round(s, 2), round(e, 2)))
args = ["ffmpeg", "-v", "error", "-y", "-i", f"{W}/picture.mp4"]
for pth, _, _ in overlays:
    args += ["-i", pth]
chain, prev = [], "[0:v]"
for k, (_, s, e) in enumerate(overlays, start=1):
    chain.append(f"{prev}[{k}:v]overlay=0:0:enable='between(t,{s},{e})'[v{k}]")
    prev = f"[v{k}]"
run(args + ["-filter_complex", ";".join(chain), "-map", prev] + enc + [f"{W}/captioned.mp4"], timeout=600)

args = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", str(TOTAL), "-i", f"anullsrc=r={SR}:cl=mono"]
ins = [f"{W}/{f}" for f, *_ in NARR] + [A + "/cute_chime.wav"]
for f in ins:
    args += ["-i", f]
fl, labs = [], ["[0:a]"]
for k, (f, a, b, tempo, at) in enumerate(NARR, start=1):
    ms = int(at * 1000)
    fl.append(f"[{k}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={tempo},aformat=sample_rates={SR}:channel_layouts=mono,"
              f"adelay={ms}|{ms}[a{k}]")
    labs.append(f"[a{k}]")
k = len(NARR) + 1
ms = int(CHIME_AT * 1000)
fl.append(f"[{k}:a]aformat=sample_rates={SR}:channel_layouts=mono,volume=0.45,adelay={ms}|{ms}[a{k}]")
labs.append(f"[a{k}]")
fl.append("".join(labs) + f"amix=inputs={len(labs)}:duration=first:normalize=0,atrim=0:{TOTAL}[aout]")
run(args + ["-filter_complex", ";".join(fl), "-map", "[aout]", "-c:a", "pcm_s16le", f"{W}/mix.wav"])
run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/captioned.mp4", "-i", f"{W}/mix.wav", "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", OUT])
print("done", OUT, dur(OUT), "chime end", round(CHIME_AT + dur(A + "/cute_chime.wav"), 2))
