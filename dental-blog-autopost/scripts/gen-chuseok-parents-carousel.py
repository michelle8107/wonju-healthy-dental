# -*- coding: utf-8 -*-
"""
"고향 가면, 부모님 치아 이것만 봐주세요" 추석 카드뉴스 (8장)
원주 건강한치과 카드뉴스 디자인 시스템 재사용 (gen-implant-prosthesis-carousel.py 기반)
팔레트: 황토색(ochre) — 2026-09-11 사용자 지정 ("세련된 황토색")

세련된 느낌을 위해 기존 ochre 팔레트는 그대로 두고 두 가지만 더했다:
  · 표지/마무리 장의 은은한 보름달 모티프 (추석)
  · 상단 얇은 골드 라인
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350

BG = (78, 48, 20)          # #4E3014
CARD = (124, 82, 40)       # #7C5228
INK = (255, 248, 238)      # #FFF8EE
INK_SOFT = (232, 201, 163) # #E8C9A3
ACCENT = (235, 178, 100)   # #EBB264
GOLD = (246, 216, 160)     # 보름달·라인용 연한 골드

FONT_PATH = "C:/Windows/Fonts/NotoSansKR-VF.ttf"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                       "assets", "instagram_carousels", "chuseok_parents_teeth")
os.makedirs(OUT_DIR, exist_ok=True)


def font(size, weight="Regular"):
    f = ImageFont.truetype(FONT_PATH, size)
    f.set_variation_by_name(weight)
    return f


def text_w(d, text, f):
    b = d.textbbox((0, 0), text, font=f)
    return b[2] - b[0]


def wrap_text(d, text, f, max_width):
    words, lines, cur = text.split(" "), [], ""
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


def add_moon(img, cx, cy, r):
    """은은한 보름달: 부드러운 후광 + 반투명 원."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse([cx - r * 1.35, cy - r * 1.35, cx + r * 1.35, cy + r * 1.35], fill=GOLD + (26,))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.25))
    ld = ImageDraw.Draw(layer)
    ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD + (48,))
    base = img.convert("RGBA")
    base.alpha_composite(layer)
    return base.convert("RGB")


def new_canvas(moon=None):
    img = Image.new("RGB", (W, H), BG)
    if moon:
        img = add_moon(img, *moon)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 8], fill=ACCENT)
    return img, d


def draw_eyebrow(d, text, y, size=40):
    f = font(size, "Bold")
    tw = text_w(d, text, f)
    icon_w, gap = 14, 24
    x = (W - (icon_w + gap + tw)) // 2
    d.rectangle([x, y, x + icon_w, y + size + 6], fill=ACCENT)
    d.text((x + icon_w + gap, y - 2), text, font=f, fill=ACCENT)


