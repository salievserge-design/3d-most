#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Путепровод 15+24+24+15 — комплект 3D-модели для 3D-печати (Bambu Lab A1)
========================================================================
Серия 3.503.1-81 (Гипропромстройпроект, ГОСТ Р 52748-2007):
  балки двутаврового сечения с предварительно напрягаемой арматурой:
    - Б2400.140.123  — L=24 м, b=1.40 м, h=1.23 м
    - Б1500.140.123  — L=15 м, b=1.40 м, h=1.23 м
Масштаб модели: 1:100 (1 м = 10 мм). Все детали размещаются на столе A1 (256 мм).

Состав комплекта:
  * балки (6 на пролёт = 24 шт.): 12 × 24 м, 12 × 15 м (шаг балок 2.0 м,
    зазор по верху плиты 0.6 м); в концевых зонах стенка плавно уширяется
    с 160 до 260, с обоих концов снизу — "обувь" 590×100×812
  * опоры на круглых стойках (3 шт.): 4 стойки Ø 0.8 м + ригель 13.0×1.7×1.0 м
    (верх, на него опираются балки) + ростверк 13.3×3.5×1.8 м (низ)
  * устои (2 шт.): стена + откос (печатаются отдельными частями)
  * участки омоноличивания (настилка) — 4 плиты по пролётам (ширина 12.0 м)

Запуск:  python3 generate_bridge.py
Результат: бинарные STL в ./stl/
Только стандартная библиотека Python (struct, math, os).

