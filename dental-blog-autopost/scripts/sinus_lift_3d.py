# -*- coding: utf-8 -*-
"""
상악동 거상술 3D 렌더러 — numpy SDF 레이마칭.

2D 모식도(sinus_lift_diagram.py)가 "직관적이지 않다"는 피드백(2026-09-17)에 따라,
참조 릴스처럼 '표본을 실제로 보고 있는' 입체감을 내려고 새로 만들었다.
메시 대신 거리함수(SDF)를 쓰는 이유: 상악동 공동 파내기, 측방 창 뚫기, 점막 거상,
이식재 충전이 전부 CSG(빼기/교집합)라 파라미터 하나로 변형된다.

핵심 트릭 — **아치 좌표계**: 월드 좌표를 (x, y, 반지름-ARC_R)로 한 번 바꿔 놓으면
그 안에서는 전부 곧은 상자·타원체로 정의해도 결과는 치열궁을 따라 휘어진다.
모든 프리미티브가 이 u-공간에서 정의된다.

  img = render(dict(window=1, lift=1, graft=.5), w=720, h=900)   # PIL.Image
  x, y = project_u((0, -0.34, 0), w, h)                          # 라벨 지시선용

속도 메모: 마칭용 SDF에 표면 요철을 넣지 않는다(사인 호출이 스텝마다 곱절로 든다).
질감은 히트 지점에서 노멀을 흔들어 낸다. 프레임은 프로세스 풀로 병렬 렌더한다.
"""
import math

import numpy as np
from PIL import Image

F = np.float32

# ── 팔레트 (2D 카드뉴스와 같은 노랑/골드 배경) ────────────────────────
BG_TOP = np.array([0.100, 0.076, 0.020], F)
BG_BOT = np.array([0.032, 0.024, 0.006], F)

MAT_BONE, MAT_TOOTH, MAT_MEM, MAT_GRAFT, MAT_COVER, MAT_METAL = range(6)
ALBEDO = np.array([
    [0.90, 0.82, 0.63],   # 뼈 (상아색)
    [0.97, 0.95, 0.89],   # 치아
    [0.85, 0.40, 0.44],   # 상악동 점막
    [0.95, 0.88, 0.66],   # 뼈이식재
    [0.88, 0.88, 0.90],   # 차폐막
    [0.68, 0.72, 0.79],   # 임플란트
], F)
SPEC = np.array([0.06, 0.38, 0.55, 0.05, 0.26, 0.85], F)
SHINE = np.array([16.0, 64.0, 46.0, 10.0, 44.0, 120.0], F)
WRAP = np.array([0.18, 0.10, 0.30, 0.20, 0.15, 0.04], F)   # 뼈·이식재는 빛이 감싸는 느낌

# ── 아치 좌표계 ──────────────────────────────────────────────────────
ARC_C = np.array([0.0, 0.0, -1.12], F)   # 치열궁 중심
ARC_R = F(1.46)                          # 치열궁 반지름 (앞벽이 z≈0.34)

# ── u-공간 기하 (1 단위 ≈ 10mm) ──────────────────────────────────────
BONE_B = np.array([0.90, 0.58, 0.29], F)
BONE_R = F(0.075)
CREST_Y = F(-BONE_B[1] - BONE_R)              # 치조정 -0.655

SINUS_C = np.array([0.0, -0.02, -0.02], F)
SINUS_R = np.array([1.25, 0.31, 0.175], F)
FLOOR_Y = F(SINUS_C[1] - SINUS_R[1])          # 상악동 바닥 -0.34

WIN_C = np.array([0.0, 0.02, 0.30], F)
WIN_B = np.array([0.26, 0.20, 0.34], F)      # 최종 크기 (타원형 개창, z는 앞벽 관통)

LIFT_H = F(0.25)
MOLAR_X = F(0.62)
IMPLANT_X = F(0.0)
CUT_X = F(0.62)           # 어금니 한가운데를 지나는 절단면 (뿌리가 단면으로 보임)

TARGET = np.array([-0.06, -0.14, 0.26], F)
CAM_DIR = np.array([0.60, 0.30, 1.0], F)
CAM_DIST = F(5.8)
CAM = TARGET + CAM_DIR / np.linalg.norm(CAM_DIR) * CAM_DIST
FOV = 26.0

MAX_STEPS = 72
SURF_EPS = F(0.0016)


# ── SDF 프리미티브 ───────────────────────────────────────────────────
def _len(v):
    return np.sqrt(np.einsum("ij,ij->i", v, v))


