# -*- coding: utf-8 -*-
"""
상악동 거상술(측방 접근) + 뼈이식 모식도 — PIL 프리미티브로만 그린 원본 일러스트.
캐러셀(정지 이미지)과 애니메이션 영상이 같은 함수를 공유한다.

참고한 릴스에서는 '설명 순서'만 가져왔고 그림은 전부 여기서 새로 그린다 — 저작권 노출 0.

좌표계: 1080 x 1350, 앞에서 본 상악 구치부 단면.
  · 왼쪽 = 볼쪽(협측, 측방 창이 뚫리는 벽), 오른쪽 = 입천장쪽
"""
import math
import random
from PIL import Image, ImageChops, ImageDraw, ImageFont

W, H = 1080, 1350

# 팔레트 (노랑/골드)
BG = (58, 44, 8)            # #3A2C08
CARD = (92, 71, 18)         # #5C4712
INK = (255, 251, 238)       # #FFFBEE
INK_SOFT = (233, 217, 166)  # #E9D9A6
ACCENT = (245, 200, 56)     # #F5C838
GOLD = (250, 226, 150)

# 해부 색
BONE = (231, 215, 183)
BONE_DEEP = (205, 186, 148)
BONE_EDGE = (186, 164, 122)
BONE_DOT = (214, 196, 158)
AIR = (34, 26, 6)
MEM = (242, 150, 164)
MEM_DEEP = (206, 112, 128)
GING = (206, 116, 112)
GING_DEEP = (176, 92, 90)
TOOTH = (253, 251, 246)
TOOTH_EDGE = (206, 198, 180)
GRAFT = (252, 244, 226)
GRAFT_DOT = (222, 196, 142)
COVER = (198, 230, 240)
METAL = (198, 206, 216)
METAL_DARK = (132, 142, 158)

FONT_PATH = "C:/Windows/Fonts/NotoSansKR-VF.ttf"

# ── 기하 ─────────────────────────────────────────────────────────────
CREST_Y = 856            # 치조정 (뼈 아래 경계)
FLOOR_Y = 756            # 원래 상악동 바닥
SINUS_CX = 540
SINUS_A = 262            # 상악동 반폭
SINUS_B = 292            # 상악동 높이
BONE_L, BONE_R = 118, 962
BONE_SHOULDER = 584      # 옆벽이 직선으로 서 있는 높이
BONE_APEX = 412          # 뼈 윗면 꼭대기
WIN = (118, 588, 342, 710)   # 측방 창 (왼쪽 볼쪽 벽) — 상악동까지 관통
LIFT_MAX = 176
MOLAR_L, MOLAR_R = 222, 858


def font(size, weight="Regular"):
    f = ImageFont.truetype(FONT_PATH, size)
    f.set_variation_by_name(weight)
    return f


def text_w(d, text, f):
    b = d.textbbox((0, 0), text, font=f)
    return b[2] - b[0]


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_c(c1, c2, t):
    return tuple(int(round(lerp(c1[i], c2[i], t))) for i in range(3))


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ── 윤곽선 ───────────────────────────────────────────────────────────
def bone_outline():
    """치조골 + 상악동을 감싼 뼈 덩어리 (아래는 치조정, 위는 완만한 아치)."""
    pts = [(BONE_L, CREST_Y)]
    y = CREST_Y
    while y > BONE_SHOULDER:
        pts.append((BONE_L, y))
        y -= 24
    for i in range(101):
        t = i / 100.0
        x = lerp(BONE_L, BONE_R, t)
        y = BONE_SHOULDER - (BONE_SHOULDER - BONE_APEX) * math.sin(math.pi * t) ** 0.85
        pts.append((x, y))
    y = BONE_SHOULDER
    while y < CREST_Y:
        pts.append((BONE_R, y))
        y += 24
    pts.append((BONE_R, CREST_Y))
    return pts


def mem_y(x, lift):
    """거상된 점막(상악동 바닥)의 y 좌표."""
    u = min(1.0, abs(x - SINUS_CX) / SINUS_A)
    if u <= 0.32:
        b = 1.0
    else:
        b = 0.5 * (1 + math.cos(math.pi * (u - 0.32) / 0.68))
    return FLOOR_Y - lift * LIFT_MAX * b


def sinus_polygon(lift):
    """상악동 공기 공간: 거상된 바닥 + 고정된 돔."""
    floor = []
    for i in range(97):
        x = SINUS_CX - SINUS_A + i * (2 * SINUS_A) / 96.0
        floor.append((x, mem_y(x, lift)))
    dome = []
    for i in range(97):
        th = math.pi * i / 96.0
        x = SINUS_CX - SINUS_A * math.cos(th) * (1 - 0.10 * math.sin(th))
        y = FLOOR_Y - SINUS_B * math.sin(th) ** 0.92
        dome.append((x, y))
    return floor + dome[::-1]


