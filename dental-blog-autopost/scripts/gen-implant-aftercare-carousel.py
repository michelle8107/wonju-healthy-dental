# -*- coding: utf-8 -*-
"""
"임플란트 시술 후, 이렇게 관리하고 계신가요?" 체크리스트 카드뉴스 (8장)
원주 건강한치과 카드뉴스 디자인 시스템 재사용 (implant_checklist/med_disclosure_checklist와 동일 톤)
팔레트: 황토색(ochre) — 로테이션에 신규 추가 (진녹색 -> 네이비 -> 와인색 -> 황토색 -> 반복)

2026-09-07 사용자 피드백 반영 이력:
  1) 제목 중앙정렬
  2) 바탕 톤업(더 밝은 황토색)
  3) 전체 글씨 확대
  4) eyebrow 라벨도 중앙정렬 + 텍스트 블록을 캔버스 상단이 아니라 세로 중앙 쪽으로 이동
     (med_disclosure_checklist 세트의 실제 배치를 기준으로 맞춤)
  5) 제목/본문 폰트를 그 기준 세트보다도 더 크게
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

PALETTE_NAME = "ochre"
P = PALETTES[PALETTE_NAME]
BG = P["BG"]
CARD = P["CARD"]
INK = P["INK"]
INK_SOFT = P["INK_SOFT"]
ACCENT = P["ACCENT"]

FONT_PATH = "C:/Windows/Fonts/NotoSansKR-VF.ttf"

OUT_DIR = r"C:\Users\MYP\OneDrive\Claude_Dental Clinic\assets\instagram_carousels\implant_aftercare_checklist"
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
        "개인의 시술 범위·건강 상태에 따라",
        "관리 방법은 달라질 수 있습니다.",
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

# 1. Hook
slides.append(slide_title(
    1, TOTAL, "임플란트 관리 체크리스트",
    ["임플란트 심고 나서,", "이렇게 관리하고", "계신가요?"],
))

# 2. Why it matters
slides.append(slide_bullets(
    2, TOTAL, "왜 중요할까요",
    ["초기 관리 방법에 따라", "회복 경과가 달라집니다"],
    [
        "며칠간의 관리 습관이 회복 속도에 영향을 줄 수 있습니다",
        "주변 조직이 안정되는 과정에도 영향을 줄 수 있습니다",
        "정기적인 확인이 장기적인 유지에 도움이 됩니다",
    ],
))

# 3. 식사
slides.append(slide_checklist_card(
    3, TOTAL, "①  확인해주세요",
    ["시술 부위로", "바로 씹고 계신가요?"],
    "식사 · 저작 습관",
    ["초반에는 반대쪽으로 씹고 부드러운 음식 위주로", "너무 뜨겁거나 딱딱한 음식은 피하는 것이 권장됩니다"],
))

# 4. 구강위생
slides.append(slide_checklist_card(
    4, TOTAL, "②  확인해주세요",
    ["평소처럼 칫솔질", "하고 계신가요?"],
    "구강 위생 관리",
    ["시술 부위는 부드럽게, 처방받은 가글이 있다면", "안내받은 방법대로 사용해주세요"],
))

# 5. 흡연·음주
slides.append(slide_checklist_card(
    5, TOTAL, "③  확인해주세요",
    ["흡연이나 음주,", "평소대로 하고 계신가요?"],
    "흡연 · 음주",
    ["회복 기간 동안에는 자제가 권장됩니다", "궁금하시면 진료 시 얼마나 자제해야 할지 문의해주세요"],
))

# 6. 붓기/통증
slides.append(slide_checklist_card(
    6, TOTAL, "④  확인해주세요",
    ["붓기나 통증이", "계속되고 있진 않나요?"],
    "붓기 · 통증 관리",
    ["안내받은 냉찜질과 처방약을 챙겨주시고", "며칠이 지나도 나아지지 않으면 바로 연락해주세요"],
))

# 7. Don't self-judge
slides.append(slide_bullets(
    7, TOTAL, "가장 중요한 것",
    ["이상하다 싶으면", "스스로 판단하지", "마세요"],
    [
        "정해진 정기검진은 꼭 방문해서 확인받아주세요",
        "붓기·통증·출혈이 오래가면 바로 병원에 문의해주세요",
        "궁금한 점은 참지 말고 언제든 물어봐주세요",
    ],
))

# 8. Closing
slides.append(slide_closing(8, TOTAL))

for i, img in enumerate(slides, start=1):
    path = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(path)
    print("saved", path)
