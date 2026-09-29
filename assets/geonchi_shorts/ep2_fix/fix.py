# 건치 2탄 수정 (2026-09-29): "하나도 안 아파요" 단정 표현 -> "생각보다 훨씬 덜 불편해요(개인차 있음)"
# 원본 최종본의 8.6s 이후 자막을 흐림 처리하고 새 자막/내레이션을 얹는다. 대사가 길어져 11.9s에 1.8s 정지컷을 넣음.
import subprocess
from PIL import Image, ImageDraw, ImageFont
SRC = r"D:/OneDrive/Claude_Dental Clinic/output/geonchi2_scaling.mp4"
FONT = r"D:/OneDrive/Claude_Dental Clinic/assets/geonchi_shorts/fonts/Jua-Regular.ttf"
CUT, HOLD, TEMPO = 11.9, 1.8, 1.15
L1_AT, L2_AT = 8.68, 10.85
ORIG_TAIL = 13.97          # 원본에서 차임이 시작되기 직전
def run(a, t=300):
    p = subprocess.Popen(a)
    try:
        if p.wait(timeout=t): raise SystemExit("fail " + " ".join(a[:5]))
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)]); raise

def cap(text, path):
    im = Image.new("RGBA", (720, 1280), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lines = text.split("\n"); size = 46; f = ImageFont.truetype(FONT, size)
    while max(d.textbbox((0, 0), l, font=f)[2] for l in lines) > 660: size -= 2; f = ImageFont.truetype(FONT, size)
    by, bh = 978, 130   # 원본 자막 상자와 같은 자리·크기 (흰 로고 배경에서 두 겹으로 보이지 않게)
    d.rectangle([0, by, 720, by + bh], fill=(0, 0, 0, 140))
    lh = size + 10; y0 = by + (bh - (lh * len(lines) - 10)) / 2
    for k, l in enumerate(lines):
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((720 - (bb[2] - bb[0])) / 2 - bb[0], y0 + k * lh - bb[1] + (size - (bb[3] - bb[1])) / 2), l, font=f, fill="white")
    im.save(path)

for i in (1, 2):
    run(["ffmpeg", "-v", "error", "-y", "-i", f"a{i}_s.wav", "-af", f"atempo={TEMPO}", "-ar", "24000", "-ac", "2", f"a{i}_t.wav"])
cap("어라? 생각보다 괜찮네?", "c1.png")
cap("스케일링, 생각보다 훨씬 덜 불편해요!\n(개인차 있음)", "c2.png")
END = ORIG_TAIL + HOLD + 0.05
fc = (f"[0:v]trim=0:{CUT},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={HOLD}[va];"
      f"[0:v]trim={CUT},setpts=PTS-STARTPTS[vb];[va][vb]concat=n=2:v=1:a=0[v0];"
      f"[v0]split[v1][v2];[v2]crop=720:130:0:978,boxblur=25:5[bl];"
      f"[v1][bl]overlay=0:978:enable='between(t,8.6,{END})'[v3];"
      f"[v3][1:v]overlay=0:0:enable='between(t,8.6,{L2_AT - 0.05})'[v4];"
      f"[v4][2:v]overlay=0:0:enable='between(t,{L2_AT - 0.05},{END})'[vout];"
      f"[0:a]atrim=0:8.6,afade=t=out:st=8.5:d=0.1,asetpts=PTS-STARTPTS[oa];"
      f"[0:a]atrim={ORIG_TAIL},asetpts=PTS-STARTPTS,adelay={int((ORIG_TAIL + HOLD) * 1000)}|{int((ORIG_TAIL + HOLD) * 1000)}[ob];"
      f"[3:a]adelay={int(L1_AT * 1000)}|{int(L1_AT * 1000)}[n1];[4:a]adelay={int(L2_AT * 1000)}|{int(L2_AT * 1000)}[n2];"
      f"[oa][ob][n1][n2]amix=inputs=4:duration=longest:normalize=0[aout]")
run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-i", "c1.png", "-i", "c2.png", "-i", "a1_t.wav", "-i", "a2_t.wav",
     "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
     "-c:a", "aac", "-b:a", "160k", "-shortest", "ep2_fixed.mp4"], 600)
print("L1 end", L1_AT + 2.28 / TEMPO, "L2 end", L2_AT + 5.1 / TEMPO, "chime at", ORIG_TAIL + HOLD)
