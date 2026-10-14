"""Imagen de las tapas autónomas (pasante y bolsillo): frente, trasera y corte."""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import tapa as T
from cajon import box, gramos
from render import render
from img_uniones import tm, recorta, limpio

C = np.array([0.95, 0.91, 0.82])
EUR = lambda g: f"{g * 0.02:.2f}".replace(".", ",")
fig, axes = plt.subplots(2, 3, figsize=(17, 11))
for fila, v in enumerate(("pasante", "bolsillo")):
    m = T.tapa(v)
    g = gramos(m)
    axes[fila, 0].imshow(recorta(render([(tm(m), C)], az=-22, el=12, size=(460, 460))))
    axes[fila, 0].set_title(f"Tapa {v} · ≈ {g:.0f} g · {EUR(g)} €\nvista de frente", fontsize=12)
    axes[fila, 1].imshow(recorta(render([(tm(m), C)], az=155, el=25, size=(460, 460))))
    axes[fila, 1].set_title("por detrás: faldón de 12 mm y 6 costillas de apriete", fontsize=12)
    corte = m ^ box(-1, -1, 60, 2, 30, 74)               # rebanada central alrededor de la abertura
    axes[fila, 2].imshow(recorta(render([(tm(corte), C)], az=90, el=0, size=(460, 460))))
    axes[fila, 2].set_title("perfil cortado por el centro (frente a la derecha)\n" + ("el bolsillo sube 8 mm sobre el arco: la yema engancha" if v == "bolsillo" else "abertura pasante: los dedos enganchan por detrás"), fontsize=12)
    for a in axes[fila]: limpio(a)
fig.suptitle("Tapa autónoma de 3 voltes (129 × 134 mm, faldón de 12 mm): prueba de puerta y tapa para los huecos sin cajón", fontsize=14, y=0.99)
plt.tight_layout(rect=(0, 0, 1, 0.95))
plt.savefig(os.path.join(AQUI, "..", "tapas.png"), dpi=90)
