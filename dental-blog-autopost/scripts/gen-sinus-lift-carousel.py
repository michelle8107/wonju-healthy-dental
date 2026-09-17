# -*- coding: utf-8 -*-
"""
"상악동 거상술 + 뼈이식" 카드뉴스 (10장). 2026-09-18: 영상 대신 Higgsfield 3D 스틸(src_3d/)로 단계를 보여준다.
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


SRC_3D = os.path.join(OUT_DIR, "src_3d")
IMG_BOX = (72, 300, 1008, 1080)   # 그림 영역 (x0, y0, x1, y1)


def fit_image(name, focus_y=0.5):
    """src_3d 그림을 IMG_BOX 비율로 크롭(세로 기준점 focus_y) + 둥근 모서리."""
    bw, bh = IMG_BOX[2] - IMG_BOX[0], IMG_BOX[3] - IMG_BOX[1]
    src = Image.open(os.path.join(SRC_3D, name)).convert("RGB")
    sw, sh = src.size
    ch = int(sw * bh / bw)
    top = max(0, min(sh - ch, int(sh * focus_y - ch / 2)))
    pic = src.crop((0, top, sw, top + ch)).resize((bw, bh), Image.LANCZOS)
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, bw, bh], radius=32, fill=255)
    return pic, mask, top, sw / bw


def pill(d, text, xy, size=32, anchor_center=True):
    f = font(size, "Bold")
    tw = text_w(d, text, f)
    x, y = xy
    if anchor_center:
        x -= (tw + 36) // 2
    d.rounded_rectangle([x, y, x + tw + 36, y + size + 22], radius=(size + 22) // 2,
                        fill=(20, 14, 2, 200))
    d.text((x + 18, y + 6), text, font=f, fill=INK)


def slide_image(page, total, eyebrow, title, image, caption, labels=(), focus_y=0.5, note=None):
    """3D 그림 한 장 + 한 줄 제목 + 하단 설명. labels = [(텍스트, (원본x, 원본y) 지시점, (슬라이드x, 슬라이드y) 라벨 위치)]"""
    img, d = new_canvas()
    draw_eyebrow(d, eyebrow, y=96)
    bottom = draw_title(d, [title], y=170, size=56)
    draw_underline(d, bottom + 26, w=120)

    pic, mask, top, scale = fit_image(image, focus_y)
    img.paste(pic, IMG_BOX[:2], mask)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for text, (sx, sy), (lx, ly) in labels:
        tx = IMG_BOX[0] + sx / scale
        ty = IMG_BOX[1] + (sy - top) / scale
        ld.line([(lx, ly + 27), (tx, ty)], fill=INK + (230,), width=3)
        ld.ellipse([tx - 8, ty - 8, tx + 8, ty + 8], fill=ACCENT + (255,))
        pill(ld, text, (lx, ly))
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    d = ImageDraw.Draw(img)

    y = centered_lines(d, caption, 1108, 36, INK, weight="Medium", lh=50)
    if note:
        centered_lines(d, [note], y + 4, 26, INK_SOFT)
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


AI_NOTE = "※ 이해를 돕기 위해 AI로 생성한 3D 그림으로, 실제 구조와 차이가 있습니다"

TOTAL = 10
slides = [
    slide_title(1, TOTAL, "임플란트 뼈이식",
                ["위 어금니 임플란트,", "뼈가 부족하다는 말", "들어보셨나요?"],
                ["상악동 거상술과 뼈이식이 어떻게 진행되는지", "3D 그림으로 단계별로 정리했습니다"]),
    slide_bullets(2, TOTAL, "먼저 구조부터",
                  ["위 어금니 바로 위에는", "빈 공간이 있습니다"],
                  ["상악동은 코 옆 뼈 안쪽에 있는, 공기가 차 있는 빈 공간입니다",
                   "위 어금니 뿌리 끝은 이 공간과 아주 가깝게 맞닿아 있습니다",
                   "어금니를 오래 비워두면 잇몸뼈가 얇아지고 상악동이 내려앉기도 합니다",
                   "그래서 임플란트를 심을 뼈 높이가 부족한 경우가 생깁니다"]),
    slide_image(3, TOTAL, "한 장으로 보는 구조", "위 어금니 위, 이렇게 생겼습니다",
                "anatomy.png",
                ["어금니 자리 위로 상악동이 내려와 있어", "임플란트를 심을 뼈가 얇게 남은 상태입니다"],
                labels=[("상악동 (공기가 찬 공간)", (448, 330), (540, 470)),
                        ("상악동 점막", (640, 594), (800, 640)),
                        ("얇게 남은 뼈", (330, 657), (290, 690)),
                        ("잇몸", (620, 770), (820, 980))],
                focus_y=0.45, note=AI_NOTE),
    slide_image(4, TOTAL, "시술 과정 1단계", "볼쪽 뼈에 작은 창을 만듭니다",
                "step1_window.png",
                ["빈 어금니 자리 위, 볼쪽 뼈에 창을 내어", "상악동으로 접근합니다 (측방 접근)"],
                focus_y=0.36, note=AI_NOTE),
    slide_image(5, TOTAL, "시술 과정 2단계", "점막을 조심스럽게 들어올립니다",
                "step2_lift.png",
                ["상악동 점막이 찢어지지 않게 뼈에서 분리해", "들어올리면 아래에 빈 공간이 생깁니다"],
                labels=[("들어올린 점막", (448, 505), (540, 420)),
                        ("새로 생긴 공간", (448, 580), (540, 900))],
                focus_y=0.45, note=AI_NOTE),
    slide_image(6, TOTAL, "시술 과정 3단계", "빈 공간에 뼈이식재를 채웁니다",
                "step3_graft.png",
                ["공간을 뼈이식재로 채운 뒤, 창을 차폐막으로", "덮고 잇몸을 봉합합니다"],
                labels=[("뼈이식재", (448, 580), (540, 900))],
                focus_y=0.45, note=AI_NOTE),
    slide_image(7, TOTAL, "시술 과정 4단계", "뼈가 자리 잡으면 임플란트를 심습니다",
                "step4_implant.png",
                ["치유 기간 동안 이식재가 자기 뼈로 바뀌고,", "높아진 뼈에 임플란트를 식립합니다"],
                labels=[("높아진 뼈", (300, 620), (260, 720)),
                        ("임플란트", (448, 640), (800, 720))],
                focus_y=0.45,
                note="※ 기간·순서는 뼈 상태에 따라 다르며, 뼈이식과 식립을 함께 하기도 합니다"),
    slide_bullets(8, TOTAL, "알아두면 좋은 점",
                  ["접근 방법은", "하나가 아닙니다"],
                  ["남은 뼈가 어느 정도 있으면 잇몸뼈 위쪽에서 접근해 조금만 들어올리기도 합니다",
                   "뼈가 많이 부족할 때 앞에서 본 측방 접근을 사용합니다",
                   "어느 방법이든 상악동 점막이 찢어지지 않게 하는 것이 중요합니다",
                   "선택 기준은 CT로 확인한 뼈 높이와 상악동의 형태입니다"]),
    slide_bullets(9, TOTAL, "수술 후에는",
                  ["며칠 동안", "이렇게 지내주세요"],
                  ["코를 세게 풀지 않습니다",
                   "재채기가 나올 때는 입을 벌리고 합니다",
                   "빨대 사용과 흡연은 피해주세요",
                   "비행기 탑승처럼 압력이 변하는 일정은 미리 말씀해 주세요"],
                  note=["※ 주의 기간과 내용은 수술 범위에 따라 다르므로",
                        "   진료 시 안내받은 내용을 따라주세요."]),
    slide_closing(10, TOTAL),
]

for i, img in enumerate(slides, start=1):
    p = os.path.join(OUT_DIR, f"{i:02d}.png")
    img.save(p)
    print("saved", p)
