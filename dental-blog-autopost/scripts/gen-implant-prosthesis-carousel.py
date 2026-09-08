# -*- coding: utf-8 -*-
"""
"내 임플란트, 어떻게 고정되어 있을까요?" 임플란트 보철 연결 방식 카드뉴스 (9장)
원주 건강한치과 카드뉴스 디자인 시스템 재사용 (gen-implant-aftercare-carousel.py 기반)
팔레트: 네이비(navy) — 로테이션 순서 복귀 (진녹색 -> 네이비 -> 와인색 -> 황토색 -> 반복)

2026-09-08: 사용자가 참고로 보내준 릴스(전문가용 SCRP 설명)를 환자용으로 풀어 쓴 세트.
레이아웃 규칙은 aftercare 세트(2026-09-07 피드백 반영본)를 그대로 따른다:
  제목/eyebrow 중앙정렬 · 텍스트 블록 세로 중앙 · 확대된 폰트 · 불릿 자동 줄바꿈
추가: 임플란트 3부품 구조 설명용 자체 제작 단면 다이어그램 슬라이드 (저작권 이슈 없음)
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
        "BG": (10, 31, 22),
        "CARD": (17, 45, 32),
        "INK": (240, 250, 244),
        "INK_SOFT": (163, 201, 179),
        "ACCENT": (110, 217, 160),
    },
    "wine": {
        "BG": (32, 12, 20),
        "CARD": (56, 22, 34),
        "INK": (250, 241, 244),
        "INK_SOFT": (206, 163, 179),
        "ACCENT": (232, 130, 160),
    },
    "ochre": {
        "BG": (78, 48, 20),
        "CARD": (124, 82, 40),
        "INK": (255, 248, 238),
        "INK_SOFT": (232, 201, 163),
        "ACCENT": (235, 178, 100),
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

OUT_DIR = r"C:\Users\MYP\OneDrive\Claude_Dental Clinic\assets\instagram_carousels\implant_prosthesis_types"
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
        f = font(34, "Regular")
        sy = bottom + 66
        for line in sub:
            lw = text_w(d, line, f)
            d.text(((W - lw) // 2, sy), line, font=f, fill=INK_SOFT)
            sy += 48
    draw_footer(d, page, total)
    return img


def slide_bullets(page, total, eyebrow, title_lines, bullets, note=None):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow, y=340)
    bottom = draw_title(d, title_lines, y=420, size=74)
    draw_underline(d, bottom + 20)

    # 42px 기준으로 배치하되, 푸터(1230)를 넘기면 한 단계씩 줄여 자동으로 맞춘다.
    max_w = W - 124 - 72
    start_y = bottom + 66
    for size, lh, gap in ((42, 56, 30), (40, 53, 26), (38, 50, 22), (36, 48, 18)):
        f = font(size, "Medium")
        wrapped = [b if isinstance(b, list) else wrap_text(d, b, f, max_w) for b in bullets]
        end = start_y + sum(len(w) * lh + gap for w in wrapped)
        if end <= 1230:
            break

    y = start_y
    for lines in wrapped:
        d.ellipse([72, y + 6, 100, y + 34], fill=ACCENT)
        for li, line in enumerate(lines):
            d.text((124, y + li * lh), line, font=f, fill=INK)
        y += len(lines) * lh + gap

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
    card_h = 340 if card_sub and len(card_sub) > 2 else (300 if card_sub else 250)
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


def slide_diagram(page, total):
    """임플란트 3부품 단면 다이어그램 — PIL 프리미티브로 직접 그림 (저작권 이슈 없음)."""
    img, d = new_canvas()
    draw_eyebrow(d, "먼저 구조부터", y=250)
    bottom = draw_title(d, ["임플란트는", "세 부분으로 나뉩니다"], y=330, size=64)
    draw_underline(d, bottom + 18)

    # ── 다이어그램 영역
    BONE = (26, 44, 80)
    GUM = (58, 88, 138)
    METAL = (150, 172, 214)
    CROWN_C = (238, 243, 252)

    top = bottom + 76           # 다이어그램 시작 y
    gum_y = top + 210           # 잇몸선
    cx = 330                    # 치아 중심 x

    # 잇몸뼈 블록
    d.rounded_rectangle([150, gum_y, 620, gum_y + 320], radius=24, fill=BONE)
    # 잇몸 층
    d.rounded_rectangle([150, gum_y - 34, 620, gum_y + 40], radius=18, fill=GUM)

    # 픽스처(인공 치근) — 나사산 표현
    fx0, fx1 = cx - 42, cx + 42
    fy0, fy1 = gum_y + 6, gum_y + 286
    d.rounded_rectangle([fx0, fy0, fx1, fy1], radius=18, fill=METAL)
    ridge = fy0 + 26
    while ridge < fy1 - 16:
        d.line([fx0 + 4, ridge, fx1 - 4, ridge + 10], fill=BONE, width=5)
        ridge += 30

    # 지대주(연결 기둥) — 사다리꼴
    d.polygon(
        [(cx - 34, gum_y + 10), (cx + 34, gum_y + 10), (cx + 46, gum_y - 96), (cx - 46, gum_y - 96)],
        fill=METAL,
    )

    # 크라운(인공 치아) — 위쪽이 넓은 어금니 형태
    d.rounded_rectangle([cx - 96, gum_y - 240, cx + 96, gum_y - 86], radius=34, fill=CROWN_C)
    d.rounded_rectangle([cx - 70, gum_y - 110, cx + 70, gum_y - 74], radius=18, fill=CROWN_C)
    # 나사 구멍 메운 자국 (교합면)
    d.ellipse([cx - 26, gum_y - 232, cx + 26, gum_y - 200], fill=(198, 212, 236))

    # ── 라벨 + 리더 라인
    lf = font(38, "Bold")
    sf = font(30, "Regular")
    labels = [
        (gum_y - 176, cx + 84, "크라운", "겉으로 보이는 인공 치아"),
        (gum_y - 52, cx + 46, "지대주", "크라운과 픽스처를 잇는 기둥"),
        (gum_y + 140, cx + 42, "픽스처", "뼈에 심는 인공 치아뿌리"),
    ]
    for ly, sx, name, desc in labels:
        d.line([sx + 10, ly, 660, ly], fill=ACCENT, width=4)
        d.ellipse([sx + 2, ly - 8, sx + 18, ly + 8], fill=ACCENT)
        d.text((680, ly - 44), name, font=lf, fill=ACCENT)
        d.text((680, ly + 2), desc, font=sf, fill=INK_SOFT)

    d.text((150, gum_y + 344), "잇몸뼈", font=font(30, "Regular"), fill=INK_SOFT)
    d.text((176, gum_y - 22), "잇몸", font=font(30, "Regular"), fill=(226, 234, 248))

    draw_footer(d, page, total)
    return img


def slide_closing(page, total):
    img, d = new_canvas()
    draw_eyebrow(d, "마지막으로", y=380)
    bottom = draw_title(d, ["궁금한 점은", "언제든 문의해주세요"], y=460, size=74)
    draw_underline(d, bottom + 24)

    note_lines = [
        "이 콘텐츠는 일반적인 정보 제공을 목적으로 하며,",
        "어떤 방식이 적합한지는 잇몸·뼈 상태와",
        "임플란트 위치에 따라 달라질 수 있습니다.",
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


TOTAL = 9
slides = []

# 1. Hook
slides.append(slide_title(
    1, TOTAL, "임플란트 보철 이야기",
    ["내 임플란트,", "어떻게 고정되어", "있을까요?"],
))

# 2. 구조 다이어그램
slides.append(slide_diagram(2, TOTAL))

# 3. 오늘의 핵심 질문
slides.append(slide_bullets(
    3, TOTAL, "오늘의 주제",
    ["맨 위 인공 치아를", "붙이는 방법이", "두 가지 있습니다"],
    [
        "나사로 조여서 고정하는 방식",
        "치과용 접착제로 붙이는 방식",
        "이 선택은 몇 년 뒤 관리에서 차이가 드러납니다",
    ],
))

# 4. 나사식
slides.append(slide_checklist_card(
    4, TOTAL, "①  나사로 조이는 방식",
    ["씹는 면의 동그란 자국,", "보신 적 있으신가요?"],
    "나사 유지형",
    ["나사를 넣은 구멍을 치아색 재료로 메운 흔적입니다", "하자가 아니라 정상적인 마무리입니다",
     "나중에 나사를 풀어 분리해볼 수 있습니다"],
))

# 5. 접착식
slides.append(slide_checklist_card(
    5, TOTAL, "②  접착제로 붙이는 방식",
    ["겉은 더 매끄럽지만,", "떼어내기는 어렵습니다"],
    "시멘트 유지형",
    ["자연치아에 크라운을 씌우는 것과 같은 방식입니다", "씹는 면에 자국이 남지 않습니다",
     "점검이 필요할 때 분리가 쉽지 않습니다"],
))

# 6. 잔여 시멘트
slides.append(slide_bullets(
    6, TOTAL, "짚어둘 부분",
    ["잇몸 속에 남은", "접착제가 문제가", "되기도 합니다"],
    [
        "밀려 나온 여분이 잇몸 아래로 들어가면 확인이 어렵습니다",
        "세균막이 달라붙어 주변 잇몸 염증의 원인이 될 수 있습니다",
        "임플란트 주위 염증은 통증 없이 진행되는 경우가 많습니다",
    ],
))

# 7. SCRP
slides.append(slide_bullets(
    7, TOTAL, "그래서 나온 방법",
    ["두 방식을 합친", "SCRP 방식"],
    [
        "크라운과 지대주를 기공실에서 미리 붙여 하나로 만듭니다",
        "접착제 정리를 입 밖에서 끝내고 들어갑니다",
        "입안에서는 나사로만 고정합니다",
        "필요할 때 나사를 풀어 분리해볼 수 있습니다",
    ],
))

# 8. 무엇이 정답인가 (비교/우열 프레이밍 피하고 케이스별 판단으로)
slides.append(slide_bullets(
    8, TOTAL, "다만",
    ["항상 한 방식이", "정해져 있진 않습니다"],
    [
        "심어진 각도에 따라 나사 구멍 위치가 달라집니다",
        "앞니처럼 보이는 면이 중요한 부위는 고려할 점이 다릅니다",
        "위치·각도·씹는 힘·잇몸 상태를 함께 보고 정합니다",
        "내 보철이 어떤 방식인지 진료 시 물어보셔도 좋습니다",
    ],
))

# 9. Closing
slides.append(slide_closing(9, TOTAL))

for i, img in enumerate(slides, start=1):
    path = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(path)
    print("saved", path)
