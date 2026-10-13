"""Imágenes: uniones del cajón y propuestas estéticas de la puerta."""
import os, sys, numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from cajon import *
from render import render

EUR = lambda gr: f"{gr * 0.02:.2f}".replace(".", ",")
C_FR, C_T1, C_T2 = np.array([0.95, 0.91, 0.82]), np.array([0.80, 0.86, 0.80]), np.array([0.80, 0.84, 0.92])


def tm(m):
    me = m.to_mesh()
    return trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)


def recorta(img, pad=10):
    ys, xs = np.where(img.min(axis=2) < 0.99)
    return img[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]


def limpio(ax):
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)


fr, t1, t2 = frente("volta"), tramo1(), tramo2()

# ---------- uniones ----------
fig = plt.figure(figsize=(17, 11))
gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1])
ax = fig.add_subplot(gs[0, :2])
img = render([(tm(fr.translate((0, -45, 0))), C_FR), (tm(t1), C_T1), (tm(t2.translate((0, 45, 40))), C_T2)],
             az=-40, el=-28, size=(1000, 560))
ax.imshow(recorta(img)); limpio(ax)
ax.set_title("Despiece visto desde abajo: patines y colas de milano.\n"
             "Se monta bajando cada pieza sobre la lengüeta de la anterior (frente → tramo 1 → tramo 2)", fontsize=12)
ax = fig.add_subplot(gs[0, 2])
img = render([(tm(fr), C_FR), (tm(t1), C_T1), (tm(t2), C_T2)], az=-40, el=-28, size=(520, 560))
ax.imshow(recorta(img)); limpio(ax)
tot = gramos(fr) + gramos(t1) + gramos(t2)
ax.set_title(f"Montado (desde abajo)\n≈ {tot:.0f} g · {EUR(tot)} €", fontsize=12)

ax = fig.add_subplot(gs[1, 0])
b = np.array([[-45, Y_SPLIT - 25, -2], [45, Y_SPLIT + 25, 12]])
corte_t1 = t1 ^ box(-60, Y_SPLIT - 30, -1, 120, 60, 40)
corte_t2 = (t2 ^ box(-60, Y_SPLIT - 30, -1, 120, 60, 40)).translate((0, 0, 14))
img = render([(tm(corte_t1), C_T1), (tm(corte_t2), C_T2)], az=-30, el=-35, size=(540, 420))
ax.imshow(recorta(img)); limpio(ax)
ax.set_title("Detalle junta tramo 1 / tramo 2\n(tramo 2 levantado: el hueco está abierto por abajo)", fontsize=11)

ax = fig.add_subplot(gs[1, 1])
corte_fr = fr ^ box(-60, -1, -1, 120, 30, 30)
corte_t1b = (t1 ^ box(-60, 0, -1, 120, 40, 40)).translate((0, 0, 14))
img = render([(tm(corte_fr), C_FR), (tm(corte_t1b), C_T1)], az=-30, el=-35, size=(540, 420))
ax.imshow(recorta(img)); limpio(ax)
ax.set_title("Detalle junta frente / tramo 1\n(pestaña inferior del frente con dos lengüetas)", fontsize=11)

ax = fig.add_subplot(gs[1, 2])
p = prueba_union()
img = render([(tm(p), np.array([0.93, 0.80, 0.62]))], az=-25, el=40, size=(540, 420))
ax.imshow(recorta(img)); limpio(ax)
ax.set_title(f"Probeta de tolerancias: juego 0,1 / 0,2 / 0,3 mm\n(1, 2 o 3 muescas) ≈ {gramos(p):.0f} g · {EUR(gramos(p))} €", fontsize=11)
fig.suptitle("Uniones: «cola de milano a caída» sobre dos patines", fontsize=15, y=0.99)
plt.tight_layout(rect=(0, 0, 1, 0.96))
plt.savefig(os.path.join(AQUI, "..", "uniones.png"), dpi=95)
plt.close()

# ---------- estética de la puerta ----------
nombres = {"actual": "Actual\naristas vivas", "sombra": "Línea de sombra\nradio 2 + chaflán 1 mm",
           "pildora": "Píldora fina\nmás discreta", "bolsillo": "Bolsillo\nno se ve el interior",
           "onda": "Onda superior\nsin agujero", "circulo": "Círculo\nmínimo",
           "volta": "Volta catalana\narco rebajado", "revoltons": "Revoltons\ntres voltes entre vigas"}
fig, axes = plt.subplots(2, 4, figsize=(17, 10.5))
for ax, k in zip(axes.flat, nombres):
    f = frente(k)
    img = render([(tm(f), C_FR)], az=-22, el=12, size=(400, 420))
    ax.imshow(recorta(img)); limpio(ax)
    ax.set_title(f"{nombres[k]}\n≈ {gramos(f):.0f} g · {EUR(gramos(f))} €", fontsize=12)
fig.suptitle("Propuestas estéticas de la puerta (frente enrasado de 129 × 134 mm)", fontsize=15, y=0.99)
plt.tight_layout(rect=(0, 0, 1, 0.95))
plt.savefig(os.path.join(AQUI, "..", "puertas_estetica.png"), dpi=95)
