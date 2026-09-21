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
BEAM_SPANS = [(-0.30, 14.70), (15.00, 39.00), (39.05, 63.05), (63.30, 78.30)]
DECK_SPANS = [(-0.45, 14.95), (15.05, 38.95), (39.10, 62.95), (63.35, 78.45)]
PIER_X     = (15.0, 39.0, 63.0)
BEAM_Y     = (-3.0, -1.5, 0.0, 1.5, 3.0)
BZ         = 5.0     # низ балки
BH         = 1.23    # высота балки
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

def beam_poly(yc, zoff=0.0):
    p = [(yc + y, zoff + z) for (y, z) in BEAM_R]
    p += [(yc - y, zoff + z) for (y, z) in reversed(BEAM_R)]
    return p

fig = plt.figure(figsize=(17.2, 10.2), dpi=150)
gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1.0], hspace=0.30, wspace=0.14,
                      left=0.05, right=0.985, top=0.90, bottom=0.06)
axE = fig.add_subplot(gs[0, :])   # вид спереди (разрез поперечный? нет — продольный)
axC = fig.add_subplot(gs[1, 0])   # разрез поперечный
axP = fig.add_subplot(gs[1, 1])   # план

fig.text(0.5, 0.965, "ПУТЕПРОВОД  15 + 24 + 24 + 15  м  ·  СЕРИЯ 3.503.1-81  ·  МАСШТАБ МОДЕЛИ 1:100",
         ha="center", va="center", fontsize=15, weight="bold", color=C_TEXT)
fig.text(0.5, 0.933,
         "Балки двутавровые Б2400.140.123 / Б1500.140.123 (b = 1.40 м, h = 1.23 м + обу́вь 0.10 м, "
         "стыки — выпуклостями) · 5 балок на пролёт · опоры — круглые стойки Ø 1.0 м, ригель и ростверк · "
         "настилка (участки омоноличивания) 0.35 м",
         ha="center", va="center", fontsize=9.5, color="#6a6254")

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

# опоры
for xc in PIER_X:
    axE.add_patch(Rectangle((xc - 0.5, 0), 1.0, 0.6, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))
    axE.add_patch(Rectangle((xc - 0.5, 0.6), 1.0, 3.5, facecolor=C_FILL, edgecolor=C_EDGE, lw=1.0))
    axE.add_patch(Rectangle((xc - 0.5, 4.1), 1.0, 0.9, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))

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
axC.set_xlim(-5.6, 5.6)
axC.set_ylim(-1.1, 8.4)
axC.set_aspect("equal")
axC.axis("off")

axC.plot([-5.3, 5.3], [0, 0], color=C_GROUND, lw=1.6)
for x in range(-5, 6, 2):
    axC.plot([x, x - 0.5], [0, -0.55], color=C_GROUND, lw=0.5)

# ригель, стойки (в разрезе — прямоугольники), ростверк
axC.add_patch(Rectangle((-1.1, 0), 2.2, 0.6, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.1))
for yc in (-0.8, 0.8):
    axC.add_patch(Rectangle((yc - 0.5, 0.6), 1.0, 3.5, facecolor=C_FILL, edgecolor=C_EDGE, lw=1.1))
axC.add_patch(Rectangle((-1.2, 4.1), 2.4, 0.9, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.1))

# балки (5 шт.)
for yc in BEAM_Y:
    axC.add_patch(Rectangle((yc - SHOE_W, BZ), 2 * SHOE_W, SHOE_H,
                            facecolor="#ddd5c0", edgecolor=C_EDGE, lw=1.0))
    axC.add_patch(Polygon(beam_poly(yc, BZ), closed=True, facecolor=C_FILL, edgecolor=C_EDGE, lw=1.1))

# настилка
axC.add_patch(Rectangle((-4.0, DZ), 8.0, DT, facecolor=C_DECK, edgecolor=C_EDGE,
                        lw=0.9, hatch="///", alpha=0.95))

# подписи
axC.annotate("настилка (участок\nомоноличивания)", xy=(2.6, DZ + 0.1), xytext=(3.1, 7.3),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("балка Б.140.123", xy=(0.7, 6.6), xytext=(1.9, 6.9),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("ростверк", xy=(0.55, 4.55), xytext=(2.1, 4.6),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("стойка Ø 1,0 м", xy=(0.8, 2.0), xytext=(2.4, 1.2),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("ригель", xy=(0.0, 0.3), xytext=(2.3, 0.1),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.annotate("зазор 0,1 м\n(настилка монолитная)", xy=(-2.25, 6.35), xytext=(-5.2, 3.2),
             fontsize=8.5, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axC.text(-5.3, 7.9, "Разрез 1-1 (опора П-1)", fontsize=11, weight="bold")

# ================= ПЛАН =================
axP.set_xlim(-3.2, 81.5)
axP.set_ylim(-5.6, 5.6)
axP.set_aspect("equal")
axP.axis("off")

# настилка
for (x0, x1) in DECK_SPANS:
    axP.add_patch(Rectangle((x0, -4.0), x1 - x0, 8.0, facecolor="#f1ecdf", edgecolor=C_EDGE, lw=0.8))
# балки
for (x0, x1) in BEAM_SPANS:
    for yc in BEAM_Y:
        axP.add_patch(Rectangle((x0, yc - 0.7), x1 - x0, 1.4, facecolor=C_FILL,
                                edgecolor=C_EDGE, lw=0.9))
# устои (стена + откос)
axP.add_patch(Rectangle((-1.4, -4.2), 1.4, 8.4, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))
axP.add_patch(Rectangle((0.0, -4.2), 1.6, 8.4, facecolor="#efe9da", edgecolor=C_EDGE, lw=0.8, hatch=".."))
axP.add_patch(Rectangle((78.0, -4.2), 1.4, 8.4, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))
axP.add_patch(Rectangle((76.4, -4.2), 1.6, 8.4, facecolor="#efe9da", edgecolor=C_EDGE, lw=0.8, hatch=".."))
# опоры: ростверк + стойки (спрятаны — пунктир)
for xc in PIER_X:
    axP.add_patch(Rectangle((xc - 0.5, -1.2), 1.0, 2.4, facecolor=C_FILL2, edgecolor=C_EDGE, lw=1.0))
    for yc in (-0.8, 0.8):
        axP.add_patch(Circle((xc, yc), 0.5, facecolor="none", edgecolor=C_EDGE,
                             lw=0.9, ls=(0, (3, 2))))

axP.annotate("балка 1,4 м (5 шт./пролёт)", xy=(8, -0.7), xytext=(3.0, -4.9),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axP.annotate("ростверк + стойки Ø1,0", xy=(14.6, 1.25), xytext=(8.5, 4.95),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axP.annotate("откос", xy=(0.9, 2.6), xytext=(3.0, 2.9),
             fontsize=8.5, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axP.annotate("настилка 8,0 м", xy=(48, 3.4), xytext=(45, 4.75),
             fontsize=9, color=C_TEXT, arrowprops=dict(arrowstyle="->", lw=0.9))
axP.text(-3.0, 5.25, "Вид сверху", fontsize=11, weight="bold")

plt.savefig("drawing.png", facecolor="white")
print("drawing.png сохранён")
