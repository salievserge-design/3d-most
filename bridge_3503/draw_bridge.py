#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Чертёж путепровода 15+24+24+15 (серия 3.503.1-81, масштаб 1:100) -> drawing.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle

# ---------- палитра ----------
C_FILL   = "#e9e3d3"   # бетон светлый
C_FILL2  = "#d9d1bc"   # бетон средный
C_DECK   = "#c9bea5"   # настилка
C_EDGE   = "#4d463a"
C_GROUND = "#8a7f6a"
C_TEXT   = "#2e2a24"

# ---------- параметры (метры) ----------
SPANS      = [(0.0, 15.0), (15.0, 39.0), (39.0, 63.0), (63.0, 78.0)]
BEAM_SPANS = [(0.00, 15.40), (14.60, 39.40), (38.60, 63.40), (62.60, 78.00)]
DECK_SPANS = [(-0.45, 14.95), (15.05, 38.95), (39.10, 62.95), (63.35, 78.45)]
PIER_X     = (15.0, 39.0, 63.0)
BEAM_Y     = (-5.0, -3.0, -1.0, 1.0, 3.0, 5.0)   # 6 балок, шаг 2.0, зазор 0.6
BZ         = 5.0     # низ "обуви" балки
BH         = 1.23    # высота балки (до низа уширения)
DZ         = 6.33    # низ настилки
DT         = 0.35    # толщина настилки

# Сечение балки Б.140.123 по чертежу 3.503.1-81.7-1-11 (сечение А-А), метры.
# z от нижней грани "обуви"; плита 1.40x0.15, стенка 0.16, уширение 0.59,
# стыки - большие выпуклости; "обувь" 0.59x0.10 с обоих концов (длина 0.812).
BEAM_R = [
    (0.70, 1.33), (0.70, 1.18),
    (0.62, 1.162), (0.50, 1.140), (0.40, 1.105), (0.32, 1.060), (0.25, 1.010),
    (0.19, 0.960), (0.15, 0.920), (0.12, 0.885), (0.10, 0.860), (0.08, 0.845),
    (0.08, 0.45),
    (0.085, 0.440), (0.095, 0.415), (0.112, 0.385), (0.14, 0.350), (0.175, 0.315),
    (0.215, 0.280), (0.255, 0.248), (0.285, 0.220), (0.30, 0.195),
    (0.305, 0.165), (0.30, 0.130), (0.295, 0.10),
]
SHOE_L, SHOE_W, SHOE_H = 0.812, 0.295, 0.10

# Концевое сечение (Б-Б): стенка 260 — в разрезе на опоре балка видна с уширенной стенкой
BEAM_R_END = [
    (0.70, 1.33), (0.70, 1.18),
    (0.62, 1.162), (0.50, 1.140), (0.40, 1.105), (0.32, 1.060), (0.25, 1.010),
    (0.19, 0.960), (0.15, 0.920), (0.142, 0.895), (0.134, 0.872), (0.13, 0.855),
    (0.13, 0.45),
    (0.135, 0.430), (0.145, 0.410), (0.165, 0.380), (0.195, 0.345), (0.230, 0.305),
    (0.265, 0.270), (0.290, 0.240), (0.298, 0.215), (0.295, 0.195),
    (0.300, 0.165), (0.297, 0.130), (0.295, 0.10),
]

def beam_poly(yc, zoff=0.0, profile=BEAM_R):
    p = [(yc + y, zoff + z) for (y, z) in profile]
    p += [(yc - y, zoff + z) for (y, z) in reversed(profile)]
    return p

fig = plt.figure(figsize=(17.2, 10.2), dpi=150)
gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1.0], hspace=0.30, wspace=0.14,
                      left=0.05, right=0.985, top=0.90, bottom=0.06)
axE = fig.add_subplot(gs[0, :])   # вид спереди (разрез поперечный? нет — продольный)
axC = fig.add_subplot(gs[1, 0])   # разрез поперечный
axP = fig.add_subplot(gs[1, 1])   # план

fig.text(0.5, 0.965, "ПУТЕПРОВОД  15 + 24 + 24 + 15  м  ·  СЕРИЯ 3.503.1-81  ·  МАСШТАБ МОДЕЛИ 1:100",
         ha="center", va="center", fontsize=15, weight="bold", color=C_TEXT)
fig.text(0.5, 0.940,
         "Балки Б2400.140.123 / Б1500.140.123 (b = 1,40 м, h = 1,23 м + обу́вь 0,10 м; стыки — выпуклостями, "
         "в концевых зонах стенка 0,16 → 0,26 м)",
         ha="center", va="center", fontsize=8.5, color="#6a6254")
