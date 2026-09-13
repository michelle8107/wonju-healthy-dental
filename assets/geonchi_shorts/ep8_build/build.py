# 건치의 하루 8탄 - 추석 연휴에 갑자기 이가 아플 때 (응급 대처 + 연휴 휴진 안내)
# 휴진 일정은 2026-09-13 사용자 확인: 9/24(목)~9/27(일) 휴진, 9/28(월)부터 정상 진료.
import subprocess, os, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont

W = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:/OneDrive/Claude_Dental Clinic"
A = ROOT + "/assets/geonchi_shorts"
FONT = A + "/fonts/Jua-Regular.ttf"
OUT = W + "/ep8.mp4"
SR = 24000

def run(args):
    subprocess.run(args, check=True)

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]).decode().strip())

# ---- picture timeline ----
# ("clip", file, ss, dur) | ("hold", dur) -> previous clip's last frame w/ slow push-in | ("logo", dur)
SEGS = [
    ("clip", "s1.mp4", 0.25, 4.3),    # 0.00  연휴 기지개
    ("clip", "s2.mp4", 2.0, 3.0),     # 4.30  얼어붙음 -> 볼 잡고 울먹
    ("hold", 6.4),                    # 7.30  울먹 정지컷: 치과도 쉬는데 / 이렇게 해보세요
    ("clip", "s3.mp4", 0.25, 4.75),   # 13.70 찬 찜질 -> 엄지척
    ("hold", 5.25),                   # 18.45 엄지척 정지컷: 진통제 안내
    ("clip", "s2.mp4", 2.9, 2.1),     # 23.70 볼 잡는 컷 재사용: 이럴 땐 참지 말고
    ("hold", 6.8),                    # 25.80
    ("logo", 8.8),                    # 32.60 휴진 안내 + 차임
]

# ---- narration: (file, abs start, [(caption, rel_start, rel_end), ...]) ----
NARR = [
    ("n1_t.wav", 0.30, [("추석 연휴다!", 0.0, 1.15), ("오늘은 푹 쉬어야지!", 1.70, 3.39)]),
    ("n2_t.wav", 5.65, [("악! 갑자기 이가 욱신욱신해요!", 0.0, 2.34)]),
    ("n3_t.wav", 8.30, [("연휴라 치과도 쉬는데, 어떡하죠?", 0.0, 2.84),
                        ("당황하지 말고, 이렇게 해보세요!", 3.07, 5.12)]),
    ("n4_t.wav", 13.90, [("아픈 쪽 볼 바깥에\n차가운 찜질을 해주고,", 0.0, 2.52),
                         ("아픈 쪽으로는 씹지 마세요", 2.76, 4.23)]),
    ("n5_t.wav", 18.60, [("진통제는 설명서대로 드시고,", 0.0, 2.33),
                         ("약을 잇몸에 직접 대는 건\n안 돼요!", 2.66, 4.82)]),
    ("n6_t.wav", 23.90, [("얼굴이 붓거나 열이 나면\n참지 말고,", 0.0, 3.14),
                         ("129나 119에 전화해서\n문 연 병원을 안내받으세요", 3.47, 8.42)]),
    ("n7_t.wav", 32.90, [("원주 건강한치과는\n9월 24일(목)~27일(일) 휴진", 0.0, 4.50),
                         ("28일(월)부터 정상 진료해요!", 4.85, 7.06)]),
]
TITLE = ("연휴 치통", 0.0, 1.0)
ZAP_AT = 5.50
CHIME_AT = 40.10

TOTAL = round(sum(s[-1] for s in SEGS), 3)

# ---- 찌릿 SFX: buzzy high tone w/ fast tremolo + crackle clicks, sharp decay ----
def make_zap(path):
    sr, d = 48000, 0.42
    rng = np.random.default_rng(8)
    t = np.arange(int(sr * d)) / sr
    f = 1900 - 900 * t / d
    tone = np.sign(np.sin(2 * np.pi * np.cumsum(f) / sr)) * 0.25 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / sr) * 0.35
    trem = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 38 * t))
    env = np.exp(-t * 7.5) * np.minimum(1, t / 0.006)
    sig = tone * trem * env
    for _ in range(14):
        at = int(rng.uniform(0, d * 0.75) * sr)
        n = int(sr * rng.uniform(0.003, 0.009))
        burst = rng.standard_normal(n) * np.exp(-np.linspace(0, 6, n)) * rng.uniform(0.3, 0.8)
        sig[at:at + n] += burst[:len(sig) - at]
    sig = sig / np.max(np.abs(sig)) * 0.9
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())

make_zap(f"{W}/zap.wav")

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
srcs = [(f, at, 1.0) for f, at, _ in NARR] + [("zap.wav", ZAP_AT, 0.35), (A + "/cute_chime.wav", CHIME_AT, 0.45)]
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

# sanity: narration must not overlap the next line; caption windows must not outlast the audio
for (f, at, caps), nxt in zip(NARR, NARR[1:] + [(None, CHIME_AT, None)]):
    d = dur(f"{W}/{f}")
    end = at + d
    cap_end = at + caps[-1][2]
    flag = "OVERLAP" if end > nxt[1] else ("CAP>AUDIO" if cap_end > end + 0.05 else "ok")
    print(f"{f:10s} {at:6.2f} -> {end:6.2f}  cap_end {cap_end:6.2f}  next {nxt[1]:6.2f}  {flag}")
print("chime end", CHIME_AT + dur(A + "/cute_chime.wav"), "total", TOTAL)
print("done", OUT, dur(OUT))
