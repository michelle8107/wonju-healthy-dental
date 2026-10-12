# -*- coding: utf-8 -*-
"""
"칫솔질만으로 다 닦였다고 생각하시나요?" 치실·치간칫솔 체크리스트 카드뉴스 (8장), 팔레트 green
(gen-implant-aftercare-carousel.py 레이아웃 재사용)
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350

PALETTES = {
    "navy": {
        "BG": (10, 20, 40),          # #0A1428
        "CARD": (19, 36, 68),        # #132444
        "INK": (240, 244, 250),      # #F0F4FA
        "INK_SOFT": (163, 179, 209), # #A3B3D1
        "ACCENT": (122, 168, 255),   # #7AA8FF
    },
    "green": {
        "BG": (10, 31, 22),          # #0A1F16
        "CARD": (17, 45, 32),        # #112D20
        "INK": (240, 250, 244),      # #F0FAF4
        "INK_SOFT": (163, 201, 179), # #A3C9B3
        "ACCENT": (110, 217, 160),   # #6ED9A0
    },
    "wine": {
        "BG": (32, 12, 20),          # #200C14
        "CARD": (56, 22, 34),        # #381622
        "INK": (250, 241, 244),      # #FAF1F4
        "INK_SOFT": (206, 163, 179), # #CEA3B3
        "ACCENT": (232, 130, 160),   # #E882A0
    },
    "ochre": {
        "BG": (78, 48, 20),          # #4E3014 (톤업: 기존 #241608보다 밝게)
        "CARD": (124, 82, 40),       # #7C5228
        "INK": (255, 248, 238),      # #FFF8EE
        "INK_SOFT": (232, 201, 163), # #E8C9A3
        "ACCENT": (235, 178, 100),   # #EBB264
    },
}

PALETTE_NAME = "green"
P = PALETTES[PALETTE_NAME]
BG = P["BG"]
CARD = P["CARD"]
INK = P["INK"]
INK_SOFT = P["INK_SOFT"]
ACCENT = P["ACCENT"]

FONT_PATH = "C:/Windows/Fonts/NotoSansKR-VF.ttf"

OUT_DIR = r"D:/OneDrive/Claude_Dental Clinic/assets/instagram_carousels/floss_interdental_checklist"
os.makedirs(OUT_DIR, exist_ok=True)


def font(size, weight="Regular"):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def text_w(d, text, f):
    bbox = d.textbbox((0, 0), text, font=f)
    return bbox[2] - bbox[0]


def wrap_text(d, text, f, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(d, trial, f) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_eyebrow(d, text, y=340, size=40):
    f = font(size, "Bold")
    tw = text_w(d, text, f)
    icon_w, gap = 14, 24
    total = icon_w + gap + tw
    x = (W - total) // 2
    d.rectangle([x, y, x + icon_w, y + size + 6], fill=ACCENT)
    d.text((x + icon_w + gap, y - 2), text, font=f, fill=ACCENT)


def draw_footer(d, page, total, show_name=True):
    if show_name:
        d.text((72, 1268), "원주 건강한치과 · 표경열 원장", font=font(28, "Regular"), fill=INK_SOFT)
    label = f"{page} / {total}"
    bbox = d.textbbox((0, 0), label, font=font(30, "Regular"))
    w = bbox[2] - bbox[0]
    d.text((1008 - w, 1264), label, font=font(30, "Regular"), fill=INK_SOFT)


def new_canvas():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def draw_title(d, lines, y, size, weight="Black", color=INK, line_gap=None):
    if line_gap is None:
        line_gap = int(size * 1.28)
    f = font(size, weight)
    for i, line in enumerate(lines):
        lw = text_w(d, line, f)
        x = (W - lw) // 2
        d.text((x, y + i * line_gap), line, font=f, fill=color)
    return y + len(lines) * line_gap


def draw_underline(d, y, w=150):
    x = (W - w) // 2
    d.rectangle([x, y, x + w, y + 10], fill=ACCENT)


def slide_title(page, total, eyebrow, title_lines, sub=None):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow, y=420)
    bottom = draw_title(d, title_lines, y=520, size=84)
    draw_underline(d, bottom + 24)
    if sub:
        sy = bottom + 66
        for line in sub:
            d.text((72, sy), line, font=font(34, "Regular"), fill=INK_SOFT)
            sy += 48
    draw_footer(d, page, total)
    return img


def slide_bullets(page, total, eyebrow, title_lines, bullets, note=None):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow, y=340)
    bottom = draw_title(d, title_lines, y=420, size=74)
    draw_underline(d, bottom + 20)

    y = bottom + 66
    f = font(42, "Medium")
    max_w = W - 124 - 72
    for b in bullets:
        d.ellipse([72, y + 6, 100, y + 34], fill=ACCENT)
        lines = b if isinstance(b, list) else wrap_text(d, b, f, max_w)
        for li, line in enumerate(lines):
            d.text((124, y + li * 56), line, font=f, fill=INK)
        y += len(lines) * 56 + 30

    if note:
        ny = 1150
        for line in note:
            d.text((72, ny), line, font=font(30, "Regular"), fill=INK_SOFT)
            ny += 42

    draw_footer(d, page, total)
    return img


def slide_checklist_card(page, total, eyebrow, title_lines, card_title, card_sub=None):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow, y=300)
    bottom = draw_title(d, title_lines, y=380, size=66)
    draw_underline(d, bottom + 20)

    card_y = bottom + 80
    card_h = 340 if card_sub else 250
    d.rounded_rectangle([72, card_y, 1008, card_y + card_h], radius=32, fill=CARD)

    cx, cy, r = 142, card_y + 84, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
    d.line([cx - 15, cy, cx - 4, cy + 14], fill=BG, width=8)
    d.line([cx - 4, cy + 14, cx + 17, cy - 14], fill=BG, width=8)

    tx = 200
    d.text((tx, card_y + 46), card_title, font=font(50, "Bold"), fill=INK)
    if card_sub:
        sy = card_y + 124
        for line in card_sub:
            d.text((tx, sy), line, font=font(36, "Regular"), fill=INK_SOFT)
            sy += 50

    draw_footer(d, page, total)
    return img


def slide_closing(page, total):
    img, d = new_canvas()
    draw_eyebrow(d, "마지막으로", y=380)
    bottom = draw_title(d, ["궁금한 점은", "언제든 문의해주세요"], y=460, size=74)
    draw_underline(d, bottom + 24)

    note_lines = [
        "이 콘텐츠는 일반적인 정보 제공을 목적으로 하며,",
        "개인의 구강 상태에 따라",
        "관리 방법과 도구는 달라질 수 있습니다.",
    ]
    ny = bottom + 70
    for line in note_lines:
        d.text((72, ny), line, font=font(36, "Regular"), fill=INK_SOFT)
        ny += 50

    d.text((72, 1096), "원주 건강한치과", font=font(42, "Bold"), fill=ACCENT)
    d.text((72, 1152), "강원특별자치도 원주시 건강로 21, 2층 (반곡동)", font=font(30, "Regular"), fill=INK_SOFT)
    d.text((72, 1196), "TEL. 033-734-2275", font=font(30, "Regular"), fill=INK_SOFT)

    draw_footer(d, page, total, show_name=False)
    return img


TOTAL = 8
slides = []

slides.append(slide_title(
    1, TOTAL, "치실 · 치간칫솔 체크리스트",
    ["칫솔질만으로", "다 닦였다고", "생각하시나요?"],
))

slides.append(slide_bullets(
    2, TOTAL, "왜 필요할까요",
    ["칫솔이 닿기 어려운", "곳이 있습니다"],
    [
        "치아 사이는 칫솔모가 닿기 어려워 세균막이 남기 쉽습니다",
        "남은 세균막은 충치와 잇몸 염증의 원인이 될 수 있습니다",
        "보조 도구를 함께 쓰면 구강 관리에 도움이 됩니다",
    ],
))

slides.append(slide_checklist_card(
    3, TOTAL, "①  확인해주세요",
    ["치아 사이가", "좁은 편인가요?"],
    "치실",
    ["C자 모양으로 치아를 감싸 위아래로 닦아주세요", "힘주어 튕기듯 넣으면 잇몸이 다칠 수 있어요"],
))

slides.append(slide_checklist_card(
    4, TOTAL, "②  확인해주세요",
    ["치아 사이에 틈이", "있는 편인가요?"],
    "치간칫솔",
    ["틈에 맞는 굵기를 골라 넣었다 빼며 닦아주세요", "너무 굵은 것을 억지로 넣지 않는 것이 좋습니다"],
))

slides.append(slide_checklist_card(
    5, TOTAL, "③  확인해주세요",
    ["임플란트나 교정장치,", "브릿지가 있나요?"],
    "보철 · 장치 주변",
    ["일반 치실이 들어가기 어려운 부위가 있을 수 있어요", "내게 맞는 도구는 진료 시 안내받으실 수 있습니다"],
))

slides.append(slide_checklist_card(
    6, TOTAL, "④  확인해주세요",
    ["닦을 때 피가 난다고", "그냥 두고 계신가요?"],
    "잇몸 출혈",
    ["염증이 있으면 피가 날 수 있어요", "출혈이 계속되면 확인받아 보세요"],
))

slides.append(slide_bullets(
    7, TOTAL, "기억해주세요",
    ["도구는 사람마다", "달라요"],
    [
        "치아 사이 틈, 치아 배열, 보철 여부에 따라 맞는 도구가 다릅니다",
        "하루 한 번, 자기 전에 꾸준히 하는 것이 중요합니다",
        "어떤 걸 써야 할지 모르겠다면 진료 시 편하게 물어봐주세요",
    ],
))

slides.append(slide_closing(8, TOTAL))

for i, img in enumerate(slides, start=1):
    path = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(path)
    print("saved", path)