fig.text(0.5, 0.913,
         "6 балок на пролёт (зазор по верху плиты 0,6 м) · опоры: 4 стойки Ø 0,8 м, ригель 13,0 м, "
         "ростверк 13,3 м · настилка (участки омоноличивания) 12,0 × 0,35 м",
         ha="center", va="center", fontsize=8.5, color="#6a6254")

# ================= ЭЛЕВАЦИЯ =================
axE.set_xlim(-3.2, 81.5)
axE.set_ylim(-1.1, 8.4)
axE.set_aspect("equal")
axE.axis("off")

# земля
axE.plot([-2.8, 81.2], [0, 0], color=C_GROUND, lw=1.6)
for x in range(-3, 82, 2):
    axE.plot([x, x - 0.9], [0, -0.55], color=C_GROUND, lw=0.5)

# устои
axE.add_patch(Polygon([(-1.4, 0), (1.6, 0), (0, 5), (-1.4, 5)], closed=True,
                      facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.2))
axE.add_patch(Polygon([(76.4, 0), (79.4, 0), (79.4, 5), (78, 5)], closed=True,
                      facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.2))

# опоры: ростверк (низ) 13.3×3.5×1.8, стойки Ø 0.8, ригель (верх) 13.0×1.7×1.0
for xc in PIER_X:
    axE.add_patch(Rectangle((xc - 1.75, 0), 3.5, 1.8, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))
    axE.add_patch(Rectangle((xc - 0.4, 1.8), 0.8, 2.2, facecolor=C_FILL, edgecolor=C_EDGE, lw=1.0))
    axE.add_patch(Rectangle((xc - 0.85, 4.0), 1.7, 1.0, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))

# балки (тело 1,23 м + "обувь" 0,10 м с обоих концов)
for (x0, x1) in BEAM_SPANS:
    axE.add_patch(Rectangle((x0, BZ + 0.10), x1 - x0, BH, facecolor="#e4dcbd", edgecolor=C_EDGE, lw=1.3))
    axE.add_patch(Rectangle((x0, BZ), SHOE_L, SHOE_H, facecolor="#ddd5c0", edgecolor=C_EDGE, lw=1.0))
    axE.add_patch(Rectangle((x1 - SHOE_L, BZ), SHOE_L, SHOE_H, facecolor="#ddd5c0", edgecolor=C_EDGE, lw=1.0))
    axE.plot([x0, x1], [BZ + 1.18, BZ + 1.18], color=C_EDGE, lw=0.5, ls=(0, (4, 3)))  # низ плиты
    axE.plot([x0, x1], [BZ + 0.10, BZ + 0.10], color=C_EDGE, lw=0.5, ls=(0, (4, 3)))  # низ уширения

# настилка
for (x0, x1) in DECK_SPANS:
    axE.add_patch(Rectangle((x0, DZ), x1 - x0, DT, facecolor=C_DECK, edgecolor=C_EDGE,
                            lw=0.9, hatch="///", alpha=0.95))

# стрелки пролётов
for i, (x0, x1) in enumerate(SPANS):
    z = 7.45
    axE.annotate("", xy=(x1, z), xytext=(x0, z),
                 arrowprops=dict(arrowstyle="<->", color=C_TEXT, lw=1.0))
    axE.text((x0 + x1) / 2, z + 0.25, f"{x1 - x0:.0f} м", ha="center", fontsize=11, weight="bold")

# подписи
axE.text(-1.4, -0.75, "У-1", ha="center", fontsize=10)
axE.text(79.4, -0.75, "У-2", ha="center", fontsize=10)
for i, xc in enumerate(PIER_X):
    axE.text(xc, -0.75, f"П-{i+1}", ha="center", fontsize=10)
axE.annotate("балка Б2400.140.123\n(h = 1,23 м)", xy=(27, 5.9), xytext=(22.5, 3.1),
             fontsize=9.5, color=C_TEXT,
             arrowprops=dict(arrowstyle="->", color=C_TEXT, lw=0.9))
axE.annotate("настилка (участок омоноличивания)\nt = 0,35 м", xy=(54, 6.55), xytext=(57.5, 8.15),
             fontsize=9.5, color=C_TEXT,
             arrowprops=dict(arrowstyle="->", color=C_TEXT, lw=0.9))
axE.text(-2.6, 7.9, "Вид спереди", fontsize=11, weight="bold")

# ================= РАЗРЕЗ (поперечный, на опоре П-1) =================
axC.set_xlim(-7.4, 7.4)
axC.set_ylim(-1.1, 8.4)
axC.set_aspect("equal")
axC.axis("off")

axC.plot([-7.1, 7.1], [0, 0], color=C_GROUND, lw=1.6)
for x in range(-7, 8, 2):
    axC.plot([x, x - 0.5], [0, -0.55], color=C_GROUND, lw=0.5)

