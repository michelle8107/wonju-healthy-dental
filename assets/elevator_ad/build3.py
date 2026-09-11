# 엘리베이터 광고 v2 (15초, 1080x1920) — 건물 입구 → 엘리베이터 타고 2층 → 병원 내부
# 각 구간: (파일, 원본 시작, 원본 끝, 출력 길이) → 속도는 (끝-시작)/출력길이 배속으로 자동 계산
import subprocess, os, sys

E = os.path.dirname(os.path.abspath(__file__))
ORIG = r"D:/OneDrive/Claude_Dental Clinic/KakaoTalk_20260909_114941445.mp4"
OUT = E + "/elevator_ad_v3.mp4"
OPEN = sys.argv[1] if len(sys.argv) > 1 else "o1.mp4"
ELEV = "e1.mp4"
VID_Y, VID_H = 190, 810
TOTAL = 15.0
XF = 0.35  # 엔드카드 크로스페이드

SEGS = [  # (파일, 원본 시작, 원본 끝, 출력 길이, 헤드라인 번호)
    (OPEN, 0.0, 1.3, 1.3, 1),       # 국민건강보험공단 뷰 — 정속으로 잠깐 보여줌
    (OPEN, 1.3, None, 1.7, 1),      # 길 건너 조은빌딩 입구로
    (ELEV, 0.0, None, 3.0, 2),      # 엘리베이터 타고 2층 → 유리문
    ("c2.mp4", 0.0, None, 1.85, 3), # 유리문 → 접수대
    ("c3.mp4", 0.0, None, 1.85, 4), # 접수대 → 대기실
    ("c4.mp4", 0.0, None, 1.85, 5), # 대기실 → 진료실
    ("c5.mp4", 0.0, None, 1.85, 6), # 진료실 → 상담실
]
END_DUR = TOTAL - sum(s[3] for s in SEGS)   # 1.7

def run(a):
    subprocess.run(a, check=True)

def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]).decode())

parts = []
for i, (f, a, b, out_d, _) in enumerate(SEGS):
    src = f"{E}/{f}"
    b = b if b is not None else dur(src) - 0.04
    speed = (b - a) / out_d
    o = f"{E}/v3seg{i}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", src, "-an",
         "-vf", f"setpts=PTS/{speed:.4f},fps=30,scale=-2:{VID_H}:flags=lanczos,crop=1080:{VID_H},setsar=1",
         "-t", str(out_d), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", o])
    print(f"seg{i} {f} {a}-{b:.2f}s x{speed:.2f} -> {out_d}s")
    parts.append(o)
run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", f"{E}/endcard.png", "-t", str(END_DUR + XF),
     "-vf", "fps=30,setsar=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", f"{E}/v3seg_end.mp4"])
with open(f"{E}/v3concat.txt", "w") as fh:
    for p in parts:
        fh.write(f"file '{p}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{E}/v3concat.txt",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", f"{E}/v3drone.mp4"])
drone_len = sum(s[3] for s in SEGS)
run(["ffmpeg", "-v", "error", "-y", "-i", f"{E}/v3drone.mp4", "-i", f"{E}/v3seg_end.mp4", "-filter_complex",
     f"[0:v][1:v]xfade=transition=fade:duration={XF}:offset={drone_len - XF},trim=0:{TOTAL}[v]", "-map", "[v]",
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", f"{E}/v3window.mp4"])

# 헤드라인 창: 같은 번호 구간을 묶어서 (엔드카드는 마지막 번호)
bounds, t = {}, 0.0
for s in SEGS:
    k = s[4]
    bounds.setdefault(k, [t, t])[1] = t + s[3]; t += s[3]
bounds[max(bounds) + 1] = [t, TOTAL]
bounds = [tuple(bounds[k]) for k in sorted(bounds)]
hl = [(f"{E}/hl_{k + 1}.png", s, e) for k, (s, e) in enumerate(bounds)]

args = ["ffmpeg", "-v", "error", "-y",
        "-f", "lavfi", "-i", f"color=c=white:s=1080x1920:r=30:d={TOTAL}",
        "-i", f"{E}/v3window.mp4",
        "-loop", "1", "-t", str(TOTAL), "-i", f"{E}/base.png"]
for p, _, _ in hl:
    args += ["-loop", "1", "-t", str(TOTAL), "-i", p]
fc = [f"[0:v][1:v]overlay=0:{VID_Y}:shortest=1[a0]", "[a0][2:v]overlay=0:0[a1]"]
prev = "[a1]"
for k, (_, s, e) in enumerate(hl):
    fc.append(f"[{3 + k}:v]format=rgba,fade=t=in:st={s:.3f}:d=0.2:alpha=1[h{k}]")
    fc.append(f"{prev}[h{k}]overlay=0:0:enable='between(t,{s:.3f},{e - 0.001:.3f})'[b{k}]")
    prev = f"[b{k}]"
args += ["-filter_complex", ";".join(fc), "-map", prev, "-t", str(TOTAL),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-r", "30", f"{E}/v3picture.mp4"]
run(args)

run(["ffmpeg", "-v", "error", "-y", "-i", f"{E}/v3picture.mp4", "-i", ORIG, "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(TOTAL), "-movflags", "+faststart", OUT])
print("headlines:", [(round(s, 2), round(e, 2)) for _, s, e in hl])
print("done", OUT)
