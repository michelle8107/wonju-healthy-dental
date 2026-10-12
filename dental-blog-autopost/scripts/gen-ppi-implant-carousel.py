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

PALETTE_NAME = "navy"
P = PALETTES[PALETTE_NAME]
BG = P["BG"]
CARD = P["CARD"]
INK = P["INK"]
INK_SOFT = P["INK_SOFT"]
ACCENT = P["ACCENT"]

FONT_PATH = "C:/Windows/Fonts/NotoSansKR-VF.ttf"

OUT_DIR = r"D:/OneDrive/Claude_Dental Clinic/assets/instagram_carousels/ppi_implant_guide"
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
    1, TOTAL, "복용 약 · 임플란트",
    ["위산 억제제(PPI)를", "오래 복용 중인데", "임플란트 해도 될까요?"],
))

slides.append(slide_bullets(
    2, TOTAL, "먼저 알아볼까요",
    ["위산 억제제란", "어떤 약일까요"],
    [
        "위산을 줄이는 약은 여러 종류이며, 여기서는 에소메프라졸·판토프라졸 등 PPI를 다룹니다",
        "역류성 식도염, 위궤양 치료에 쓰이고, 몇 주에서 수년까지 복용하기도 합니다",
        "PPI가 칼슘 흡수에 영향을 줄 가능성이 연구됐지만, 결과는 일관되지 않습니다",
    ],
))

slides.append(slide_bullets(
    3, TOTAL, "뼈와의 관계",
    ["치과에서 왜", "약을 물어볼까요"],
    [
        "임플란트는 턱뼈와 결합(골유착)해야 하고, 장기 유지에는 잇몸 건강과 꾸준한 관리도 중요합니다",
        "미국 FDA는 2010년 관찰연구를 근거로 PPI 사용과 고관절·손목·척추 골절 위험 증가 가능성을 알렸고, 특히 고용량 또는 1년 이상 복용에서 보고됐습니다",
        "이 경고는 골절에 관한 것으로, 임플란트에 대한 직접적인 근거는 아닙니다",
    ],
))

slides.append(slide_bullets(
    4, TOTAL, "연구는 어떨까요",
    ["연구 결과는", "엇갈립니다"],
    [
        "주로 관찰연구에서 복용군의 임플란트 실패 위험 증가가 보고됐습니다",
        "다른 요인을 보정한 뒤에도 연관성이 나타난 연구와 뚜렷하지 않은 연구가 모두 있습니다",
        "인과관계는 확립되지 않았으며, 약이 원인이라고 확정된 것은 아닙니다",
    ],
))

slides.append(slide_checklist_card(
    5, TOTAL, "핵심은 이것",
    ["복용 중이라고", "임플란트를 못 하는 건 아니에요"],
    "계획할 때 참고하는 정보",
    ["복용 사실만으로 가능 여부가 정해지지 않아요", "진찰과 검사 후 개별적으로 판단합니다"],
))

slides.append(slide_bullets(
    6, TOTAL, "상담 때 알려주세요",
    ["이런 내용을", "알려주시면 좋아요"],
    [
        "약 이름, 복용량, 복용한 기간(과거 복용 이력 포함)",
        "앞으로도 계속 복용할 예정인지",
        "골다공증 치료제의 복용·주사 여부와 마지막 투여일",
        "처방전이나 약 목록을 가져오시면 정확합니다",
    ],
))

slides.append(slide_bullets(
    7, TOTAL, "골다공증 약이 함께라면",
    ["골다공증 약은", "턱뼈와도 관련돼요"],
    [
        "비스포스포네이트·데노수맙은 골다공증 치료 용량에서 드물게 약물 관련 턱뼈괴사와 관련됩니다. 위험은 치료 목적·용량·기간에 따라 달라집니다",
        "복용 사실을 알려주시면 발치·임플란트 계획을 더 꼼꼼히 세울 수 있습니다",
        "약 변경 여부는 반드시 처방한 의료진과 상의해주세요",
    ],
))

slides.append(slide_bullets(
    8, TOTAL, "역류와 치아",
    ["위산이 입안까지", "역류하면 치아가", "닳을 수 있어요"],
    [
        "역류와 관련된 문제로, 위산이 치아 표면을 닳게 하는 산식증이 생길 수 있습니다",
        "역류 직후에는 먼저 물로 헹구고 바로 칫솔질하지 마세요. 평소에는 부드러운 칫솔과 불소치약을 사용하세요",
        "역류가 반복되면 담당 의사와 상담하고, 치아 표면이 예민하면 검진 때 알려주세요",
    ],
))

slides.append(slide_bullets(
    9, TOTAL, "기억해주세요",
    ["약은 임의로", "끊지 마세요"],
    [
        "복용 중인 약의 변경은 처방한 의료진과 상의해주세요",
        "임플란트 가능 여부는 진찰과 영상 검사 후 개별적으로 판단합니다",
        "궁금한 점은 참지 말고 편하게 물어봐주세요",
    ],
    note=["참고: FDA PPI 골절 안전성 정보(2010), 임플란트 관련 관찰연구(2016·2021)"],
))

slides.append(slide_closing(10, TOTAL))

for i, img in enumerate(slides, start=1):
    path = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(path)
    print("saved", path)
