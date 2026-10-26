# -*- coding: utf-8 -*-
"""
"치아 미백, 하기 전에 알아두세요" 카드뉴스 (10장), 팔레트 wine
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

PALETTE_NAME = "wine"
P = PALETTES[PALETTE_NAME]
BG = P["BG"]
CARD = P["CARD"]
INK = P["INK"]
INK_SOFT = P["INK_SOFT"]
ACCENT = P["ACCENT"]

FONT_PATH = "C:/Windows/Fonts/NotoSansKR-VF.ttf"

OUT_DIR = r"D:/OneDrive/Claude_Dental Clinic/assets/instagram_carousels/whitening_guide"
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
        "진료 계획과 관리 방법은 달라질 수 있습니다.",
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



TOTAL = 10
slides = []

slides.append(slide_title(
    1, TOTAL, "치아 미백 가이드",
    ["치아 미백,", "하기 전에", "알아두세요"],
))

slides.append(slide_bullets(
    2, TOTAL, "미백이란",
    ["치아 색을 밝게 하는", "과정이에요"],
    [
        "과산화수소나 과산화요소 계열의 미백제를 사용하는 방법이 흔합니다",
        "치과에서 하는 방법과 집에서 쓰는 제품이 있고, 농도와 사용 방법이 서로 다릅니다",
        "밝아지는 정도와 유지 기간은 사람마다 다릅니다",
    ],
))

slides.append(slide_bullets(
    3, TOTAL, "흔한 질문",
    ["미백 후 치아에", "문제가 생길까요"],
    [
        "연구 결과는 미백제의 농도, 사용 시간, 치아 상태에 따라 달라 한마디로 단정하기 어렵습니다",
        "그래서 제품 설명서나 안내받은 방법을 지키는 것이 중요합니다",
        "치아가 약해지는 것이 걱정된다면 시작 전에 상태를 확인받으세요",
    ],
))

slides.append(slide_bullets(
    4, TOTAL, "나타날 수 있는 불편",
    ["일시적으로 시리거나", "잇몸이 자극될 수 있어요"],
    [
        "미백 중이나 후에 이가 일시적으로 시릴 수 있습니다",
        "미백제가 잇몸에 닿으면 자극이나 불편이 생길 수 있습니다",
        "불편이 심하거나 오래가면 사용을 멈추고 진료를 받으세요",
    ],
))

slides.append(slide_checklist_card(
    5, TOTAL, "핵심은 이것",
    ["미백보다", "검진이 먼저예요"],
    "내 치아 상태 확인",
    ["충치나 잇몸 문제가 있으면", "먼저 진찰받고 치료 여부를 확인해요"],
))

slides.append(slide_bullets(
    6, TOTAL, "먼저 확인할 것",
    ["이런 경우는", "상담이 꼭 필요해요"],
    [
        "충치, 잇몸 염증, 금이 간 치아가 있는 경우",
        "평소 이가 자주 시린 경우",
        "크라운이나 레진 등 보철물이 있는 경우: 보철물은 미백제로 밝아지지 않아 자연치와 색 차이가 생길 수 있습니다",
        "임신 중이거나 수유 중인 경우: 미백 전 치과의사와 상담하세요",
    ],
))

slides.append(slide_bullets(
    7, TOTAL, "누런 이유",
    ["치아 색이 변하는", "이유는 여러 가지예요"],
    [
        "커피, 차, 와인 같은 음식과 흡연으로 표면에 착색이 생깁니다",
        "나이가 들면 법랑질이 얇아지고 상아질 색이 비쳐 누렇게 보일 수 있습니다",
        "일부 경우에는 신경치료를 받은 치아나 특정 약물 때문에 색이 달라지기도 합니다",
        "원인에 따라 맞는 방법이 달라서 먼저 원인을 확인하는 것이 좋습니다",
    ],
))

slides.append(slide_bullets(
    8, TOTAL, "평소 관리",
    ["착색은 평소", "관리로도 줄일 수 있어요"],
    [
        "착색이 잘 되는 음식을 먹은 뒤에는 물로 입을 헹궈주세요",
        "하루 2회 이상, 올바른 방법으로 칫솔질해주세요",
        "스케일링은 치석과 일부 표면 착색을 제거하는 데 도움이 되지만, 치아 본래 색을 밝히는 미백과는 다릅니다",
    ],
))

slides.append(slide_bullets(
    9, TOTAL, "기억해주세요",
    ["사용법을 지키고", "무리하지 마세요"],
    [
        "제품 설명서나 안내받은 사용 방법과 횟수를 지켜주세요",
        "더 밝게 하려고 과하게 반복하지 마세요",
        "개인별 가능 여부와 방법은 진찰 후 안내받으실 수 있습니다",
    ],
    note=["참고: American Dental Association, Whitening (ada.org)"],
))

slides.append(slide_closing(10, TOTAL))

for i, img in enumerate(slides, start=1):
    path = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(path)
    print("saved", path)