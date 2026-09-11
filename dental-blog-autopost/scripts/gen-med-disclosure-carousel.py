# -*- coding: utf-8 -*-
"""
"발치 전, 복용 중인 약 미리 알려주세요" 체크리스트 카드뉴스 (8장)
원주 건강한치과 navy 카드뉴스 디자인 시스템 재사용 (implant_checklist와 동일 톤)
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
}

PALETTE_NAME = "green"
P = PALETTES[PALETTE_NAME]
BG = P["BG"]
CARD = P["CARD"]
INK = P["INK"]
INK_SOFT = P["INK_SOFT"]
ACCENT = P["ACCENT"]

FONT_PATH = "C:/Windows/Fonts/NotoSansKR-VF.ttf"

OUT_DIR = r"D:\OneDrive\Claude_Dental Clinic\assets\instagram_carousels\med_disclosure_checklist"
os.makedirs(OUT_DIR, exist_ok=True)


def font(size, weight="Regular"):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def wrap_lines(text):
    return text.split("\n")


def draw_eyebrow(d, text, x=72, y=140):
    d.rectangle([x, y, x + 8, y + 34], fill=ACCENT)
    d.text((x + 24, y - 3), text, font=font(30, "Bold"), fill=ACCENT)


def draw_footer(d, page, total, show_name=True):
    if show_name:
        d.text((72, 1270), "원주 건강한치과 · 표경열 원장", font=font(26, "Regular"), fill=INK_SOFT)
    label = f"{page} / {total}"
    bbox = d.textbbox((0, 0), label, font=font(28, "Regular"))
    w = bbox[2] - bbox[0]
    d.text((1008 - w, 1266), label, font=font(28, "Regular"), fill=INK_SOFT)


def new_canvas():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def draw_title(d, lines, y=230, size=64, weight="Black", color=INK, x=72, line_gap=78):
    f = font(size, weight)
    for i, line in enumerate(lines):
        d.text((x, y + i * line_gap), line, font=f, fill=color)
    return y + len(lines) * line_gap


def draw_underline(d, y, x=72, w=100):
    d.rectangle([x, y, x + w, y + 6], fill=ACCENT)


def slide_title(page, total, eyebrow, title_lines, sub=None):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow)
    bottom = draw_title(d, title_lines, y=230)
    draw_underline(d, bottom + 20)
    if sub:
        sy = bottom + 60
        for line in sub:
            d.text((72, sy), line, font=font(32, "Regular"), fill=INK_SOFT)
            sy += 46
    draw_footer(d, page, total)
    return img


def slide_bullets(page, total, eyebrow, title_lines, bullets, note=None):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow)
    bottom = draw_title(d, title_lines, y=230, size=56)
    draw_underline(d, bottom + 16)

    y = bottom + 70
    for b in bullets:
        d.ellipse([72, y + 10, 88, y + 26], fill=ACCENT)
        f = font(32, "Medium")
        lines = b if isinstance(b, list) else [b]
        for li, line in enumerate(lines):
            d.text((110, y + li * 42), line, font=f, fill=INK)
        y += len(lines) * 42 + 26

    if note:
        ny = 1150
        for line in note:
            d.text((72, ny), line, font=font(26, "Regular"), fill=INK_SOFT)
            ny += 36

    draw_footer(d, page, total)
    return img


def slide_checklist_card(page, total, eyebrow, title_lines, card_title, card_sub=None):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow)
    bottom = draw_title(d, title_lines, y=200, size=52)
    draw_underline(d, bottom + 14)

    card_y = bottom + 80
    card_h = 260 if card_sub else 200
    d.rounded_rectangle([72, card_y, 1008, card_y + card_h], radius=28, fill=CARD)

    # check circle
    cx, cy, r = 130, card_y + 70, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
    d.line([cx - 11, cy, cx - 3, cy + 10], fill=BG, width=6)
    d.line([cx - 3, cy + 10, cx + 13, cy - 10], fill=BG, width=6)

    tx = 176
    d.text((tx, card_y + 40), card_title, font=font(38, "Bold"), fill=INK)
    if card_sub:
        sy = card_y + 100
        for line in card_sub:
            d.text((tx, sy), line, font=font(28, "Regular"), fill=INK_SOFT)
            sy += 40

    draw_footer(d, page, total)
    return img


def slide_closing(page, total):
    img, d = new_canvas()
    draw_eyebrow(d, "마지막으로")
    bottom = draw_title(d, ["임의로 조절하지 마시고,", "진료 전 먼저 알려주세요"], y=280, size=56)
    draw_underline(d, bottom + 20)

    note_lines = [
        "이 콘텐츠는 일반적인 정보 제공을 목적으로 하며,",
        "개인의 복용 약물·건강 상태에 따라",
        "진료 전 확인 사항은 달라질 수 있습니다.",
    ]
    ny = bottom + 70
    for line in note_lines:
        d.text((72, ny), line, font=font(28, "Regular"), fill=INK_SOFT)
        ny += 42

    d.text((72, 1120), "원주 건강한치과", font=font(34, "Bold"), fill=ACCENT)
    d.text((72, 1168), "강원특별자치도 원주시 건강로 21, 2층 (반곡동)", font=font(26, "Regular"), fill=INK_SOFT)
    d.text((72, 1204), "TEL. 033-734-2275", font=font(26, "Regular"), fill=INK_SOFT)

    draw_footer(d, page, total, show_name=False)
    return img


TOTAL = 8
slides = []

# 1. Hook
slides.append(slide_title(
    1, TOTAL, "발치 전 체크리스트",
    ["치과 진료 전,", "이 약 드시고", "계신가요?"],
))

# 2. Why it matters
slides.append(slide_bullets(
    2, TOTAL, "왜 중요할까요",
    ["복용 중인 약에 따라", "진료 방식이 달라집니다"],
    [
        "지혈에 걸리는 시간이 달라질 수 있습니다",
        "마취 방법과 시술 시기 조정이 필요할 수 있습니다",
        "함께 처방할 약(항생제 등)이 달라질 수 있습니다",
    ],
))

# 3. 혈전용해제 항응고제
slides.append(slide_checklist_card(
    3, TOTAL, "①  확인해주세요",
    ["혈전을 묽게 하는 약을", "드시고 계신가요?"],
    "혈전용해제 · 항응고제",
    ["아스피린, 와파린, 자렐토, 엘리퀴스 등", "심장질환·뇌졸중 예방으로 복용하는 경우가 많습니다"],
))

# 4. 골다공증약
slides.append(slide_checklist_card(
    4, TOTAL, "②  확인해주세요",
    ["뼈를 튼튼하게 하는 약을", "드시고 계신가요?"],
    "골다공증 치료제",
    ["비스포스포네이트 계열 등", "복용 기간과 방법이 발치 계획에 영향을 줄 수 있습니다"],
))

# 5. 당뇨약
slides.append(slide_checklist_card(
    5, TOTAL, "③  확인해주세요",
    ["혈당 조절 약을", "사용하고 계신가요?"],
    "당뇨약 · 인슐린",
    ["회복 속도와 감염 관리에", "영향을 줄 수 있어 미리 확인이 필요합니다"],
))

# 6. 스테로이드/임신수유
slides.append(slide_checklist_card(
    6, TOTAL, "④  확인해주세요",
    ["그 밖에도", "알려주시면 좋은 것들"],
    "스테로이드제 · 임신/수유 여부",
    ["최근 수술 이력, 알레르기 여부도", "함께 말씀해주시면 진료 계획에 도움이 됩니다"],
))

# 7. Don't self-adjust
slides.append(slide_bullets(
    7, TOTAL, "가장 중요한 것",
    ["약 조절은", "스스로 하는 게", "아닙니다"],
    [
        "임의로 며칠 끊거나 줄이면 오히려 위험할 수 있습니다",
        "복용 중인 약은 처방받은 병원과 함께 확인해주세요",
        "궁금한 점은 진료 전 미리 문의해주세요",
    ],
))

# 8. Closing
slides.append(slide_closing(8, TOTAL))

for i, img in enumerate(slides, start=1):
    path = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(path)
    print("saved", path)
