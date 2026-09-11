# 엘리베이터 광고 레이아웃 PNG 생성 (1080x1920 세로)
# base.png   : 헤더(로고) + 영상 창(투명) + 헤드라인 띠 배경 + 하단 정보 패널 (15초 내내 고정)
# hl_N.png   : 헤드라인 문구 (장면마다 교체)
# endcard.png: 마지막 로고 카드 (영상 창 자리)
import os
from PIL import Image, ImageDraw, ImageFont

E = os.path.dirname(os.path.abspath(__file__))
FONT = "C:/Windows/Fonts/NotoSansKR-VF.ttf"
W, H = 1080, 1920

HEADER_H = 190
VID_Y, VID_H = HEADER_H, 810            # 1080x810 (4:3) 드론 영상
BAND_Y, BAND_H = VID_Y + VID_H, 330     # 헤드라인 띠 1000~1330
PANEL_Y = BAND_Y + BAND_H               # 하단 정보 1330~1920

TEAL = (0, 104, 138)       # 로고 '치과' 청록
DEEP = (8, 38, 52)         # 하단 패널 딥 네이비-청록
ORANGE = (255, 184, 28)    # 로고 주황 계열, 전화번호 강조
LIME = (176, 196, 0)
SOFT = (170, 216, 232)

def font(size, weight="Black"):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(weight)
    return f

def fit(d, text, weight, max_size, max_w, min_size=48):
    s = max_size
    while s > min_size:
        f = font(s, weight)
        if d.textbbox((0, 0), text, font=f)[2] <= max_w:
            return f
        s -= 2
    return font(min_size, weight)

def center_text(d, y, text, f, fill, stroke=0, stroke_fill=None):
    bb = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
    x = (W - (bb[2] - bb[0])) / 2 - bb[0]
    d.text((x, y - bb[1]), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return bb[3] - bb[1]

# ---------- base ----------
base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(base)
d.rectangle([0, 0, W, HEADER_H], fill=(255, 255, 255, 255))
logo = Image.open(E + "/logo1.png").convert("RGBA")
lh = 128
logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
base.alpha_composite(logo, ((W - logo.width) // 2, (HEADER_H - lh) // 2))
# 헤드라인 띠
d.rectangle([0, BAND_Y, W, BAND_Y + BAND_H], fill=TEAL + (255,))
d.rectangle([0, BAND_Y, W, BAND_Y + 10], fill=LIME + (255,))   # 영상과 띠 사이 포인트 라인
# 하단 패널
d.rectangle([0, PANEL_Y, W, H], fill=DEEP + (255,))
y = PANEL_Y + 52
pill_f = font(44, "Bold")
pill_t = "진료 예약 · 상담 문의"
bb = d.textbbox((0, 0), pill_t, font=pill_f)
pw, ph = bb[2] - bb[0] + 64, 76
d.rounded_rectangle([(W - pw) / 2, y, (W + pw) / 2, y + ph], radius=38, fill=TEAL + (255,))
center_text(d, y + (ph - (bb[3] - bb[1])) / 2, pill_t, pill_f, "white")
y += ph + 36
phone_f = fit(d, "033-734-2275", "Black", 170, 1000)
y += center_text(d, y, "033-734-2275", phone_f, ORANGE) + 56
center_text(d, y, "원주 반곡동 · 국민건강보험공단 앞", fit(d, "원주 반곡동 · 국민건강보험공단 앞", "Bold", 62, 980), "white")
y += 92
center_text(d, y, "건강로 21 조은빌딩 2층  건강한치과의원", fit(d, "건강로 21 조은빌딩 2층  건강한치과의원", "Medium", 50, 960), SOFT)
base.save(E + "/base.png")

# ---------- headlines ----------
HEADLINES = [
    ["국민건강보험공단", "바로 앞 건강한치과"],
    [[("조은빌딩 ", "white"), ("2층", ORANGE)]],   # 2층 강조
    ["필요한 진료 중심"],
    ["충분한 설명", "친절한 상담"],
    ["어린이부터 성인까지"],
    ["임플란트 · 보철 · 충치 · 잇몸", "스케일링 · 신경치료 · 치아교정"],
    ["건강한 치아", "건강한 미소"],
]
for i, lines in enumerate(HEADLINES, start=1):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if len(lines) == 1 and isinstance(lines[0], list):   # 색 섞인 한 줄
        segs = lines[0]
        full = "".join(t for t, _ in segs)
        f = fit(d, full, "Black", 150, 980)
        bb = d.textbbox((0, 0), full, font=f)
        x = (W - (bb[2] - bb[0])) / 2 - bb[0]
        y = BAND_Y + 10 + (BAND_H - 10 - (bb[3] - bb[1])) / 2 - bb[1]
        for t, col in segs:
            d.text((x, y), t, font=f, fill=col)
            x += d.textlength(t, font=f)
    elif len(lines) == 1:
        f = fit(d, lines[0], "Black", 128, 980)
        bb = d.textbbox((0, 0), lines[0], font=f)
        center_text(d, BAND_Y + 10 + (BAND_H - 10 - (bb[3] - bb[1])) / 2, lines[0], f, "white")
    else:
        size = min(fit(d, ln, "Black", 112, 980).size for ln in lines)
        f = font(size, "Black")
        hs = [d.textbbox((0, 0), ln, font=f)[3] - d.textbbox((0, 0), ln, font=f)[1] for ln in lines]
        gap = int(size * 0.32)
        total = sum(hs) + gap * (len(lines) - 1)
        yy = BAND_Y + 10 + (BAND_H - 10 - total) / 2
        for ln, h in zip(lines, hs):
            center_text(d, yy, ln, f, "white")
            yy += h + gap
    im.save(f"{E}/hl_{i}.png")

# ---------- end card (영상 창 자리) ----------
card = Image.new("RGBA", (W, VID_H), (255, 255, 255, 255))
lg = Image.open(E + "/logo2.png").convert("RGBA")
lw = 600
lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
card.alpha_composite(lg, ((W - lw) // 2, (VID_H - lg.height) // 2))
card.convert("RGB").save(E + "/endcard.png")

# preview: base + 첫 헤드라인, 영상 자리엔 사진
prev = Image.new("RGBA", (W, H), (255, 255, 255, 255))
ph_img = Image.open(E + "/kf/k3.jpg").convert("RGBA").resize((W, VID_H))
prev.alpha_composite(ph_img, (0, VID_Y))
prev.alpha_composite(base)
prev.alpha_composite(Image.open(E + "/hl_1.png"))
prev2 = Image.new("RGBA", (W, H), (255, 255, 255, 255))
prev2.alpha_composite(Image.open(E + "/endcard.png").convert("RGBA"), (0, VID_Y))
prev2.alpha_composite(base)
prev2.alpha_composite(Image.open(E + "/hl_2.png"))
pair = Image.new("RGB", (W * 2 + 40, H), (60, 60, 60))
pair.paste(prev.convert("RGB"), (0, 0)); pair.paste(prev2.convert("RGB"), (W + 40, 0))
pair.resize((pair.width // 2, H // 2)).save(E + "/layout_preview.png")
print("ok")
