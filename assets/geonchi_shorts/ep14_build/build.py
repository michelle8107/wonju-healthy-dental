# 건치의 하루 14탄 - 치아 미백하면 약해진다? (D22). s1 거울 클립 -> 정지컷 -> s3 설명 클립 -> 정지컷 -> 로고
# 대사는 Codex 의료광고 검토 반영: 안전성 단정 금지, 시림/잇몸 자극 명시, 검진 먼저.
import subprocess, os
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.abspath(__file__))
A = r"D:/OneDrive/Claude_Dental Clinic/assets/geonchi_shorts"
FONT = A + "/fonts/Jua-Regular.ttf"
OUT = W + "/ep14_v1.mp4"
SR = 24000
DISCLOSURE = "AI 캐릭터를 활용한 가상 상황, 일반적인 건강정보"

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

# 구간: s1 클립 5.0 / s1 끝 정지컷 7.0 / s3 클립 5.0 / s3 끝 정지컷 7.5 / 로고 3.6
S1, ST1, S3, ST3, LOGO = 5.0, 7.0, 5.0, 7.5, 3.6
T_ST1 = S1; T_S3 = S1 + ST1; T_ST3 = T_S3 + S3; T_LOGO = T_ST3 + ST3
TOTAL = round(T_LOGO + LOGO, 3)

# (파일, trim a, trim b, tempo, 배치 시각)
NARR = [("n1.wav", 0.40, 7.60, 1.1, 0.2),
        ("n2.wav", 0.40, 11.08, 1.15, 6.8),
        ("n3c.wav", 0.0, 8.30, 1.1, 16.5)]
CAPS = [("요즘 이가 좀\n누래 보여요", 0.25, 2.5),
        ("미백하고 싶은데\n이가 약해진다던데 정말일까요?", 2.75, 6.45),
        ("미백은 방법과 치아 상태에\n따라 영향이 달라요", 6.85, 10.55),
        ("미백 후 일시적으로 이가 시리거나\n잇몸이 자극될 수 있어요", 11.0, 16.05),
        ("충치나 잇몸 문제가 있으면\n먼저 치료가 필요할 수도 있어요", 16.55, 20.9),
        ("미백 전에 검진부터\n받아 보세요!", 21.3, 24.2)]
END_CAP = ("미백이 궁금하다면\n먼저 치아 상태를 확인하세요", T_LOGO + 0.2, TOTAL - 0.2)
TITLE = ("미백", 0.0, 1.0)
CHIME_AT = T_LOGO + 0.2

def assert_glyphs():
    from fontTools.ttLib import TTFont
    cmap = set()
    for tbl in TTFont(FONT)["cmap"].tables:
        cmap |= set(tbl.cmap.keys())
    text = TITLE[0] + DISCLOSURE + END_CAP[0] + "".join(c[0] for c in CAPS)
    missing = sorted({ch for ch in text if ch != "\n" and ord(ch) not in cmap})
    if missing:
        raise SystemExit("Jua 폰트에 없는 글자: " + " ".join(f"{c!r}(U+{ord(c):04X})" for c in missing))
assert_glyphs()

enc = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18"]
vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=24,setsar=1"

def still(src_clip, ss, name, secs):
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-i", src_clip, "-frames:v", "1", "-vf",
         "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280", "-update", "1", f"{W}/{name}.png"])
    n = int(round(secs * 24))
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/{name}.png", "-vf",
         f"scale=2880:5120:flags=lanczos,zoompan=z='1+0.08*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
         f":d={n}:s=720x1280:fps=24,setsar=1", "-t", str(secs)] + enc + [f"{W}/{name}.mp4"])

run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/s1.mp4", "-t", str(S1), "-vf", vf, "-an"] + enc + [f"{W}/p0.mp4"])
still(f"{W}/s1.mp4", 4.9, "st1", ST1)
run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/s3.mp4", "-t", str(S3), "-vf", vf, "-an"] + enc + [f"{W}/p2.mp4"])
still(f"{W}/s3.mp4", 4.9, "st3", ST3)
nl = int(round(LOGO * 24))
run(["ffmpeg", "-v", "error", "-y", "-i", A + "/geonchihan_chikwa_logo.png", "-vf",
     f"scale=720:1280,setsar=1,loop={nl}:1:0,fps=24,fade=t=in:st=0:d=0.3", "-t", str(LOGO)] + enc + [f"{W}/p4.mp4"])
names = ["p0", "st1", "p2", "st3", "p4"]
with open(f"{W}/concat.txt", "w", encoding="utf-8") as fh:
    for nm in names:
        fh.write(f"file '{W}/{nm}.mp4'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/concat.txt"] + enc + [f"{W}/picture.mp4"])

def caption_png(text, path):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = text.split("\n")
    size = 46
    font = ImageFont.truetype(FONT, size)
    while max(d.textbbox((0, 0), ln, font=font)[2] for ln in lines) > 660 and size > 30:
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

def disclosure_png(path):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, 26)
    bb = d.textbbox((0, 0), DISCLOSURE, font=font)
    d.text(((720 - (bb[2] - bb[0])) / 2 - bb[0], 1175), DISCLOSURE, font=font, fill="white",
           stroke_width=3, stroke_fill=(0, 0, 0, 200))
    im.save(path)

def endcap_png(text, path):
    # 흰 로고 배경 위: 어두운 글자
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = text.split("\n")
    size = 44
    font = ImageFont.truetype(FONT, size)
    while max(d.textbbox((0, 0), ln, font=font)[2] for ln in lines) > 660 and size > 30:
        size -= 2
        font = ImageFont.truetype(FONT, size)
    d.rectangle([0, 940, 720, 1125], fill=(0, 0, 0, int(255 * 0.55)))
    line_h = size + 14
    y0 = 940 + (185 - (line_h * len(lines) - 14)) / 2
    for k, ln in enumerate(lines):
        bb = d.textbbox((0, 0), ln, font=font)
        d.text(((720 - (bb[2] - bb[0])) / 2 - bb[0], y0 + k * line_h - bb[1] + (size - (bb[3] - bb[1])) / 2),
               ln, font=font, fill="white")
    im.save(path)

overlays = []
title_png(TITLE[0], f"{W}/title.png"); overlays.append((f"{W}/title.png", TITLE[1], TITLE[2]))
# 2026-10-21 사용자 결정: 상시 AI 표기 문구는 영상에서 제외 (의료인/실제 인물 없음). 캡션에 일반 건강정보 안내만 유지
for i, (t, s, e) in enumerate(CAPS):
    caption_png(t, f"{W}/cap{i}.png"); overlays.append((f"{W}/cap{i}.png", s, e))
endcap_png(END_CAP[0], f"{W}/endcap.png"); overlays.append((f"{W}/endcap.png", END_CAP[1], END_CAP[2]))

args = ["ffmpeg", "-v", "error", "-y", "-i", f"{W}/picture.mp4"]
for pth, _, _ in overlays:
    args += ["-i", pth]
chain, prev = [], "[0:v]"
for k, (_, s, e) in enumerate(overlays, start=1):
    chain.append(f"{prev}[{k}:v]overlay=0:0:enable='between(t,{round(s,2)},{round(e,2)})'[v{k}]")
    prev = f"[v{k}]"
run(args + ["-filter_complex", ";".join(chain), "-map", prev] + enc + [f"{W}/captioned.mp4"], timeout=900)

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
print("done", OUT, dur(OUT), "total", TOTAL, "chime end", round(CHIME_AT + dur(A + "/cute_chime.wav"), 2))
