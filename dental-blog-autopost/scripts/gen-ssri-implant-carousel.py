# -*- coding: utf-8 -*-
"""
"우울·불안 약(SSRI) 복용 중인데 임플란트 해도 될까요?" 카드뉴스 (10장), 팔레트 ochre
(gen-ppi-implant-carousel.py 레이아웃 재사용. 경쟁 병원 게시물은 주제 참고만: 성분명 사용, 수치 미사용, 구성 변경)
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

OUT_DIR = r"D:/OneDrive/Claude_Dental Clinic/assets/instagram_carousels/ssri_implant_guide"
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


ART_DIR = os.path.join(OUT_DIR, "art")


def paste_art(img, name, size, y, crop=None):
    """일러스트를 둥근 사각형으로 가운데 배치 (crop=(l,t,r,b) 비율)"""
    a = Image.open(os.path.join(ART_DIR, name)).convert("RGB")
    if crop:
        aw, ah = a.size
        a = a.crop((int(crop[0] * aw), int(crop[1] * ah), int(crop[2] * aw), int(crop[3] * ah)))
    a = a.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=40, fill=255)
    x = (W - size) // 2
    ImageDraw.Draw(img).rounded_rectangle([x - 6, y - 6, x + size + 6, y + size + 6], radius=46, fill=CARD)
    img.paste(a, (x, y), mask)


def slide_title(page, total, eyebrow, title_lines, sub=None, art=None):
    img, d = new_canvas()
    if art:
        paste_art(img, art, 500, 90)
        draw_eyebrow(d, eyebrow, y=680)
        bottom = draw_title(d, title_lines, y=770, size=76)
    else:
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


def slide_bullets(page, total, eyebrow, title_lines, bullets, note=None, art=None, crop=None, art_bottom=None):
    img, d = new_canvas()
    if art:
        paste_art(img, art, 250, 50, crop)
        draw_eyebrow(d, eyebrow, y=330, size=36)
        bottom = draw_title(d, title_lines, y=396, size=66)
    else:
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

    if art_bottom:
        paste_art(img, art_bottom, 250, min(y + 20, 1130 - 250))

    if note:
        ny = 1150
        for line in note:
            d.text((72, ny), line, font=font(30, "Regular"), fill=INK_SOFT)
            ny += 42

    draw_footer(d, page, total)
    return img


def slide_checklist_card(page, total, eyebrow, title_lines, card_title, card_sub=None, art=None):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow, y=300)
    bottom = draw_title(d, title_lines, y=380, size=66)
    draw_underline(d, bottom + 20)

    card_y = bottom + 80
    card_h = 340 if card_sub else 250
    d.rounded_rectangle([72, card_y, 1008, card_y + card_h], radius=32, fill=CARD)

    if art:
        paste_art(img, art, 230, 1000)

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
    1, TOTAL, "복용 약 · 임플란트",
    ["우울·불안 약(SSRI)을", "복용 중인데", "임플란트 해도 될까요?"],
    art="a1.png",
))

slides.append(slide_bullets(
    2, TOTAL, "먼저 알아볼까요",
    ["SSRI는", "어떤 약일까요"],
    [
        "에스시탈로프람·설트랄린·파록세틴 등이 SSRI(선택적 세로토닌 재흡수 억제제)에 속합니다",
        "우울, 불안, 공황 증상 등에 처방되고, 몇 달 이상 꾸준히 복용하는 경우가 많습니다",
        "치과 문진표의 복용 약 칸에 적지 않고 지나가는 경우도 있습니다",
    ],
    art="a4.png", crop=(0.0, 0.0, 1.0, 1.0),
))

slides.append(slide_bullets(
    3, TOTAL, "뼈와의 관계",
    ["세로토닌은", "뼈에도 작용한다고", "알려져 있어요"],
    [
        "뼈를 만들고 재생하는 세포에도 세로토닌과 관련된 경로가 있는 것으로 알려져 있습니다",
        "관찰연구에서 SSRI 복용과 골밀도 저하, 골절 위험 증가가 보고됐습니다",
        "다만 약이 원인이라고 확정된 것은 아니며, 연구마다 결과가 다릅니다",
    ],
    art="a2.png",
))

slides.append(slide_bullets(
    4, TOTAL, "연구는 어떨까요",
    ["임플란트와의 관계는", "인과관계가 확립되지", "않았어요"],
    [
        "일부 관찰연구에서 복용군의 임플란트 실패 위험이 더 높게 보고됐습니다",
        "연구마다 대상과 분석 방법이 달라 결과를 해석할 때 주의가 필요합니다",
        "‘실패한다’가 아니라 ‘관련이 보고됐다’는 수준이며, 인과관계는 확립되지 않았습니다",
    ],
    art="a5.png",
))

slides.append(slide_checklist_card(
    5, TOTAL, "핵심은 이것",
    ["복용 중이라고", "임플란트를 못 하는 건 아니에요"],
    "계획할 때 참고하는 정보",
    ["복용 사실만으로 가능 여부가 정해지지 않아요", "진찰과 검사 후 개별적으로 판단합니다"],
    art="a1.png",
))

slides.append(slide_bullets(
    6, TOTAL, "치과에서 같이 보는 것",
    ["복용 중 함께", "확인할 세 가지"],
    [
        "입마름: 침이 줄면 충치와 잇몸병이 생기기 쉬워 관리 방법을 함께 안내합니다",
        "이갈이: 복용 중 이갈이가 보고되기도 해, 증상이 있다면 확인하고 보철 설계나 나이트 가드를 고려합니다",
        "출혈: 소염진통제와 함께 복용하면 출혈 경향이 커질 수 있어 발치·수술 때 주의합니다",
    ],
    art="a3.png",
))

slides.append(slide_bullets(
    7, TOTAL, "상담 때 알려주세요",
    ["이런 내용을", "알려주시면 좋아요"],
    [
        "약 이름, 복용량, 복용한 기간(과거 복용 이력 포함)",
        "최근 약이 바뀌었는지, 앞으로도 계속 복용할 예정인지",
        "함께 복용하는 약: 소염진통제, 항응고제·항혈소판제, 골다공증 치료제",
        "처방전이나 약 목록을 가져오시면 정확합니다",
    ],
    art="a4.png", crop=(0.4, 0.0, 1.0, 0.7),
))

slides.append(slide_bullets(
    8, TOTAL, "치료 계획은",
    ["이렇게 준비할 수", "있어요"],
    [
        "CT로 뼈의 양과 상태를 확인합니다",
        "상태에 따라 치유 기간이나 식립 시기를 조정할 수 있습니다",
        "진통제와 소염제는 복용 중인 약을 고려해서 고릅니다",
        "수술 후에는 입안을 촉촉하게 유지하는 관리법도 안내합니다",
    ],
    art="a5.png", crop=(0.1, 0.1, 0.9, 0.9),
))

slides.append(slide_bullets(
    9, TOTAL, "기억해주세요",
    ["약은 임의로", "끊지 마세요"],
    [
        "갑자기 끊으면 어지러움, 불안 같은 증상이 생길 수 있습니다",
        "처방과 약 조절은 정신건강의학과·내과 영역입니다. 변경은 처방한 의료진과 상의해주세요",
        "임플란트 가능 여부는 진찰과 영상 검사 후 개별적으로 판단합니다",
    ],
    note=["참고: SSRI와 골 건강, 임플란트 관련 관찰연구 및 메타분석"],
    art="a4.png", crop=(0.0,0.0,1.0,1.0),
))

slides.append(slide_closing(10, TOTAL))

for i, img in enumerate(slides, start=1):
    path = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(path)
    print("saved", path)
