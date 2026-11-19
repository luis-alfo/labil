import os
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gridfinity import frente, tm, g, box, cuerpo, W, H
from render import render

CREMA = np.array([0.95, 0.91, 0.82])
tipos = [("muesca", "1 · Muesca", "semicírculo arriba;\nel más simple"),
         ("gola", "2 · Gola", "ranura a todo lo ancho,\ncomo los muebles de tu cocina"),
         ("agujero", "3 · Agujero de dedo", "óvalo a media altura;\ntira cerca del reborde"),
         ("ranura", "4 · Ranura", "línea horizontal fina;\nmínimo visual"),
         ("calado", "5 · Calado", "panal: ves lo que hay\ny gasta menos")]
stub = cuerpo() ^ box(-W, -1, -1, 2 * W, 60, 200)  # arranque del tramo para dar contexto
bounds = np.array([[-W/2, 0, 0], [W/2, 60, H], [-W/2, 60, 0], [W/2, 0, H]])
fig, axes = plt.subplots(2, 5, figsize=(17, 8.6))
for i, (k, nombre, desc) in enumerate(tipos):
    f = frente(k)
    fondo = box(-W, 10, -1, 2 * W, 100, 200)       # lo retranqueado (gola) se pinta más oscuro
    partes = [(tm(f - fondo), CREMA)] + ([(tm(f ^ fondo), CREMA * 0.72)] if not (f ^ fondo).is_empty() else [])
    axes[0, i].imshow(render(partes, az=0, el=0, size=(330, 340), bounds=bounds[[0, 3]] * [1, 0, 1] + 0))
    axes[0, i].set_title(f"{nombre}\n≈ {g(f):.0f} g", fontsize=13)
    axes[1, i].imshow(render(partes + [(tm(stub), np.array([0.88, 0.84, 0.74]))], az=-32, el=24, size=(330, 340), bounds=bounds))
    axes[1, i].set_xlabel(desc, fontsize=11)
    for ax in axes[:, i]:
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_visible(False)
fig.suptitle("Propuestas de frente enrasado (129 × 134 mm, 2 mm + nervios traseros)", fontsize=14, y=0.98)
plt.tight_layout(rect=(0, 0, 1, 0.94))
plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "propuestas_frente.png"), dpi=100)