def sd_round_box(p, c, b, r):
    q = np.abs(p - c) - b
    return _len(np.maximum(q, 0.0)) + np.minimum(q.max(axis=1), 0.0) - r


def sd_ellipsoid(p, c, r):
    q = (p - c) / r
    k0 = _len(q)
    return k0 * (k0 - 1.0) / np.maximum(_len(q / r), 1e-6)


def sd_cone_y(p, c, y0, y1, r0, r1):
    q = p - c
    t = np.clip((q[:, 1] - y0) / max(1e-6, y1 - y0), 0.0, 1.0)
    dr = np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2) - (r0 + (r1 - r0) * t)
    dy = np.maximum(y0 - q[:, 1], q[:, 1] - y1)
    return (np.minimum(np.maximum(dr, dy), 0.0)
            + np.sqrt(np.maximum(dr, 0.0) ** 2 + np.maximum(dy, 0.0) ** 2))


def sd_disc_z(p, c, a, b, t):
    """z축으로 납작한 타원 디스크 (납작한 타원체 SDF가 깨지는 걸 피하려고 씀)."""
    q = p - c
    e = np.sqrt((q[:, 0] / a) ** 2 + (q[:, 1] / b) ** 2)
    dr = (e - 1.0) * min(a, b)
    dz = np.abs(q[:, 2]) - t
    return (np.minimum(np.maximum(dr, dz), 0.0)
            + np.sqrt(np.maximum(dr, 0.0) ** 2 + np.maximum(dz, 0.0) ** 2))


def _dome_parts(p, cx, cz, rx, rz, h, floor_y):
    """바닥 평면 위에 높이 h로 부푼 돔 — 구면 캡이라 h가 0에 가까워도 안전하다."""
    h = max(float(h), 0.004)
    rs = (rx * rx + h * h) / (2 * h)
    d = p - np.array([cx, floor_y - (rs - h), cz], F)
    sph = _len(d) - rs
    rad = (np.sqrt(((p[:, 0] - cx) / rx) ** 2 + ((p[:, 2] - cz) / rz) ** 2) - 1.0) * min(rx, rz)
    below = floor_y - p[:, 1]
    return sph, rad, below


def sd_dome(p, cx, cz, rx, rz, h, floor_y):
    sph, rad, below = _dome_parts(p, cx, cz, rx, rz, h, floor_y)
    return np.maximum(np.maximum(sph, rad), below)


def sd_dome_shell(p, cx, cz, rx, rz, h, floor_y, t):
    sph, rad, below = _dome_parts(p, cx, cz, rx, rz, h, floor_y)
    return np.maximum(np.maximum(np.abs(sph) - t, rad), below - t)


def _grain(p, freq):
    return (np.sin(p[:, 0] * freq) * np.sin(p[:, 1] * freq * 1.13)
            * np.sin(p[:, 2] * freq * 0.91))


def to_arch(p):
    """월드 -> 아치 좌표 (x, y, 바깥쪽 깊이)."""
    q = p - ARC_C
    rad = np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2)
    return np.stack([q[:, 0], q[:, 1], rad - ARC_R], axis=1)


def from_arch(u):
    """아치 좌표 -> 월드 (라벨 위치 계산용)."""
    ux, uy, uz = float(u[0]), float(u[1]), float(u[2])
    rad = ARC_R + uz
    # x 는 그대로 두고 z 를 반지름에서 역산
    z = math.sqrt(max(1e-6, rad * rad - ux * ux))
    return np.array([ux + ARC_C[0], uy + ARC_C[1], z + ARC_C[2]], F)


# ── 장면 ─────────────────────────────────────────────────────────────
def _win_box(st):
    k = float(st.get("window", 0.0))
    if k <= 0.001:
        return None
    b = WIN_B.copy()
    b[0] *= 0.20 + 0.80 * k
    b[1] *= 0.20 + 0.80 * k
    return b