def molar_shapes(cx):
    """상악 대구치: 위로 뻗은 뿌리 2개 + 아래로 나온 치관."""
    roots = []
    for dx in (-44, 44):
        roots.append([(cx + dx - 30, CREST_Y + 4), (cx + dx + 30, CREST_Y + 4),
                      (cx + dx + 17, CREST_Y - 106), (cx + dx + 4, CREST_Y - 146),
                      (cx + dx - 8, CREST_Y - 140), (cx + dx - 19, CREST_Y - 100)])
    crown = [(cx - 86, CREST_Y - 10), (cx + 86, CREST_Y - 10), (cx + 88, CREST_Y + 78),
             (cx + 74, CREST_Y + 132), (cx + 40, CREST_Y + 150), (cx + 14, CREST_Y + 116),
             (cx - 14, CREST_Y + 116), (cx - 40, CREST_Y + 150), (cx - 74, CREST_Y + 132),
             (cx - 88, CREST_Y + 78)]
    return roots, crown


_rng = random.Random(20260917)


def _bone_top(x):
    t = (x - BONE_L) / float(BONE_R - BONE_L)
    return BONE_SHOULDER - (BONE_SHOULDER - BONE_APEX) * math.sin(math.pi * t) ** 0.85


def _in_bone(x, y, m=16):
    if not (BONE_L + m < x < BONE_R - m):
        return False
    if not (_bone_top(x) + m < y < CREST_Y - m):
        return False
    if y < FLOOR_Y and ((x - SINUS_CX) / SINUS_A) ** 2 + ((FLOOR_Y - y) / SINUS_B) ** 2 < 1.12:
        return False
    return True


def _sample_bone_dots(n):
    out = []
    while len(out) < n:
        x = _rng.uniform(BONE_L, BONE_R)
        y = _rng.uniform(BONE_APEX, CREST_Y)
        if _in_bone(x, y):
            out.append((x, y, _rng.uniform(2.2, 4.4)))
    return out


_BONE_DOTS = _sample_bone_dots(760)
_PARTICLES = [(_rng.uniform(SINUS_CX - SINUS_A + 10, SINUS_CX + SINUS_A - 10),
               _rng.uniform(FLOOR_Y - LIFT_MAX - 2, FLOOR_Y - 5),
               _rng.uniform(5.0, 10.0)) for _ in range(210)]
_WIN_DOTS = [(_rng.uniform(WIN[0] + 22, WIN[2] - 8), _rng.uniform(WIN[1] + 14, WIN[3] - 14),
              _rng.uniform(5.0, 9.0)) for _ in range(40)]


def new_canvas():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 8], fill=ACCENT)
    return img, d


def dash_rect(d, box, color, width=5, dash=18):
    x0, y0, x1, y1 = box
    for x in range(int(x0), int(x1), dash * 2):
        d.line([(x, y0), (min(x + dash, x1), y0)], fill=color, width=width)
        d.line([(x, y1), (min(x + dash, x1), y1)], fill=color, width=width)
    for y in range(int(y0), int(y1), dash * 2):
        d.line([(x0, y), (x0, min(y + dash, y1))], fill=color, width=width)
        d.line([(x1, y), (x1, min(y + dash, y1))], fill=color, width=width)


def draw_fixture(d, cx, top_y, apex_y):
    """임플란트 픽스처: 위가 넓고 아래로 좁아지는 나사 형태."""
    half_top, half_apex = 54, 28
    body = [(cx - half_top, top_y), (cx + half_top, top_y),
            (cx + half_apex, apex_y + 24), (cx, apex_y), (cx - half_apex, apex_y + 24)]
    d.polygon(body, fill=METAL + (255,))
    y = top_y - 24
    while y > apex_y + 34:
        t = (top_y - y) / max(1.0, (top_y - apex_y))
        hw = lerp(half_top, half_apex, t) - 5
        d.line([(cx - hw, y + 6), (cx + hw, y - 6)], fill=METAL_DARK + (255,), width=6)
        y -= 25
    d.rectangle([cx - half_top, top_y - 15, cx + half_top, top_y], fill=METAL_DARK + (255,))


_CACHE = {}


