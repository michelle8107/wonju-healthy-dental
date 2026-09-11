# 엘리베이터 광고 15초 (1080x1920) 빌드
# 드론 구간 5개(각 5초 생성본을 2배속 → 2.5초) + 로고 엔드카드 2.5초, 레이아웃 PNG 합성
import subprocess, os, sys

E = os.path.dirname(os.path.abspath(__file__))
ORIG = r"D:/OneDrive/Claude_Dental Clinic/KakaoTalk_20260909_114941445.mp4"
OUT = E + "/elevator_ad.mp4"
CLIPS = [f"c{i}.mp4" for i in range(1, 6)]
SEG = 2.5
VID_Y, VID_H = 190, 810
TOTAL = 15.0

def run(a):
    subprocess.run(a, check=True)

# 1) 드론 구간: 2배속, 1080x810으로 맞춤
parts = []
for i, c in enumerate(CLIPS):
    o = f"{E}/seg{i}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{E}/{c}", "-an",
         "-vf", f"setpts=0.5*PTS,fps=30,scale=-2:{VID_H}:flags=lanczos,crop=1080:{VID_H},setsar=1",
         "-t", str(SEG), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", o])
    parts.append(o)
run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", f"{E}/endcard.png", "-t", str(SEG + 0.4),
     "-vf", "fps=30,setsar=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", f"{E}/seg_end.mp4"])
with open(f"{E}/concat.txt", "w") as fh:
    for p in parts:
        fh.write(f"file '{p}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{E}/concat.txt",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", f"{E}/drone.mp4"])
# 드론 → 엔드카드 0.4초 크로스페이드
run(["ffmpeg", "-v", "error", "-y", "-i", f"{E}/drone.mp4", "-i", f"{E}/seg_end.mp4", "-filter_complex",
     f"[0:v][1:v]xfade=transition=fade:duration=0.4:offset={5 * SEG - 0.4},trim=0:{TOTAL}[v]", "-map", "[v]",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", f"{E}/window.mp4"])

# 2) 레이아웃 합성
hl = [(f"{E}/hl_{k + 1}.png", k * SEG, (k + 1) * SEG) for k in range(6)]
args = ["ffmpeg", "-v", "error", "-y",
        "-f", "lavfi", "-i", f"color=c=white:s=1080x1920:r=30:d={TOTAL}",
        "-i", f"{E}/window.mp4",
        "-loop", "1", "-t", str(TOTAL), "-i", f"{E}/base.png"]
for p, _, _ in hl:
    args += ["-loop", "1", "-t", str(TOTAL), "-i", p]
fc = [f"[0:v][1:v]overlay=0:{VID_Y}:shortest=1[a0]", "[a0][2:v]overlay=0:0[a1]"]
prev = "[a1]"
for k, (_, s, e) in enumerate(hl):
    idx = 3 + k
    fc.append(f"[{idx}:v]format=rgba,fade=t=in:st={s}:d=0.25:alpha=1[h{k}]")
    fc.append(f"{prev}[h{k}]overlay=0:0:enable='between(t,{s},{e - 0.001})'[b{k}]")
    prev = f"[b{k}]"
args += ["-filter_complex", ";".join(fc), "-map", prev, "-t", str(TOTAL),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-r", "30", f"{E}/picture.mp4"]
run(args)

# 3) 기존 광고 음원 그대로 사용 (15초)
run(["ffmpeg", "-v", "error", "-y", "-i", f"{E}/picture.mp4", "-i", ORIG, "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(TOTAL), "-movflags", "+faststart", OUT])
print("done", OUT)
