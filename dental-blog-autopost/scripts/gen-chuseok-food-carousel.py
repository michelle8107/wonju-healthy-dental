# -*- coding: utf-8 -*-
"""
"명절 음식별 치아 지키는 법" 추석 카드뉴스 (8장)
원주 건강한치과 카드뉴스 디자인 시스템 재사용 (gen-implant-prosthesis-carousel.py 기반)
팔레트: 네이비(navy) — 2026-09-11 사용자 지정 ("세련된 파랑색")

세련된 느낌을 위해 기존 ochre 팔레트는 그대로 두고 두 가지만 더했다:
  · 표지/마무리 장의 은은한 보름달 모티프 (추석)
  · 상단 얇은 골드 라인
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350

BG = (10, 20, 40)          # #0A1428
CARD = (19, 36, 68)        # #132444
INK = (240, 244, 250)      # #F0F4FA
INK_SOFT = (163, 179, 209) # #A3B3D1
ACCENT = (122, 168, 255)   # #7AA8FF
GOLD = (214, 226, 250)     # 보름달·카드 포인트용 은빛 블루 (황토판의 GOLD 역할)

FONT_PATH = "C:/Windows/Fonts/NotoSansKR-VF.ttf"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                       "assets", "instagram_carousels", "chuseok_food_guide")
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
    bottom = draw_title(d, ["맛있는 명절,", "치아도 편안하게"], y=560, size=70)
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
    slide_title(1, TOTAL, "추석 음식 가이드",
                ["명절 음식별", "치아 지키는 법"],
                ["송편부터 갈비까지,", "맛있게 먹고 치아도 편안하게"]),
    slide_bullets(2, TOTAL, "먼저 알아두세요",
                  ["명절엔", "치아도 바빠집니다"],
                  ["끈적한 떡과 한과는 치아에 오래 붙어 있습니다",
                   "달콤한 음료를 조금씩 자주 마시게 됩니다",
                   "딱딱한 밤·견과류를 치아로 깨물기 쉽습니다",
                   "식사와 간식 사이, 입안이 쉴 틈이 줄어듭니다"]),
    slide_check(3, TOTAL, "음식 ①", ["끈적하고", "달콤한 간식"],
                "송편 · 약과 · 한과",
                ["끈적한 당분이 치아 홈과", "치아 사이에 오래 남습니다",
                 "먹은 뒤 물로 입을 헹구고", "자기 전엔 꼭 양치해 주세요"]),
    slide_check(4, TOTAL, "음식 ②", ["홀짝홀짝", "달콤한 음료"],
                "식혜 · 수정과",
                ["조금씩 자주 마시면 치아가", "당분에 닿는 시간이 길어집니다",
                 "식사와 함께 마시고,", "마신 뒤 물 한 모금이 좋아요"]),
    slide_check(5, TOTAL, "음식 ③", ["딱딱한 껍데기는", "치아 말고 도구로"],
                "밤 · 호두 · 잣",
                ["껍데기를 치아로 깨물면", "금이 가거나 깨질 수 있습니다",
                 "치료한 치아·보철물은 더 조심하고", "도구로 까서 드세요"]),
    slide_check(6, TOTAL, "음식 ④", ["자꾸 끼는", "고기와 나물"],
                "갈비 · 전 · 나물",
                ["질긴 고기 섬유와 나물은", "치아 사이에 잘 낍니다",
                 "이쑤시개보다 치실·치간칫솔이", "잇몸에 부담이 적어요"]),
    slide_bullets(7, TOTAL, "정리하면",
                  ["연휴 동안", "이것만 기억하세요"],
                  ["먹고 나면 물로 한 번 헹구기",
                   "딱딱한 건 치아 말고 도구로",
                   "자기 전 양치, 그리고 치실까지",
                   "연휴 뒤 불편한 곳이 있다면 검진으로 확인하기"]),
    slide_closing(8, TOTAL),
]

for i, img in enumerate(slides, start=1):
    p = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(p)
    print("saved", p)