def sdf_parts(p_world, st):
    """구성요소별 거리 (6, N)."""
    u = to_arch(p_world)
    lift = float(st.get("lift", 0.0))
    graft = float(st.get("graft", 0.0))
    cover = float(st.get("cover", 0.0))
    implant = float(st.get("implant", 0.0))
    n = u.shape[0]

    # 뼈 덩어리: 아치를 따라 휜 블록에서 위 모서리를 둥글게 깎는다
    outer = sd_round_box(u, np.zeros(3, F), BONE_B, BONE_R)
    outer = np.maximum(outer, sd_ellipsoid(u, np.array([0.0, -0.40, 0.0], F),
                                           np.array([0.95, 1.16, 0.40], F)))
    # 치조능: 아래로 갈수록 좁아진다 (x축 방향 원통 두 개로 앞뒤를 깎음)
    for cz in (0.72, -0.72):
        cyl = np.sqrt((u[:, 1] + 1.36) ** 2 + (u[:, 2] - cz) ** 2) - 0.80
        outer = np.maximum(outer, -cyl)
    # 치아가 빠진 자리는 능선이 얕게 꺼져 있다
    outer = np.maximum(outer, -sd_ellipsoid(u, np.array([0.0, -0.70, 0.0], F),
                                            np.array([0.30, 0.15, 0.30], F)))
    outer = np.maximum(outer, u[:, 0] - CUT_X)          # 단면 절단
    fold = u.copy()
    fold[:, 0] = np.abs(fold[:, 0]) - MOLAR_X
    outer = np.minimum(outer, sd_ellipsoid(fold, np.array([0.0, -0.34, 0.20], F),
                                           np.array([0.17, 0.30, 0.13], F)))
    sinus = sd_ellipsoid(u, SINUS_C, SINUS_R)
    bone = np.maximum(outer, -sinus)
    wb = _win_box(st)
    if wb is not None:
        bone = np.maximum(bone, -sd_ellipsoid(u, WIN_C, wb))

    # 인접치 — x를 접어 프리미티브 하나로, 뿌리는 z를 접어 두 개로
    q = fold
    crown_c = np.array([0.0, CREST_Y - 0.16, 0.0], F)
    crown = sd_round_box(q, crown_c, np.array([0.135, 0.105, 0.115], F), F(0.055))
    qc = q - crown_c                                   # 교두 4개 (협측·설측 × 근심·원심)
    qc[:, 0] = np.abs(qc[:, 0]) - 0.075
    qc[:, 2] = np.abs(qc[:, 2]) - 0.062
    crown = np.minimum(crown, _len(qc - np.array([0.0, -0.10, 0.0], F)) - F(0.085))
    for gb in (np.array([0.24, 0.05, 0.016], F), np.array([0.016, 0.05, 0.24], F)):
        crown = np.maximum(crown, -sd_round_box(       # 교두 사이 홈
            q, np.array([0.0, CREST_Y - 0.34, 0.0], F), gb, F(0.018)))
    qr = q.copy()
    qr[:, 2] = np.abs(qr[:, 2]) - 0.070
    root = sd_cone_y(qr, np.zeros(3, F), CREST_Y - 0.03, FLOOR_Y - 0.02, F(0.070), F(0.026))
    tooth = np.maximum(np.minimum(crown, root), u[:, 0] - CUT_X)

    # 상악동 점막: 바닥의 거상된 돔 + 아직 벽에 붙어 있는 부분
    ry = F(max(0.006, lift * LIFT_H))
    mem = sd_dome_shell(u, float(SINUS_C[0]), float(SINUS_C[2]),
                        1.15, float(SINUS_R[2] * 0.93), ry, float(FLOOR_Y), F(0.013))
    wall = np.abs(sd_ellipsoid(u, SINUS_C, SINUS_R * F(0.98))) - F(0.012)
    mem = np.minimum(mem, np.maximum(wall, (FLOOR_Y + ry * 0.92) - u[:, 1]))
    mem = np.maximum(np.maximum(mem, u[:, 0] - CUT_X), outer)

    # 이식재: 돔 안쪽을 아래부터 채우고 창까지 올라온다
    if graft > 0.002:
        gd = sd_dome(u, float(SINUS_C[0]), float(SINUS_C[2]),
                     1.12, float(SINUS_R[2] * 0.91), graft * ry * 0.95, float(FLOOR_Y))
        if wb is not None:                       # 창 쪽으로도 이식재가 차오른다
            wf = sd_disc_z(u, np.array([WIN_C[0], WIN_C[1] - wb[1] * (1 - graft), WIN_C[2]], F),
                           float(wb[0] * 0.94), float(max(0.03, wb[1] * graft)), F(0.22))
            gd = np.minimum(gd, np.maximum(wf, outer))
        gd = np.maximum(np.maximum(gd, u[:, 0] - CUT_X), outer)
    else:
        gd = np.full(n, 1e3, F)

    # 차폐막: 창을 덮는 얇은 막
    if cover > 0.002 and wb is not None:
        k = 0.5 + 0.5 * cover
        cd = sd_disc_z(u, np.array([WIN_C[0], WIN_C[1], BONE_B[2] + BONE_R - 0.016], F),
                       float(wb[0] * 1.12 * k), float(wb[1] * 1.14 * k), F(0.012))
    else:
        cd = np.full(n, 1e3, F)

    # 임플란트
    if implant > 0.002:
        off = F((1.0 - implant) * 0.9)
        c = np.array([IMPLANT_X, -off, -0.02], F)
        idf = sd_cone_y(u, c, CREST_Y - 0.02, FLOOR_Y + 0.24, F(0.082), F(0.042))
        idf -= F(0.007) * np.sin((u[:, 1] + off) * 88.0)
        idf = np.maximum(idf, u[:, 0] - CUT_X)
    else:
        idf = np.full(n, 1e3, F)

    return np.stack([bone, tooth, mem, gd, cd, idf])


