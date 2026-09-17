# -*- coding: utf-8 -*-
"""
"상악동 거상술 + 뼈이식" 카드뉴스 (8장) — 그래피컬 영상(00_video.mp4)과 한 게시물로 묶인다.
원주 건강한치과 카드뉴스 디자인 시스템 재사용 (gen-chuseok-parents-carousel.py 기반)
팔레트: 노랑/골드 — 2026-09-17 사용자 지정 ("캐러셀 노랑색 바탕")

모식도 슬라이드는 영상과 같은 sinus_lift_diagram 모듈로 그린다 (그림 일관성).
"""
import os

from PIL import Image, ImageDraw

import sinus_lift_diagram as S

W, H = S.W, S.H
BG, CARD, INK, INK_SOFT, ACCENT, GOLD = S.BG, S.CARD, S.INK, S.INK_SOFT, S.ACCENT, S.GOLD

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                       "assets", "instagram_carousels", "sinus_lift_bonegraft")
os.makedirs(OUT_DIR, exist_ok=True)

font, text_w = S.font, S.text_w


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


def new_canvas():
    img = Image.new("RGB", (W, H), BG)
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
    d.rectangle([(W - w) // 2, y, (W - w) // 2 + w, y + 10], fill=ACCENT)


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


def slide_title(page, total, eyebrow, title_lines, sub):
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow, y=380)
    bottom = draw_title(d, title_lines, y=480, size=80)
    draw_underline(d, bottom + 24)
    centered_lines(d, sub, bottom + 74, 36, INK_SOFT)
    draw_footer(d, page, total)
    return img


def slide_bullets(page, total, eyebrow, title_lines, bullets, note=None):
    img, d = new_canvas()
    max_w = W - 124 - 72
    limit = 1120 if note else 1230
    title_h = len(title_lines) * int(74 * 1.28)
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


def slide_steps(page, total, eyebrow, title_lines, steps, note=None):
    """번호 카드 3개 (번호 원 + 제목 + 설명)."""
    img, d = new_canvas()
    f_sub = font(34)
    max_w = 1008 - 204 - 40
    cards = []
    for num, head, sub in steps:
        lines = wrap_text(d, sub, f_sub, max_w)
        cards.append((num, head, lines, 118 + max(0, len(lines) - 1) * 46))
    gap = 26
    cards_h = sum(c[3] for c in cards) + gap * (len(cards) - 1)
    title_h = len(title_lines) * int(68 * 1.28)
    limit = 1120 if note else 1230
    block_h = 80 + title_h + 76 + cards_h
    top = (100 + limit - block_h) // 2
    draw_eyebrow(d, eyebrow, y=top)
    bottom = draw_title(d, title_lines, y=top + 80, size=68)
    draw_underline(d, bottom + 20)

    y = bottom + 76
    for num, head, lines, ch in cards:
        d.rounded_rectangle([72, y, 1008, y + ch], radius=28, fill=CARD)
        d.rounded_rectangle([72, y, 84, y + ch], radius=6, fill=GOLD)
        cx, cy, r = 148, y + ch // 2, 34
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
        fn = font(36, "Black")
        d.text((cx - text_w(d, num, fn) // 2, cy - 26), num, font=fn, fill=BG)
        d.text((204, y + 22), head, font=font(42, "Bold"), fill=INK)
        sy = y + 76
        for line in lines:
            d.text((204, sy), line, font=f_sub, fill=INK_SOFT)
            sy += 46
        y += ch + gap
    if note:
        ny = 1150
        for line in note:
            d.text((72, ny), line, font=font(30), fill=INK_SOFT)
            ny += 42
    draw_footer(d, page, total)
    return img


def slide_diagram(page, total):
    """영상과 같은 모식도의 '시술 전' 한 컷 + 라벨."""
    img, d = new_canvas()
    draw_eyebrow(d, "한 장으로 보는 구조", y=110)
    bottom = draw_title(d, ["위 어금니 위, 이렇게 생겼습니다"], y=194, size=54)
    draw_underline(d, bottom + 16)

    img = S.draw_anatomy(img, {})
    img = S.draw_height_arrow(img, 1.0)
    img = S.draw_label(img, "잇몸뼈 (치조골)", (760, 812), (724, 1078), side="left", size=34)
    img = S.draw_label(img, "잇몸", (430, 900), (206, 1078), side="right", size=34)

    d = ImageDraw.Draw(img)
    f = font(42, "Bold")
    d.text(((W - text_w(d, "상악동", f)) // 2, 530), "상악동", font=f, fill=INK)
    f2 = font(30)
    d.text(((W - text_w(d, "(공기가 차 있는 빈 공간)", f2)) // 2, 588),
           "(공기가 차 있는 빈 공간)", font=f2, fill=INK_SOFT)
    d.text((72, 1176), "※ 이해를 돕기 위한 모식도로 실제 해부 구조와 차이가 있습니다.",
           font=font(28), fill=INK_SOFT)
    draw_footer(d, page, total)
    return img


def slide_closing(page, total):
    img, d = new_canvas()
    draw_eyebrow(d, "정리하면", y=380)
    bottom = draw_title(d, ["뼈가 부족해도", "준비하는 방법이 있습니다"], y=470, size=68)
    draw_underline(d, bottom + 24)
    ny = bottom + 74
    for line in ["상악동 거상술과 뼈이식은 임플란트를 심을 자리를",
                 "미리 만들어 두는 과정입니다. 필요한 방법과 기간은",
                 "CT 검사로 확인한 뼈 상태에 따라 달라집니다."]:
        d.text((72, ny), line, font=font(34), fill=INK_SOFT)
        ny += 50
    d.text((72, 1070), "원주 건강한치과", font=font(42, "Bold"), fill=ACCENT)
    d.text((72, 1126), "강원특별자치도 원주시 건강로 21, 2층 (반곡동)", font=font(30), fill=INK_SOFT)
    d.text((72, 1170), "TEL. 033-734-2275 · 카카오톡 상담 가능", font=font(30), fill=INK_SOFT)
    draw_footer(d, page, total, show_name=False)
    return img


TOTAL = 8
slides = [
    slide_title(1, TOTAL, "임플란트 뼈이식",
                ["위 어금니 임플란트,", "뼈가 부족하다는 말", "들어보셨나요?"],
                ["상악동 거상술과 뼈이식이 어떻게 진행되는지", "앞의 영상과 함께 그림으로 정리했습니다"]),
    slide_bullets(2, TOTAL, "먼저 구조부터",
                  ["위 어금니 바로 위에는", "빈 공간이 있습니다"],
                  ["상악동은 코 옆 뼈 안쪽에 있는, 공기가 차 있는 빈 공간입니다",
                   "위 어금니 뿌리 끝은 이 공간과 아주 가깝게 맞닿아 있습니다",
                   "어금니를 오래 비워두면 잇몸뼈가 얇아지고 상악동이 내려앉기도 합니다",
                   "그래서 임플란트를 심을 뼈 높이가 부족한 경우가 생깁니다"]),
    slide_diagram(3, TOTAL),
    slide_steps(4, TOTAL, "시술 과정 ①",
                ["상악동 거상술은", "이렇게 진행됩니다"],
                [("1", "측방 창 형성", "볼쪽 뼈에 작은 창을 만들어 상악동으로 접근합니다"),
                 ("2", "점막 거상", "상악동 점막을 뼈에서 분리해 조심스럽게 들어올립니다"),
                 ("3", "뼈이식재 충전", "들어올려 생긴 공간에 뼈이식재를 채웁니다")]),
    slide_steps(5, TOTAL, "시술 과정 ②",
                ["채운 뒤에는", "기다리는 시간이 있습니다"],
                [("4", "차폐막 · 봉합", "창을 차폐막으로 덮고 잇몸을 봉합합니다"),
                 ("5", "치유 기간", "채운 이식재가 환자 자신의 뼈로 바뀌어 갑니다"),
                 ("6", "임플란트 식립", "자리 잡은 뼈에 임플란트를 심습니다")],
                note=["※ 기간과 순서는 뼈 상태에 따라 다르며, 뼈이식과 식립을 함께 하기도 합니다."]),
    slide_bullets(6, TOTAL, "알아두면 좋은 점",
                  ["접근 방법은", "하나가 아닙니다"],
                  ["남은 뼈가 어느 정도 있으면 잇몸뼈 위쪽에서 접근해 조금만 들어올리기도 합니다",
                   "뼈가 많이 부족할 때 앞에서 본 측방 접근을 사용합니다",
                   "어느 방법이든 상악동 점막이 찢어지지 않게 하는 것이 중요합니다",
                   "선택 기준은 CT로 확인한 뼈 높이와 상악동의 형태입니다"]),
    slide_bullets(7, TOTAL, "수술 후에는",
                  ["며칠 동안", "이렇게 지내주세요"],
                  ["코를 세게 풀지 않습니다",
                   "재채기가 나올 때는 입을 벌리고 합니다",
                   "빨대 사용과 흡연은 피해주세요",
                   "비행기 탑승처럼 압력이 변하는 일정은 미리 말씀해 주세요"],
                  note=["※ 주의 기간과 내용은 수술 범위에 따라 다르므로",
                        "   진료 시 안내받은 내용을 따라주세요."]),
    slide_closing(8, TOTAL),
]

for i, img in enumerate(slides, start=1):
    p = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(p)
    print("saved", p)