def _bone_base():
    """뼈 덩어리 + 골소주 텍스처 — 매 프레임 같으므로 한 번만 그린다."""
    if "bone" not in _CACHE:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        bone = bone_outline()
        d.polygon(bone, fill=BONE + (255,))
        d.line(bone + [bone[0]], fill=BONE_EDGE + (255,), width=5, joint="curve")
        bone_dot = lerp_c(BONE, BONE_DOT, 0.62)
        for (px, py, pr) in _BONE_DOTS:
            d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=bone_dot + (255,))
        d.line([(BONE_L + 6, CREST_Y - 3), (BONE_R - 6, CREST_Y - 3)],
               fill=lerp_c(BONE, BONE_DEEP, 0.85) + (255,), width=5)
        _CACHE["bone"] = layer
    return _CACHE["bone"]


def _gum_teeth():
    """잇몸 + 인접치 — 역시 고정."""
    if "gum" not in _CACHE:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        ging = [(BONE_L - 6, CREST_Y - 6)]
        for i in range(121):
            x = lerp(BONE_L - 6, BONE_R + 6, i / 120.0)
            ging.append((x, 918 + 6 * math.sin(i / 120.0 * math.pi * 5)))
        ging.append((BONE_R + 6, CREST_Y - 6))
        d.polygon(ging, fill=GING + (255,))
        d.line(ging[1:-1], fill=GING_DEEP + (255,), width=5, joint="curve")
        for cx in (MOLAR_L, MOLAR_R):
            roots, crown = molar_shapes(cx)
            for r in roots:
                d.polygon(r, fill=TOOTH + (255,))
                d.line(r + [r[0]], fill=TOOTH_EDGE + (255,), width=4, joint="curve")
            d.polygon(crown, fill=TOOTH + (255,))
            d.line(crown + [crown[0]], fill=TOOTH_EDGE + (255,), width=4, joint="curve")
        _CACHE["gum"] = layer
    return _CACHE["gum"]


def draw_anatomy(img, st):
    """st: window/lift/graft/cover/mature/implant (각 0..1) + anat(전체 페이드)."""
    window = st.get("window", 0.0)
    lift = st.get("lift", 0.0)
    graft = st.get("graft", 0.0)
    cover = st.get("cover", 0.0)
    mature = st.get("mature", 0.0)
    implant = st.get("implant", 0.0)

    layer = _bone_base().copy()
    d = ImageDraw.Draw(layer)

    # 상악동 (공기)
    d.polygon(sinus_polygon(lift), fill=AIR + (255,))
    # 거상으로 생긴 빈 공간 — 이식재가 채우기 전까지는 비어 있다
    if lift > 0.001:
        gap_top, gap_bot = [], []
        for i in range(97):
            x = SINUS_CX - SINUS_A + i * (2 * SINUS_A) / 96.0
            gap_top.append((x, mem_y(x, lift)))
            gap_bot.append((x, FLOOR_Y))
        d.polygon(gap_top + gap_bot[::-1], fill=AIR + (255,))

    # 측방 창: 볼쪽 뼈벽 제거
    if window > 0:
        wx0, wy0, wx1, wy1 = WIN
        wcx, wcy = (wx0 + wx1) / 2, (wy0 + wy1) / 2
        k = ease(window)
        d.rounded_rectangle([lerp(wcx, wx0, k), lerp(wcy, wy0, k),
                             lerp(wcx, wx1, k), lerp(wcy, wy1, k)],
                            radius=int(36 * k) + 1, fill=AIR + (255,))
    if 0.03 < window < 0.98:
        dash_rect(d, WIN, ACCENT + (225,), width=5, dash=17)
    if window >= 0.98:
        d.rounded_rectangle(WIN, radius=37, outline=BONE_EDGE + (210,), width=4)

    # 이식재
    if graft > 0:
        fill_col = lerp_c(GRAFT, BONE, ease(mature))
        dot_col = lerp_c(lerp_c(fill_col, GRAFT_DOT, 0.85), fill_col, ease(mature) * 0.82)
        g = ease(graft)
        top, bot = [], []
        for i in range(97):
            x = SINUS_CX - SINUS_A + i * (2 * SINUS_A) / 96.0
            top.append((x, FLOOR_Y - g * (FLOOR_Y - mem_y(x, lift))))
            bot.append((x, FLOOR_Y))
        d.polygon(top + bot[::-1], fill=fill_col + (255,))
        d.line(top, fill=lerp_c(fill_col, BONE_EDGE, 0.55) + (255,), width=4, joint="curve")
        dot_a = 255
        if ease(mature) < 0.98:
            for (px, py, pr) in _PARTICLES:
                if py >= FLOOR_Y - g * (FLOOR_Y - mem_y(px, lift)) + pr * 0.4:
                    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=dot_col + (dot_a,))
        if window > 0.6:
            wy = lerp(WIN[3], WIN[1] - 4, g)
            wl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            wd = ImageDraw.Draw(wl)
            wd.rectangle([WIN[0], wy, WIN[2] + 2, WIN[3]], fill=fill_col + (255,))
            if ease(mature) < 0.98:
                for (px, py, pr) in _WIN_DOTS:
                    if py >= wy:
                        wd.ellipse([px - pr, py - pr, px + pr, py + pr], fill=dot_col + (dot_a,))
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).rounded_rectangle(WIN, radius=37, fill=255)
            wl.putalpha(ImageChops.multiply(wl.getchannel("A"), mask))
            layer.alpha_composite(wl)
            d = ImageDraw.Draw(layer)

    # 상악동 점막 (슈나이더막) — 상악동 윤곽을 따라 도는 얇은 막
    poly = sinus_polygon(lift)
    mem_c = lerp_c(MEM, BONE, ease(mature) * 0.45)
    mem_d = lerp_c(MEM_DEEP, BONE_EDGE, ease(mature) * 0.45)
    d.line(poly + [poly[0]], fill=mem_c + (255,), width=10, joint="curve")
    d.line(poly[:97], fill=mem_d + (255,), width=5, joint="curve")

    # 차폐막 + 봉합
    if cover > 0:
        a = int(225 * ease(cover))
        wx0, wy0, wx1, wy1 = WIN
        cl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        cd.rounded_rectangle([wx0 - 4, wy0 - 16, wx1 + 18, wy1 + 16], radius=32,
                             fill=COVER + (int(a * 0.42),), outline=COVER + (a,), width=6)
        for i in range(4):
            sy = wy0 + 16 + i * (wy1 - wy0 - 32) / 3.0
            cd.line([(wx0 + 2, sy), (wx1 + 14, sy)], fill=COVER + (int(a * 0.7),), width=4)
        layer.alpha_composite(cl)
        d = ImageDraw.Draw(layer)

    # 임플란트
    if implant > 0:
        k = ease(implant)
        off = (1 - k) * 380
        draw_fixture(d, SINUS_CX, CREST_Y + off, 612 + off)

    layer.alpha_composite(_gum_teeth())

    base = img.convert("RGBA")
    a = st.get("anat", 1.0)
    if a < 1.0:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    base.alpha_composite(layer)
    return base.convert("RGB")