Геометрия параметрическая — правьте константы ниже (МЕТРЫ) и запускайте снова.
"""
import math
import os
import struct

SCALE = 10.0  # 1:100 — миллиметров модели на 1 метр прототипа
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl")
BED = 256.0   # стол Bambu Lab A1, мм

# ----------------------------------------------------------------------------
# Базовая триангуляция
# ----------------------------------------------------------------------------
def _sub(u, v):
    return (u[0]-v[0], u[1]-v[1], u[2]-v[2])

def _cross(u, v):
    return (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])

def signed_volume(tris):
    v = 0.0
    for a, b, c in tris:
        v += (a[0]*(b[1]*c[2]-c[1]*b[2])
              - a[1]*(b[0]*c[2]-c[0]*b[2])
              + a[2]*(b[0]*c[1]-c[0]*b[1]))
    return v / 6.0

class Mesh:
    def __init__(self):
        self.tris = []

    def tri(self, a, b, c):
        self.tris.append((a, b, c))

    def quad(self, a, b, c, d):
        self.tri(a, b, c)
        self.tri(a, c, d)

    def translate(self, dx, dy, dz):
        self.tris = [((a[0]+dx, a[1]+dy, a[2]+dz),
                      (b[0]+dx, b[1]+dy, b[2]+dz),
                      (c[0]+dx, c[1]+dy, c[2]+dz)) for a, b, c in self.tris]

    def box(self, x0, x1, y0, y1, z0, z1):
        """Параллелепипед с наружной ориентацией (правый винт)."""
        def P(i, j, k):
            return (x0 if i == 0 else x1, y0 if j == 0 else y1, z0 if k == 0 else z1)
        # -X
        self.tri(P(0,0,0), P(0,1,1), P(0,1,0))
        self.tri(P(0,0,0), P(0,0,1), P(0,1,1))
        # +X
        self.tri(P(1,0,0), P(1,1,1), P(1,0,1))
        self.tri(P(1,0,0), P(1,1,0), P(1,1,1))
        # -Y
        self.tri(P(0,0,0), P(1,0,0), P(1,0,1))
        self.tri(P(0,0,0), P(1,0,1), P(0,0,1))
        # +Y
        self.tri(P(0,1,0), P(0,1,1), P(1,1,1))
        self.tri(P(0,1,0), P(1,1,1), P(1,1,0))
        # -Z
        self.tri(P(0,0,0), P(0,1,0), P(1,1,0))
        self.tri(P(0,0,0), P(1,1,0), P(1,0,0))
        # +Z
        self.tri(P(0,0,1), P(1,0,1), P(1,1,1))
        self.tri(P(0,0,1), P(1,1,1), P(0,1,1))

    def cylinder(self, cx, cy, r, z0, z1, n=48):
        p0, p1 = [], []
        for i in range(n):
            t = 2.0 * math.pi * i / n
            p0.append((cx + r*math.cos(t), cy + r*math.sin(t), z0))
            p1.append((cx + r*math.cos(t), cy + r*math.sin(t), z1))
        for i in range(n):
            j = (i + 1) % n
            self.quad(p0[i], p0[j], p1[j], p1[i])
        c0, c1 = (cx, cy, z0), (cx, cy, z1)
        for i in range(n):
            j = (i + 1) % n
            self.tri(c1, p1[i], p1[j])
            self.tri(c0, p0[j], p0[i])

    def extrude_profile(self, profile, x0, x1):
        """profile: [(y, z), ...] контур в плоскости YZ, CCW (y вправо, z вверх),
        экструзия вдоль X. Ориентация граней — наружная (правый винт).
        Торцы триангулируются "защипыванием ушей" (работает и для вогнутых контуров)."""
        n = len(profile)
        for i in range(n):
            j = (i + 1) % n
            a, b = profile[i], profile[j]
            a0, a1 = (x0, a[0], a[1]), (x1, a[0], a[1])
            b0, b1 = (x0, b[0], b[1]), (x1, b[0], b[1])
            self.tri(a0, b1, a1)
            self.tri(a0, b0, b1)
        ears = ear_clipping(profile)
        for (i, j, k) in ears:
            p_i, p_j, p_k = profile[i], profile[j], profile[k]
            self.tri((x1, p_i[0], p_i[1]), (x1, p_j[0], p_j[1]), (x1, p_k[0], p_k[1]))  # +X
            self.tri((x0, p_i[0], p_i[1]), (x0, p_k[0], p_k[1]), (x0, p_j[0], p_j[1]))  # -X

    def taper_profile(self, p0, p1, x0, x1):
        """Ленточный переход (loft) между двумя одноимёнными контурами (CCW,
        [(y, z), ...]) в сечениях x0 и x1: стенка плавно уширяется/сужается.
        Ориентация граней — та же, что в extrude_profile."""
        n = len(p0)
        for i in range(n):
            j = (i + 1) % n
            a_i = (x0, p0[i][0], p0[i][1]); a_j = (x0, p0[j][0], p0[j][1])
            b_i = (x1, p1[i][0], p1[i][1]); b_j = (x1, p1[j][0], p1[j][1])
            self.tri(a_i, b_j, b_i)
            self.tri(a_i, a_j, b_j)
        for (i, j, k) in ear_clipping(p0):
            self.tri((x0, p0[i][0], p0[i][1]), (x0, p0[k][0], p0[k][1]),
                     (x0, p0[j][0], p0[j][1]))  # -X
        for (i, j, k) in ear_clipping(p1):
            self.tri((x1, p1[i][0], p1[i][1]), (x1, p1[j][0], p1[j][1]),
                     (x1, p1[k][0], p1[k][1]))  # +X

    def prism_xz(self, pts, y0, y1):
        """Треугольник в плоскости XZ (3 точки (x, z)), экструзия вдоль Y."""
        a, b, c = pts
        a0, a1 = (a[0], y0, a[1]), (a[0], y1, a[1])
        b0, b1 = (b[0], y0, b[1]), (b[0], y1, b[1])
        c0, c1 = (c[0], y0, c[1]), (c[0], y1, c[1])
        self.tri(a0, b0, c0)
        self.tri(a1, c1, b1)
        self.quad(a0, a1, b1, b0)
        self.quad(b0, b1, c1, c0)
        self.quad(c0, c1, a1, a0)

def _cross2d(o, a, b):
    return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

def _in_tri(p, a, b, c):
    d1, d2, d3 = _cross2d(a, b, p), _cross2d(b, c, p), _cross2d(c, a, p)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)

def ear_clipping(pts):
    """Триангуляция простого полигона (CCW) методом отсечения ушей.
    Возвращает тройки индексов (i, j, k)."""
    idx = list(range(len(pts)))
    tris = []
    guard = 0
    while len(idx) > 3:
        n = len(idx)
        ear_found = False
        for k in range(n):
            i = (k - 1) % n
            m = (k + 1) % n
            a, b, c = pts[idx[i]], pts[idx[k]], pts[idx[m]]
            if _cross2d(a, b, c) <= 0:
                continue
            ear = True
            for l in idx:
                if l in (idx[i], idx[k], idx[m]):
                    continue
                if _in_tri(pts[l], a, b, c):
                    ear = False
                    break
            if ear:
                tris.append((idx[i], idx[k], idx[m]))
                idx.pop(k)
                ear_found = True
                break
        if not ear_found:  # дегенерация — снимаем первый вершинный угол
            tris.append((idx[-1], idx[0], idx[1]))
            idx.pop(1)
        guard += 1
        if guard > 10000:
            raise RuntimeError("ear_clipping: не сходится")
    tris.append((idx[0], idx[1], idx[2]))
    return tris

def normalize(m):
    """Гарантия наружной ориентации треугольников (через знак объёма)."""
    if signed_volume(m.tris) < 0:
        m.tris = [(a, c, b) for a, b, c in m.tris]
    return m

def merge(meshes):
    out = Mesh()
    for m in meshes:
        normalize(m)
        out.tris.extend(m.tris)
    return out

def bbox(m):
    xs, ys, zs = [], [], []
    for t in m.tris:
        for p in t:
            xs.append(p[0]); ys.append(p[1]); zs.append(p[2])
    return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))

def write_stl(path, mesh):
    normalize(mesh)
    with open(path, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", len(mesh.tris)))
        for a, b, c in mesh.tris:
            n = _cross(_sub(b, a), _sub(c, a))
            f.write(struct.pack("<3f", *n))
            for p in (a, b, c):
                f.write(struct.pack("<3f", *p))
            f.write(struct.pack("<H", 0))

# ----------------------------------------------------------------------------
# Геометрия путепровода. Все размеры в МЕТРАХ (прототип), ×SCALE при генерации.
# ----------------------------------------------------------------------------
# Пролётная схема и опоры (ось X — вдоль моста)
SPANS = [(0.0, 15.0), (15.0, 39.0), (39.0, 63.0), (63.0, 78.0)]      # 15+24+24+15
PIER_X = (15.0, 39.0, 63.0)                                          # центры опор

# Балка Б.140.123 (двутавр, серия 3.503.1-81, лист 3.503.1-81.7-1-11):
# h = 1230 + "обувь" 100. Верхняя плита 1400×150 соединяется со стенкой
# большой выпуклостью; стенка переходит в нижнее уширение (590) плавной
# кривой; внизу, с обоих концов, выступает "обувь" 590×100×812 (на неё
# балка опирается на ригель/устой). Форма снята с чертежа (сечения А-А/Б-Б).
# В концевых зонах стенка плавно уширяется с 160 до 260 (сечение Б-Б).
# Значения — мм модели (1:100), z от нижней грани "обуви", y от оси балки.
BEAM_MID_R = [  # среднее сечение (А-А): стенка 160
    (7.0, 13.3), (7.0, 11.8),                       # верхняя плита (t = 1,5)
    (6.2, 11.62), (5.0, 11.40), (4.0, 11.05),       # выпуклость: плита -> стенка
    (3.2, 10.60), (2.5, 10.10), (1.9, 9.60),
    (1.5, 9.20), (1.2, 8.85), (1.0, 8.60), (0.8, 8.45),
    (0.8, 4.5),                                     # стенка 160
    (0.85, 4.40), (0.95, 4.15), (1.12, 3.85),       # выпуклость: стенка -> уширение
    (1.40, 3.50), (1.75, 3.15), (2.15, 2.80),
    (2.55, 2.48), (2.85, 2.20), (3.00, 1.95),
    (3.05, 1.65), (3.00, 1.30), (2.95, 1.00),       # основание уширения 590
]
BEAM_END_R = [  # концевое сечение (Б-Б): стенка 260
    (7.0, 13.3), (7.0, 11.8),
    (6.2, 11.62), (5.0, 11.40), (4.0, 11.05),
    (3.2, 10.60), (2.5, 10.10), (1.9, 9.60),
    (1.5, 9.20), (1.42, 8.95), (1.34, 8.72), (1.3, 8.55),
    (1.3, 4.5),                                     # стенка 260
    (1.35, 4.30), (1.45, 4.10), (1.65, 3.80),
    (1.95, 3.45), (2.30, 3.05), (2.65, 2.70),
    (2.90, 2.40), (2.98, 2.15), (2.95, 1.95),
    (3.00, 1.65), (2.97, 1.30), (2.95, 1.00),
]
SHOE_L, SHOE_W, SHOE_H = 8.12, 2.95, 1.0           # "обувь": длина, полуширина, высота (мм модели)
END_Z, TAPER_L = 8.12, 10.0                         # длина концевой зоны и плавного уширения стенки, мм модели

def _full_ccw(right):
    """Полный контур (правая половина top->bottom + зеркало) в повороте CCW."""
    full = right + [(-y, z) for (y, z) in reversed(right)]
    return list(reversed(full))  # CW -> CCW

def _blend(p0, p1, t):
    return [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            for a, b in zip(p0, p1)]

def make_beam(L_m):
    L = L_m * SCALE
    mid, end = _full_ccw(BEAM_MID_R), _full_ccw(BEAM_END_R)
    half = _full_ccw(_blend(BEAM_END_R, BEAM_MID_R, 0.25))  # промежуточный профиль (ease-in)
    m = Mesh()
    # концевые зоны (стенка 260) + "обувь"
    m.extrude_profile(end, 0.0, END_Z)
    m.extrude_profile(end, L - END_Z, L)
    m.box(0.0, END_Z, -SHOE_W, SHOE_W, -0.05, SHOE_H)
    m.box(L - END_Z, L, -SHOE_W, SHOE_W, -0.05, SHOE_H)
    # плавное уширение стенки 260 -> 160 (две ступени, закруглённый старт)
    m.taper_profile(end, half, END_Z, END_Z + TAPER_L / 2)
    m.taper_profile(half, mid, END_Z + TAPER_L / 2, END_Z + TAPER_L)
    m.taper_profile(mid, half, L - END_Z - TAPER_L, L - END_Z - TAPER_L / 2)
    m.taper_profile(half, end, L - END_Z - TAPER_L / 2, L - END_Z)
    # средняя часть (стенка 160)
    m.extrude_profile(mid, END_Z + TAPER_L, L - END_Z - TAPER_L)
    return m

# Раскладка балок в поперечном сечении: 6 шт. × 1.40 м, шаг 2.0 м,
# зазор между балками по верху плиты 0.6 м (настилка монолитная, 12.0 м)
BEAM_Y = (-5.0, -3.0, -1.0, 1.0, 3.0, 5.0)   # центры, м
BEAM_Z = 5.0                                  # низ "обуви" балки = верх ригеля/устоя

# Опора на круглых стойках (отметки: ростверк 0..1.8, стойки 1.8..4.0, ригель 4.0..5.0)
PIER = dict(
    rosv_w=13.3, rosv_l=3.5, rosv_z0=0.0, rosv_h=1.8,   # ростверк (низ опоры)
    col_d=0.8, col_y=(-3.0, -1.0, 1.0, 3.0),
    col_z0=1.8, col_z1=4.0,                             # 4 круглые стойки
    rigel_w=13.0, rigel_l=1.7, rigel_h=1.0,             # ригель (верх, на него опираются балки)
)
PIER_RIGEL_Z0 = 4.0

# Устои
ABU = dict(wall_w=1.4, wall_wide=12.4, wall_h=5.0, slope_run=1.6)

# Настилка (участки омоноличивания): лежит на верхней плите балок
DECK = dict(wide=12.0, th=0.35, z=6.33)
DECK_SPANS = [(-0.45, 14.95), (15.05, 38.95), (39.10, 62.95), (63.35, 78.45)]

# Торцы балок: "обувь" (0.812 м) ложится на ригель/устой (ось опоры = середина "обуви"
# с зазором 0.006 м — визуально на опоре)
BEAM_SPANS = [(0.00, 15.40), (14.60, 39.40), (38.60, 63.40), (62.60, 78.00)]

# ----------------------------------------------------------------------------
def build_assembly():
    """Весь мост в сборе (для предпросмотра). Координаты — метры, z вверх."""
    ms = []
    for (x0, x1) in BEAM_SPANS:
        L = x1 - x0
        for yc in BEAM_Y:
            b = make_beam(L)
            b.translate(x0 * SCALE, yc * SCALE, BEAM_Z * SCALE)
            ms.append(b)
    for xc in PIER_X:
        p = PIER
        rosv = Mesh(); rosv.box((xc - p["rosv_l"]/2) * SCALE, (xc + p["rosv_l"]/2) * SCALE,
                                -p["rosv_w"]/2 * SCALE, p["rosv_w"]/2 * SCALE,
                                p["rosv_z0"] * SCALE, (p["rosv_z0"] + p["rosv_h"]) * SCALE)
        rig = Mesh(); rig.box((xc - p["rigel_l"]/2) * SCALE, (xc + p["rigel_l"]/2) * SCALE,
                              -p["rigel_w"]/2 * SCALE, p["rigel_w"]/2 * SCALE,
                              PIER_RIGEL_Z0 * SCALE, (PIER_RIGEL_Z0 + p["rigel_h"]) * SCALE)
        ms.append(rosv); ms.append(rig)
        for dy in p["col_y"]:
            c = Mesh()
            c.cylinder(xc * SCALE, dy * SCALE, p["col_d"]/2 * SCALE,
                       p["col_z0"] * SCALE, p["col_z1"] * SCALE, n=36)
            ms.append(c)
    a = ABU
    for x_face, sdir in ((0.0, +1), (SPANS[-1][1], -1)):
        # стена устоя (за гранью)
        w = Mesh()
        if sdir > 0:
            w.box(-a["wall_w"] * SCALE, 0.0, -a["wall_wide"]/2 * SCALE, a["wall_wide"]/2 * SCALE, 0, a["wall_h"] * SCALE)
        else:
            w.box(x_face * SCALE, (x_face + a["wall_w"]) * SCALE,
                  -a["wall_wide"]/2 * SCALE, a["wall_wide"]/2 * SCALE, 0, a["wall_h"] * SCALE)
        w.translate(0, 0, 0)
        ms.append(w)
        # откос (на стороне пролёта)
        s = Mesh()
        if sdir > 0:
            s.prism_xz([(0.0, a["wall_h"]), (0.0, 0.0), (a["slope_run"], 0.0)],
                       -a["wall_wide"]/2 * SCALE, a["wall_wide"]/2 * SCALE)
        else:
            s.prism_xz([(0.0, a["wall_h"]), (0.0, 0.0), (-a["slope_run"], 0.0)],
                       -a["wall_wide"]/2 * SCALE, a["wall_wide"]/2 * SCALE)
        s.translate(x_face * SCALE, 0, 0)
        ms.append(s)
    d = DECK
    for (x0, x1) in DECK_SPANS:
        dk = Mesh()
        dk.box(x0 * SCALE, x1 * SCALE, -d["wide"]/2 * SCALE, d["wide"]/2 * SCALE,
               d["z"] * SCALE, (d["z"] + d["th"]) * SCALE)
        ms.append(dk)
    return merge(ms)

# ----------------------------------------------------------------------------
# Печатные файлы: каждая деталь (группа деталей) — один STL под Bambu Lab A1
# ----------------------------------------------------------------------------
def _file_beams(L_m, count, pitch_mm=19.0):
    ms = []
    for i in range(count):
        b = make_beam(L_m)
        b.translate(0.0, i * pitch_mm, 0.0)
        ms.append(b)
    return ms

def _file_columns(n, d_mm=10.0, h_mm=35.0):
    ms = []
    for i in range(n):
        c = Mesh()
        c.cylinder(5.0 + (i % 3) * 15.0, 5.0 + (i // 3) * 15.0, d_mm / 2, 0.0, h_mm)
        ms.append(c)
    return ms

def _file_pier_part(lx, ly, lz):
    """3 шт. длинной плиты (lx по мосту, ly поперёк), мм, укладываются в стол A1:
    одна по X + две поперёк во втором ряду."""
    a = Mesh(); a.box(0, lx, 0, ly, 0, lz)
    b = Mesh(); b.box(0, ly, ly + 5, ly + 5 + lx, 0, lz)
    c = Mesh(); c.box(ly + 5, 2 * ly + 5, ly + 5, ly + 5 + lx, 0, lz)
    return [a, b, c]

def _file_abutment_parts(part, n, pitch_mm=89.0):
    ms = []
    for i in range(n):
        m = Mesh()
        if part == "wall":
            m.box(0, ABU["wall_w"] * SCALE, -ABU["wall_wide"]/2 * SCALE, ABU["wall_wide"]/2 * SCALE,
                  0, ABU["wall_h"] * SCALE)
        else:
            m.prism_xz([(0.0, ABU["wall_h"] * SCALE), (0.0, 0.0), (ABU["slope_run"] * SCALE, 0.0)],
                       -ABU["wall_wide"]/2 * SCALE, ABU["wall_wide"]/2 * SCALE)
        m.translate(0.0, i * pitch_mm, 0.0)
        ms.append(m)
    return ms

def _file_decks(lengths_m, row_gap_mm=5.0):
    ms = []
    y = 0.0
    for L in lengths_m:
        dk = Mesh()
        dk.box(0.0, L * SCALE, -DECK["wide"]/2 * SCALE, DECK["wide"]/2 * SCALE,
               0.0, DECK["th"] * SCALE)
        dk.translate(0.0, y, 0.0)
        ms.append(dk)
        y += DECK["wide"] * SCALE + row_gap_mm
    return ms

def build_print_files():
    return [
        ("01_beam_24m_12pcs.stl",      _file_beams(24.8, 12)),
        ("02_beam_15m_12pcs.stl",      _file_beams(15.4, 12)),
        ("03_columns_12pcs.stl",       _file_columns(12, d_mm=8.0, h_mm=22.0)),
        # ригель 13.0×1.7×1.0 м (верх опоры, на него опираются балки)
        ("04_rigels_3pcs.stl",         _file_pier_part(130.0, 17.0, 10.0)),
        # ростверк 13.3×3.5×1.8 м (низ опоры)
        ("05_rosvverks_3pcs.stl",      _file_pier_part(133.0, 35.0, 18.0)),
        ("06_abutment_walls_2pcs.stl", _file_abutment_parts("wall", 2, pitch_mm=129.0)),
        ("07_abutment_slopes_2pcs.stl",_file_abutment_parts("slope", 2, pitch_mm=129.0)),
        ("08_deck_24m_2pcs.stl",       _file_decks([38.95 - 15.05, 62.95 - 39.10])),
        ("09_deck_15m_2pcs.stl",       _file_decks([14.95 - (-0.45), 78.45 - 63.35])),
    ]

# ----------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    print("=== Генерация STL (масштаб 1:%d) -> %s ===" % (int(SCALE * 100 / 10), OUT))
    total = 0
    for name, meshes in build_print_files():
        m = merge(meshes)
        write_stl(os.path.join(OUT, name), m)
        bb = bbox(m)
        dx, dy, dz = bb[3]-bb[0], bb[4]-bb[1], bb[5]-bb[2]
        fits = "OK" if (dx <= BED and dy <= BED and dz <= BED) else "НЕ ВЛЕЗЕТ!"
        print("  %-30s  %-9s  %5.1f x %5.1f x %5.1f мм  (траиангл.: %d)  [A1: %s]"
              % (name, "x%d" % len(meshes), dx, dy, dz, len(m.tris), fits))
        total += len(m.tris)
    asm = build_assembly()
    write_stl(os.path.join(OUT, "10_assembly_preview.stl"), asm)
    bb = bbox(asm)
    print("  %-30s  собранный мост (только просмотр, не печатать) %5.1f x %5.1f x %5.1f мм"
          % ("10_assembly_preview.stl", bb[3]-bb[0], bb[4]-bb[1], bb[5]-bb[2]))
    print("Всего треугольников: %d" % (total + len(asm.tris)))

if __name__ == "__main__":
    main()
