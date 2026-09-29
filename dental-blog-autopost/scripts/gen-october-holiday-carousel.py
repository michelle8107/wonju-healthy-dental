# -*- coding: utf-8 -*-
"""
"10월 공휴일에도 정상 진료합니다" 카드뉴스 (6장) — 2026-09-29
사용자 지시: 공휴일 3일(10/3 개천절, 10/5 대체공휴일, 10/9 한글날) 정상진료만 알리고 휴진(연휴) 안내는 뺀다.
팔레트: green (로테이션상 ochre 다음). 레이아웃은 gen-chuseok-parents-carousel.py 기반, 보름달 모티프 제거.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350

BG = (10, 31, 22)          # #0A1F16  green 팔레트
CARD = (17, 45, 32)        # #112D20
INK = (240, 250, 244)      # #F0FAF4
INK_SOFT = (163, 201, 179) # #A3C9B3
ACCENT = (110, 217, 160)   # #6ED9A0
GOLD = (178, 236, 204)     # 카드 좌측 바·장식용 밝은 민트

FONT_PATH = "C:/Windows/Fonts/NotoSansKR-VF.ttf"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                       "assets", "instagram_carousels", "october_holiday_hours")
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


def draw_hero(d, text, y, size):
    """'정상진료' 같은 핵심 단어를 액센트색으로 크게."""
    f = font(size, "Black")
    b = d.textbbox((0, 0), text, font=f)
    d.text(((W - (b[2] - b[0])) // 2 - b[0], y - b[1]), text, font=f, fill=ACCENT)
    return y + (b[3] - b[1])


def slide_title(page, total, eyebrow, lead, hero, sub=None):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow, y=360)
    bottom = draw_title(d, [lead], y=450, size=80)
    bottom = draw_hero(d, hero, bottom + 30, 190)
    draw_underline(d, bottom + 50)
    if sub:
        centered_lines(d, sub, bottom + 100, 38, INK_SOFT)
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



def slide_dates(page, total, eyebrow, lead, hero, rows):
    """날짜 카드 여러 장: (날짜, 공휴일 이름, 진료 시간)."""
    img, d = new_canvas()
    card_h, gap = 200, 26
    block_h = 80 + 97 + 20 + 120 + 60 + len(rows) * card_h + (len(rows) - 1) * gap
    top = (100 + 1230 - block_h) // 2
    draw_eyebrow(d, eyebrow, y=top)
    bottom = draw_title(d, [lead], y=top + 80, size=76)
    bottom = draw_hero(d, hero, bottom + 10, 120)
    y = bottom + 60
    for date, name, hours in rows:
        d.rounded_rectangle([72, y, 1008, y + card_h], radius=32, fill=CARD)
        d.rounded_rectangle([72, y, 84, y + card_h], radius=6, fill=GOLD)
        d.text((124, y + 30), date, font=font(56, "Black"), fill=INK)
        d.text((124, y + 106), name, font=font(34, "Bold"), fill=ACCENT)
        d.text((124, y + 150), hours, font=font(30), fill=INK_SOFT)
        # 우측 "정상진료" 배지 (크게)
        fb = font(54, "Black")
        b = d.textbbox((0, 0), "정상진료", font=fb)
        bw, bh = (b[2] - b[0]) + 64, 104
        bx, by = 1008 - 36 - bw, y + (card_h - bh) // 2
        d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=52, fill=ACCENT)
        d.text((bx + 32 - b[0], by + (bh - (b[3] - b[1])) // 2 - b[1]), "정상진료", font=fb, fill=BG)
        y += card_h + gap
    draw_footer(d, page, total)
    return img


def slide_closing(page, total):
    img, d = new_canvas()
    draw_eyebrow(d, "미리 예약하고 오세요", y=440)
    bottom = draw_title(d, ["10월 공휴일에도", "편하게 들러주세요"], y=520, size=72)
    draw_underline(d, bottom + 24)
    note = [
        "공휴일에는 예약이 몰릴 수 있어",
        "미리 전화로 예약해 주시면 좋습니다.",
        "정확한 상태는 진찰 후 상담으로 확인해 주세요.",
    ]
    centered_lines(d, note, bottom + 76, 34, INK_SOFT)
    d.text((72, 1080), "원주 건강한치과", font=font(42, "Bold"), fill=ACCENT)
    d.text((72, 1136), "강원특별자치도 원주시 건강로 21, 2층 (반곡동)", font=font(30), fill=INK_SOFT)
    d.text((72, 1180), "TEL. 033-734-2275 · 카카오톡 상담 가능", font=font(30), fill=INK_SOFT)
    draw_footer(d, page, total, show_name=False)
    return img


TOTAL = 6
slides = [
    slide_title(1, TOTAL, "원주 건강한치과 10월 진료 안내",
                "10월 공휴일에도", "정상진료",
                ["개천절 · 대체공휴일 · 한글날", "3일 모두 문을 엽니다"]),
    slide_bullets(2, TOTAL, "이런 적 있으셨죠",
                  ["치과 갈 시간,", "내기 어려우셨나요?"],
                  ["퇴근하고 달려가면 이미 진료가 끝나 있고",
                   "점심시간엔 병원도 쉬거나 대기가 길고",
                   "그러다 보니 불편한 치아를 자꾸 미루게 됩니다"]),
    slide_dates(3, TOTAL, "10월 공휴일 진료",
                "3일 모두", "정상진료",
                [("10/3 (토)", "개천절", "10:00 – 14:00 · 점심시간 없음"),
                 ("10/5 (월)", "대체공휴일", "10:00 – 19:00 · 점심 13–14시"),
                 ("10/9 (금)", "한글날", "10:00 – 19:00 · 점심 13–14시")]),
    slide_bullets(4, TOTAL, "이럴 때 들러보세요",
                  ["미뤄둔 치과 일정,", "이번에 챙겨보세요"],
                  ["올해 아직 스케일링을 받지 않으셨다면",
                   "찬 것에 시리거나 씹을 때 불편한 치아가 있다면",
                   "정기검진을 한동안 미뤄오셨다면",
                   "치료 중이라 다음 내원 일정을 잡아야 한다면"],
                  note=["※ 스케일링은 만 19세 이상 연 1회 건강보험이 적용됩니다."]),
    slide_bullets(5, TOTAL, "평소 진료 시간",
                  ["평일 저녁에도", "진료합니다"],
                  ["월 · 수 · 금  10:00 – 19:00 (점심 13–14시)",
                   "화  10:00 – 21:00 야간진료 (점심 13–14시)",
                   "목  14:00 – 21:00 야간진료",
                   "토  10:00 – 14:00 · 일요일 정기휴무"]),
    slide_closing(6, TOTAL),
]

for i, img in enumerate(slides, start=1):
    p = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(p)
    print("saved", p)