# ростверк (низ), 4 стойки, ригель (верх — на него опираются балки)
axC.add_patch(Rectangle((-6.65, 0), 13.3, 1.8, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.1))
for yc in (-3.0, -1.0, 1.0, 3.0):
    axC.add_patch(Rectangle((yc - 0.4, 1.8), 0.8, 2.2, facecolor=C_FILL, edgecolor=C_EDGE, lw=1.1))
axC.add_patch(Rectangle((-6.5, 4.0), 13.0, 1.0, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.1))

# балки (6 шт.; в концевой зоне — стенка 260, сечение Б-Б)
for yc in BEAM_Y:
    axC.add_patch(Rectangle((yc - SHOE_W, BZ), 2 * SHOE_W, SHOE_H,
                            facecolor="#ddd5c0", edgecolor=C_EDGE, lw=1.0))
    axC.add_patch(Polygon(beam_poly(yc, BZ, BEAM_R_END), closed=True,
                          facecolor=C_FILL, edgecolor=C_EDGE, lw=1.1))

# настилка
axC.add_patch(Rectangle((-6.0, DZ), 12.0, DT, facecolor=C_DECK, edgecolor=C_EDGE,
                        lw=0.9, hatch="///", alpha=0.95))

# подписи
axC.annotate("настилка (участок\nомоноличивания)", xy=(4.4, DZ + 0.15), xytext=(4.6, 7.75),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("балка Б.140.123\n(концевая зона, стенка 0,26)", xy=(0.7, 6.66), xytext=(-0.6, 7.15),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("ригель 13,0 м\n(балки опираются на него)", xy=(4.9, 4.5), xytext=(4.9, 5.5),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("стойка Ø 0,8 м (4 шт.)", xy=(2.7, 2.9), xytext=(4.6, 2.3),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("ростверк 13,3 м", xy=(-4.9, 0.9), xytext=(-7.1, 0.3),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("зазор 0,6 м по верху плиты", xy=(-2.0, 6.26), xytext=(-6.9, 5.5),
             fontsize=8.5, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.text(-7.1, 8.05, "Разрез 1-1 (опора П-1)", fontsize=11, weight="bold")

# ================= ПЛАН =================
axP.set_xlim(-3.2, 81.5)
axP.set_ylim(-6.9, 6.9)
axP.set_aspect("equal")
axP.axis("off")

# настилка
for (x0, x1) in DECK_SPANS:
    axP.add_patch(Rectangle((x0, -6.0), x1 - x0, 12.0, facecolor="#f1ecdf", edgecolor=C_EDGE, lw=0.8))
# балки (6 шт.)
for (x0, x1) in BEAM_SPANS:
    for yc in BEAM_Y:
        axP.add_patch(Rectangle((x0, yc - 0.7), x1 - x0, 1.4, facecolor=C_FILL,
                                edgecolor=C_EDGE, lw=0.9))
# устои (стена + откос)
axP.add_patch(Rectangle((-1.4, -6.2), 1.4, 12.4, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))
axP.add_patch(Rectangle((0.0, -6.2), 1.6, 12.4, facecolor="#efe9da", edgecolor=C_EDGE, lw=0.8, hatch=".."))
axP.add_patch(Rectangle((78.0, -6.2), 1.4, 12.4, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))
axP.add_patch(Rectangle((76.4, -6.2), 1.6, 12.4, facecolor="#efe9da", edgecolor=C_EDGE, lw=0.8, hatch=".."))
# опоры: ригель (виден сверху) + стойки (спрятаны — пунктир)
for xc in PIER_X:
    axP.add_patch(Rectangle((xc - 0.85, -6.5), 1.7, 13.0, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))
    for yc in (-3.0, -1.0, 1.0, 3.0):
        axP.add_patch(Circle((xc, yc), 0.4, facecolor="none", edgecolor=C_EDGE,
                             lw=0.9, ls=(0, (3, 2))))

axP.annotate("балка 1,4 м (6 шт./пролёт, зазор 0,6 м)", xy=(9, -5.7), xytext=(1.5, -6.65),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axP.annotate("ригель 13,0 м + стойки Ø 0,8 (4 шт.)", xy=(14.5, 4.6), xytext=(10.5, 6.3),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axP.annotate("откос", xy=(0.9, 3.6), xytext=(3.0, 4.3),
             fontsize=8.5, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axP.annotate("настилка 12,0 м", xy=(48, 4.6), xytext=(45, 5.9),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axP.text(-3.0, 6.55, "Вид сверху", fontsize=11, weight="bold")

plt.savefig("drawing.png", facecolor="white")
print("drawing.png сохранён")
