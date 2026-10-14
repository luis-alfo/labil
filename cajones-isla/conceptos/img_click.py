"""Imagen del cajón con base Clickfinity real: despiece y montado. Uso: python3 img_click.py <zip clickfinity>"""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import cajon_click as K
from cajon import llave, box
from render import render
from img_uniones import tm, recorta, limpio

C_FR, C_TA, C_TB = np.array([0.95, 0.91, 0.82]), np.array([0.80, 0.86, 0.80]), np.array([0.80, 0.84, 0.92])
C_PL, C_CO, C_K = np.array([0.93, 0.62, 0.36]), np.array([0.35, 0.60, 0.90]), np.array([0.86, 0.45, 0.35])
EUR = lambda g: f"{g * 0.02:.2f}".replace(".", ",")

fr, ta, tb = K.frente_click(), K.tramo_a(), K.tramo_b()
kit = K.kit_clickfinity(sys.argv[1])
llaves = [llave().translate((x, y, 0)) for x in K.C.RAIL_X for y in (K.C.FL_D, K.Y_SPLIT)]

g_pla = K.gramos(fr) + K.gramos(ta) + K.gramos(tb) + sum(K.gramos(k) for k in llaves)
g_petg = sum(K.gramos_petg(m) for m in kit.values())

fig = plt.figure(figsize=(18, 10.5))
gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1])
ax = fig.add_subplot(gs[0, :])
sep, alto = 60, 45
partes = [(tm(fr.translate((0, -sep, 0))), C_FR), (tm(ta), C_TA), (tm(tb.translate((0, sep, 0))), C_TB)]
partes += [(tm(k.translate((0, (sep if k.bounding_box()[1] > 100 else 0) - (sep / 2 if k.bounding_box()[1] < 100 else 0), -20))), C_K) for k in llaves]
for n, m in kit.items():
    dy = sep if m.bounding_box()[1] > 200 else (sep / 2 if n.startswith("conector") else 0)
    partes.append((tm(m.translate((0, dy, alto))), C_CO if n.startswith("conector") else C_PL))
ax.imshow(recorta(render(partes, az=-38, el=30, size=(1400, 620)))); limpio(ax)
ax.set_title("Despiece: frente (revoltons de 3 voltes) · tramo A · tramo B · 4 llaves (rojo) · "
             "placas Clickfinity 3x4 + 3x3 recortadas (naranja) · 4 conectores (azul)", fontsize=12)

ax = fig.add_subplot(gs[1, 0])
partes = [(tm(fr), C_FR), (tm(ta), C_TA), (tm(tb), C_TB)] + [(tm(m), C_CO if n.startswith("conector") else C_PL) for n, m in kit.items()]
ax.imshow(recorta(render(partes, az=-35, el=32, size=(800, 560)))); limpio(ax)
ax.set_title(f"Montado · bandeja + frente en PLA ≈ {g_pla:.0f} g ({EUR(g_pla)} €) · "
             f"Clickfinity en PETG ≈ {g_petg:.0f} g ({EUR(g_petg)} €)", fontsize=12)

ax = fig.add_subplot(gs[1, 1])
zoom = [(tm(fr), C_FR)]
ax.imshow(recorta(render(zoom, az=-20, el=10, size=(560, 560)))); limpio(ax)
ax.set_title("Frente: 3 voltes sin vigas, línea de sombra (radio 2 + chaflán 1 mm)", fontsize=12)
fig.suptitle("Cajón de la isla con base Clickfinity real — Clickfinity © NoWarrenty / jerrymk, CC BY-NC-SA 4.0", fontsize=14, y=0.99)
plt.tight_layout(rect=(0, 0, 1, 0.96))
plt.savefig(os.path.join(AQUI, "..", "cajon_clickfinity.png"), dpi=90)