def sdf(p, st):
    return sdf_parts(p, st).min(axis=0)


# ── 카메라 ───────────────────────────────────────────────────────────
def _basis(spin=0.0):
    a = math.radians(spin)
    cam = np.array([CAM[0] * math.cos(a) + CAM[2] * math.sin(a), CAM[1],
                    -CAM[0] * math.sin(a) + CAM[2] * math.cos(a)], F)
    fwd = TARGET - cam
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0, 1, 0], F))
    right /= np.linalg.norm(right)
    return cam, fwd, right, np.cross(right, fwd)


def project(point, w, h, spin=0.0):
    """월드 좌표 -> 화면 픽셀."""
    cam, fwd, right, up = _basis(spin)
    v = np.asarray(point, F) - cam
    z = max(1e-4, float(v @ fwd))
    f = 1.0 / math.tan(math.radians(FOV) / 2)
    return (((float(v @ right) / z * f) / (w / float(h))) + 1) * 0.5 * w, \
           (1 - float(v @ up) / z * f) * 0.5 * h


def project_u(u_point, w, h, spin=0.0):
    """아치 좌표 -> 화면 픽셀 (라벨은 이쪽이 편하다)."""
    return project(from_arch(u_point), w, h, spin)


def _rays(w, h, spin):
    cam, fwd, right, up = _basis(spin)
    px, py = np.meshgrid(np.arange(w, dtype=F), np.arange(h, dtype=F))
    f = F(1.0 / math.tan(math.radians(FOV) / 2))
    sx = ((px + 0.5) / w * 2 - 1) * F(w / float(h))
    sy = 1 - (py + 0.5) / h * 2
    d = (fwd[None, None, :] * f + right[None, None, :] * sx[..., None]
         + up[None, None, :] * sy[..., None]).reshape(-1, 3).astype(F)
    d /= _len(d)[:, None]
    return cam, d


# ── 셰이딩 ───────────────────────────────────────────────────────────
def _unit(v):
    return (np.asarray(v, F) / np.linalg.norm(v)).astype(F)


LIGHTS = (
    (_unit([-0.55, 0.66, 0.62]), np.array([1.00, 0.96, 0.88], F), 1.05),   # 키
    (_unit([0.84, 0.10, 0.30]), np.array([0.52, 0.46, 0.34], F), 0.20),    # 필
    (_unit([0.10, -0.30, -0.95]), np.array([1.00, 0.84, 0.44], F), 0.30),  # 림
    (_unit([-0.26, 0.20, 0.94]), np.array([1.00, 0.95, 0.86], F), 0.45),   # 창 안쪽 조명
)
AMBIENT = np.array([0.15, 0.12, 0.08], F)


def _normals(p, st, eps=F(0.0018)):
    n = np.empty_like(p)
    for i in range(3):
        o = np.zeros(3, F)
        o[i] = eps
        n[:, i] = sdf(p + o, st) - sdf(p - o, st)
    return n / np.maximum(_len(n)[:, None], 1e-8)


def _ao(p, n, st):
    occ = np.zeros(p.shape[0], F)
    sca = F(1.0)
    for i in range(1, 5):
        hgt = F(0.018 + 0.055 * i)
        occ += (hgt - sdf(p + n * hgt, st)) * sca
        sca *= F(0.72)
    return np.clip(1.0 - 3.0 * occ, 0.0, 1.0)


def _soft_shadow(p, ldir, st, k=14.0, steps=22):
    res = np.ones(p.shape[0], F)
    t = np.full(p.shape[0], F(0.03))
    live = np.arange(p.shape[0])
    for _ in range(steps):
        if live.size == 0:
            break
        hgt = sdf(p[live] + ldir[None, :] * t[live][:, None], st)
        res[live] = np.minimum(res[live], k * hgt / np.maximum(t[live], 1e-4))
        t[live] += np.clip(hgt, 0.012, 0.18)
        live = live[(res[live] > 0.02) & (t[live] < 3.0)]
    return np.clip(res, 0.0, 1.0)