def draw_label(img, text, tip, anchor, side="left", size=34, color=None, alpha=1.0):
    """지시선 + 라벨. tip=그림 위의 점, anchor=글자 왼쪽 위."""
    if alpha <= 0.01:
        return img
    color = color or INK
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(size, "Bold")
    a = int(255 * alpha)
    tw = text_w(d, text, f)
    ax, ay = anchor
    elbow = (ax - 14 if side == "left" else ax + tw + 14, ay + size // 2 + 6)
    d.line([tip, elbow], fill=ACCENT + (a,), width=4)
    d.line([elbow, (ax, elbow[1]) if side == "left" else (ax + tw, elbow[1])],
           fill=ACCENT + (a,), width=4)
    d.ellipse([tip[0] - 8, tip[1] - 8, tip[0] + 8, tip[1] + 8], fill=ACCENT + (a,))
    d.text((ax, ay), text, font=f, fill=color + (a,))
    base = img.convert("RGBA")
    base.alpha_composite(layer)
    return base.convert("RGB")


def draw_height_arrow(img, alpha=1.0, text="남은 뼈 높이", x=600):
    """치조정~상악동 바닥 사이 남은 뼈 높이를 양방향 화살표로."""
    if alpha <= 0.01:
        return img
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a = int(255 * alpha)
    d.line([(x, FLOOR_Y + 8), (x, CREST_Y - 8)], fill=ACCENT + (a,), width=6)
    for y, dy in ((FLOOR_Y + 8, 1), (CREST_Y - 8, -1)):
        d.polygon([(x, y), (x - 14, y + 24 * dy), (x + 14, y + 24 * dy)], fill=ACCENT + (a,))
    f = font(32, "Bold")
    tw = text_w(d, text, f)
    tx, ty = x + 26, (FLOOR_Y + CREST_Y) // 2 - 24
    d.rounded_rectangle([tx - 14, ty - 8, tx + tw + 14, ty + 48], radius=14, fill=BG + (int(a * 0.88),))
    d.text((tx, ty), text, font=f, fill=ACCENT + (a,))
    base = img.convert("RGBA")
    base.alpha_composite(layer)
    return base.convert("RGB")
