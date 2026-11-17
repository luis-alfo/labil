"""Cajón Gridfinity con frente de agujero de dedo: despiece y montado (sin cubos)."""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gridfinity import cuerpo, frente, box, tm, g, W, L, Y_SPLIT
from render import render

EUR_G = 0.02
body = cuerpo()
fr = frente("agujero")
t1 = body ^ box(-W, -1, -1, 2 * W, Y_SPLIT + 1, 200)
t2 = body ^ box(-W, Y_SPLIT, -1, 2 * W, L, 200)
COL = {"fr": np.array([0.95, 0.91, 0.82]), "t1": np.array([0.80, 0.86, 0.80]), "t2": np.array([0.80, 0.84, 0.92])}
eur = lambda x: f"{x:.2f}".replace(".", ",")
etiqueta = lambda n, m: f"{n}: {g(m):.0f} g · {eur(g(m) * EUR_G)} €"

def recorta(img, pad=12):
    ys, xs = np.where(img.min(axis=2) < 0.99)
    return img[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]

sep = 90
bounds = np.array([[-W / 2, -sep, 0], [W / 2, L + sep, 134], [-W / 2, L + sep, 0], [W / 2, -sep, 134]])
fig = plt.figure(figsize=(16, 6.4))
ax = fig.add_subplot(1, 2, 1)
ax.imshow(recorta(render([(tm(fr.translate((0, -sep, 0))), COL["fr"]), (tm(t1), COL["t1"]), (tm(t2.translate((0, sep, 0))), COL["t2"])],
                 az=-35, el=30, size=(780, 640), bounds=bounds)))
ax.set_axis_off()
ax.set_title("Piezas separadas\n" + "   ".join([etiqueta("Frente", fr), etiqueta("Tramo 1", t1), etiqueta("Tramo 2", t2)]), fontsize=12)
ax = fig.add_subplot(1, 2, 2)
ax.imshow(recorta(render([(tm(fr), COL["fr"]), (tm(t1), COL["t1"]), (tm(t2), COL["t2"])], az=-35, el=30, size=(780, 640), bounds=bounds)))
ax.set_axis_off()
tot = g(fr) + g(t1) + g(t2)
ax.set_title(f"Montado\nTotal ≈ {tot:.0f} g · {eur(tot * EUR_G)} € de PLA (20 €/kg)", fontsize=12)
fig.suptitle("Cajón Gridfinity 3 × 8 con frente de agujero de dedo — hueco 130 × 135 × 350 mm", fontsize=14, y=0.98)
plt.tight_layout(rect=(0, 0, 1, 0.93))
plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cajon_agujero.png"), dpi=100)