def render(st, w=720, h=900):
    spin = float(st.get("spin", 0.0))
    cam, dirs = _rays(w, h, spin)

    yy = np.repeat(np.linspace(0, 1, h, dtype=F), w)
    col = BG_TOP[None, :] * (1 - yy[:, None]) + BG_BOT[None, :] * yy[:, None]
    xx = np.tile(np.linspace(-1, 1, w, dtype=F), h)
    col *= (1.0 - 0.28 * (xx ** 2 + (yy * 2 - 1) ** 2))[:, None]

    oc = cam - np.array([0.0, -0.20, 0.34], F)
    b = dirs @ oc
    disc = b * b - (float(oc @ oc) - 1.45 ** 2)
    active = np.where(disc > 0)[0]
    if active.size == 0:
        return _to_image(col, w, h)

    d_act = dirs[active]
    t = np.maximum(-b[active] - np.sqrt(disc[active]), 0.0).astype(F)
    alive = np.arange(active.size)
    hit = np.zeros(active.size, bool)

    for _ in range(MAX_STEPS):
        if alive.size == 0:
            break
        dist = sdf(cam[None, :] + d_act[alive] * t[alive][:, None], st)
        t[alive] += dist * F(0.85)
        done = dist < SURF_EPS
        hit[alive[done]] = True
        alive = alive[(~done) & (t[alive] < 7.0)]

    idx = np.where(hit)[0]
    if idx.size:
        p = cam[None, :] + d_act[idx] * t[idx][:, None]
        n = _normals(p, st)
        mat = sdf_parts(p, st).argmin(axis=0)
        ao = _ao(p, n, st)
        alb, spec, shine, wrap = ALBEDO[mat].copy(), SPEC[mat], SHINE[mat], WRAP[mat]
        tint = 1.0 + 0.10 * _grain(to_arch(p) * 0.9, 5.0) - 0.05 * _grain(to_arch(p), 2.3)
        alb *= tint[:, None]

        # 절단면(법선이 +x)에 드러난 뼈는 해면골 느낌으로
        cut_face = (mat == MAT_BONE) & (n[:, 0] > 0.80)
        if cut_face.any():
            alb = alb.copy()
            alb[cut_face] = np.array([0.80, 0.70, 0.52], F)
        rough = np.where(mat == MAT_GRAFT, 0.40,
                         np.where(cut_face, 0.34, np.where(mat == MAT_BONE, 0.09, 0.0))).astype(F)
        if rough.any():
            up_ = to_arch(p)
            jit = np.stack([_grain(up_, 52.0) * 0.55 + _grain(up_, 13.0) * 0.75,
                            _grain(up_ * 1.21, 44.0) * 0.55 + _grain(up_ * 1.1, 11.0) * 0.75,
                            _grain(up_ * 0.83, 61.0) * 0.55 + _grain(up_ * 0.9, 15.0) * 0.75], 1)
            n = n + jit * rough[:, None]
            n /= np.maximum(_len(n)[:, None], 1e-8)

        v = -d_act[idx]
        shade = alb * AMBIENT[None, :] * ao[:, None]
        sha = _soft_shadow(p + n * F(0.012), LIGHTS[0][0], st)
        for li, (lv, lc, inten) in enumerate(LIGHTS):
            vis = sha if li == 0 else 1.0
            ndl = n @ lv
            ndl = np.maximum((ndl + wrap) / (1.0 + wrap), 0.0)     # wrap lighting
            shade += alb * (ndl * inten * vis)[:, None] * lc[None, :]
            hv = lv + v
            hv /= np.maximum(_len(hv)[:, None], 1e-8)
            sp = np.maximum(np.einsum("ij,ij->i", n, hv), 0.0) ** shine
            shade += (sp * spec * inten * vis)[:, None] * lc[None, :]
        shade *= (0.22 + 0.78 * ao)[:, None]
        col[active[idx]] = shade

    return _to_image(col, w, h)


def _to_image(col, w, h):
    col = np.clip(col, 0.0, None)
    col = col / (1.0 + col * 0.8)
    col = np.clip(col * 1.20, 0.0, 1.0) ** (1 / 2.2)
    return Image.fromarray((col.reshape(h, w, 3) * 255).astype(np.uint8), "RGB")