def draw_title(d, lines, y, size, weight="Black", color=INK):
    gap = int(size * 1.28)
    f = font(size, weight)
    for i, line in enumerate(lines):
        d.text(((W - text_w(d, line, f)) // 2, y + i * gap), line, font=f, fill=color)
    return y + len(lines) * gap


def draw_underline(d, y, w=150):
    x = (W - w) // 2
    d.rectangle([x, y, x + w, y + 10], fill=ACCENT)


def draw_footer(d, page, total, show_name=True):
    if show_name:
        d.text((72, 1268), "원주 건강한치과 · 표경열 원장", font=font(28), fill=INK_SOFT)
    label = f"{page} / {total}"
    f = font(30)
    d.text((1008 - text_w(d, label, f), 1264), label, font=f, fill=INK_SOFT)


def centered_lines(d, lines, y, size, color, weight="Regular", lh=None):
    f = font(size, weight)
    lh = lh or int(size * 1.42)
    for line in lines:
        d.text(((W - text_w(d, line, f)) // 2, y), line, font=f, fill=color)
        y += lh
    return y


def slide_title(page, total, eyebrow, title_lines, sub=None):
    img, d = new_canvas(moon=(860, 250, 150))
    draw_eyebrow(d, eyebrow, y=420)
    bottom = draw_title(d, title_lines, y=520, size=84)
    draw_underline(d, bottom + 24)
    if sub:
        centered_lines(d, sub, bottom + 70, 36, INK_SOFT)
    draw_footer(d, page, total)
    return img


def slide_bullets(page, total, eyebrow, title_lines, bullets, note=None):
    img, d = new_canvas()
    max_w = W - 124 - 72
    limit = 1120 if note else 1230
    title_h = len(title_lines) * int(74 * 1.28)
    # 42px부터 배치해보고 넘치면 한 단계씩 줄인다. 전체 블록은 세로 중앙(100~limit)에 둔다.
    for size, lh, gap in ((42, 56, 30), (40, 53, 26), (38, 50, 22), (36, 48, 18)):
        f = font(size, "Medium")
        wrapped = [wrap_text(d, b, f, max_w) for b in bullets]
        content_h = sum(len(w) * lh + gap for w in wrapped) - gap
        block_h = 80 + title_h + 66 + content_h
        if block_h <= limit - 140:
            break
    top = (100 + limit - block_h) // 2
    draw_eyebrow(d, eyebrow, y=top)
    bottom = draw_title(d, title_lines, y=top + 80, size=74)
    draw_underline(d, bottom + 20)
    y = bottom + 66
    for lines in wrapped:
        d.ellipse([72, y + 6, 100, y + 34], fill=ACCENT)
        for li, line in enumerate(lines):
            d.text((124, y + li * lh), line, font=f, fill=INK)
        y += len(lines) * lh + gap
    if note:
        ny = 1150
        for line in note:
            d.text((72, ny), line, font=font(30), fill=INK_SOFT)
            ny += 42
    draw_footer(d, page, total)
    return img


def slide_check(page, total, eyebrow, title_lines, card_title, card_sub):
    """체크 항목 1개 = 1장: 큰 질문 + 카드(무엇을 보면 되는지)."""
    img, d = new_canvas()
    f_sub = font(38)
    max_w = 1008 - 200 - 48
    sub_lines = [ln for s in card_sub for ln in wrap_text(d, s, f_sub, max_w)]
    card_h = 156 + len(sub_lines) * 56
    # 눈썹 + 제목 + 밑줄 + 카드 전체를 세로 중앙(100~1230)에 배치
    title_h = len(title_lines) * int(76 * 1.28)
    block_h = 80 + title_h + 80 + card_h
    top = (100 + 1230 - block_h) // 2
    draw_eyebrow(d, eyebrow, y=top)
    bottom = draw_title(d, title_lines, y=top + 80, size=76)
    draw_underline(d, bottom + 20)
    card_y = bottom + 80
    d.rounded_rectangle([72, card_y, 1008, card_y + card_h], radius=32, fill=CARD)
    d.rounded_rectangle([72, card_y, 84, card_y + card_h], radius=6, fill=GOLD)

    cx, cy, r = 142, card_y + 84, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
    d.line([cx - 15, cy, cx - 4, cy + 14], fill=BG, width=8)
    d.line([cx - 4, cy + 14, cx + 17, cy - 14], fill=BG, width=8)

    d.text((200, card_y + 46), card_title, font=font(48, "Bold"), fill=INK)
    sy = card_y + 126
    for line in sub_lines:
        d.text((200, sy), line, font=f_sub, fill=INK_SOFT)
        sy += 56
    draw_footer(d, page, total)
    return img


def slide_closing(page, total):
    img, d = new_canvas(moon=(540, 300, 130))
    draw_eyebrow(d, "올 추석에는", y=480)
    bottom = draw_title(d, ["부모님 식사 시간,", "한 번 더 살펴봐 주세요"], y=560, size=70)
    draw_underline(d, bottom + 24)
    note = [
        "이 콘텐츠는 일반적인 정보 제공을 목적으로 하며,",
        "정확한 상태는 검진을 통해 확인하실 수 있습니다.",
    ]
    ny = bottom + 70
    for line in note:
        d.text((72, ny), line, font=font(34), fill=INK_SOFT)
        ny += 48
    d.text((72, 1080), "원주 건강한치과", font=font(42, "Bold"), fill=ACCENT)
    d.text((72, 1136), "강원특별자치도 원주시 건강로 21, 2층 (반곡동)", font=font(30), fill=INK_SOFT)
    d.text((72, 1180), "TEL. 033-734-2275 · 카카오톡 상담 가능", font=font(30), fill=INK_SOFT)
    draw_footer(d, page, total, show_name=False)
    return img


TOTAL = 8
slides = [
    slide_title(1, TOTAL, "추석 명절 체크리스트",
                ["고향 가면", "부모님 치아,", "이것만 봐주세요"],
                ["오랜만에 함께하는 식사 자리에서", "자연스럽게 살펴볼 수 있어요"]),
    slide_bullets(2, TOTAL, "왜 명절일까요",
                  ["불편하셔도", "잘 말씀하지 않으세요"],
                  ["\u201c괜찮다\u201d, \u201c나이 들면 원래 그렇다\u201d며 넘기시는 경우가 많습니다",
                   "매일 뵙는 가족보다 오랜만에 뵙는 자녀가 변화를 더 잘 알아채기도 합니다",
                   "함께 식사하는 명절이 가장 자연스럽게 살펴볼 수 있는 때입니다"]),
    slide_check(3, TOTAL, "체크 ①", ["한쪽으로만", "씹으시나요?"],
                "씹는 모습 살펴보기",
                ["한쪽 턱으로만 씹거나", "음식을 오래 머금고 계신다면",
                 "반대쪽 치아나 잇몸이", "불편하실 수 있습니다"]),
    slide_check(4, TOTAL, "체크 ②", ["좋아하시던 음식을", "멀리하시나요?"],
                "딱딱하고 질긴 음식",
                ["갈비·김치·견과류를 잘게 잘라", "드시거나 아예 손대지 않으신다면",
                 "씹기가 불편하다는", "신호일 수 있습니다"]),
    slide_check(5, TOTAL, "체크 ③", ["틀니가 헐거워", "보이진 않나요?"],
                "틀니·보철물 점검",
                ["말씀하실 때 틀니가 들썩이거나", "식사 중 자꾸 빼고 끼우신다면",
                 "잇몸과 잇몸뼈 모양이 달라져", "조정이 필요할 수 있습니다"]),
    slide_bullets(6, TOTAL, "체크 ④",
                  ["잇몸 상태도", "살펴봐 주세요"],
                  ["양치할 때 피가 나거나 잇몸이 붓는다면",
                   "예전보다 입냄새가 심해졌다면",
                   "치아가 흔들리거나 길어 보인다면 (잇몸이 내려간 경우)",
                   "잇몸 질환의 신호일 수 있어 검진으로 확인하는 것이 좋습니다"]),
    slide_bullets(7, TOTAL, "이렇게 해보세요",
                  ["불편함이 보인다면", "검진부터 권해드리세요"],
                  ["복용 중인 약을 미리 정리해 두면 상담에 도움이 됩니다",
                   "자녀가 함께 가면 설명을 같이 듣고 기억하기 좋습니다",
                   "만 65세 이상은 틀니·임플란트에 건강보험이 적용될 수 있습니다",
                   "스케일링은 만 19세 이상 연 1회 건강보험이 적용됩니다"],
                  note=["※ 건강보험 적용 조건은 개인별로 다를 수 있어 내원 시 확인해 주세요."]),
    slide_closing(8, TOTAL),
]

for i, img in enumerate(slides, start=1):
    p = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(p)
    print("saved", p)
