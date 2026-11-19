"""Imágenes de la tapa con lengüetas y de la galga."""
import os, sys, numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import tapa_lenguetas as T
import galga as G
from cajon import box
from render import render


def tm(m):
    me = m.to_mesh()
    return trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)


def recorta(img, pad=10):
    ys, xs = np.where(img.min(axis=2) < 0.99)
    return img[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]


def limpio(ax):
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)


C = np.array([0.95, 0.91, 0.82])
pas, aro, bol = T.tapa("pasante"), T.tapa("aro"), T.tapa("bolsillo")
g = lambda m: m.volume() / 1000 * T.PLA

fig, axes = plt.subplots(2, 3, figsize=(18, 12.5))
a = axes[0, 0]
a.imshow(recorta(render([(tm(pas), C)], az=-20, el=12, size=(520, 520))))
a.set_title("Tapa pasante, de frente\nlos topes asoman 4 mm por cada lado y se esconden al entrar", fontsize=12)
a = axes[0, 1]
a.imshow(recorta(render([(tm(pas), C)], az=160, el=22, size=(520, 520))))
a.set_title("Por detrás: faldón metido 7,6 mm, 2 pies y\n2 lengüetas por lado que salen de un taco central", fontsize=12)
a = axes[0, 2]
zona = (pas ^ box(40, -1, 8, 40, 20, 62)).rotate((90, 0, 0))       # como se imprime: la cara vista abajo
a.imshow(recorta(render([(tm(zona), C)], az=-62, el=24, size=(600, 520))))
a.set_title("Detalle de una lengüeta, tal como se imprime (cara vista abajo):\nlámina de 2 mm en puente sobre 3 apoyos, y tope con rampas", fontsize=12)
a = axes[1, 0]
a.imshow(recorta(render([(tm(aro), C)], az=160, el=22, size=(520, 520))))
a.set_title(f"Aro de prueba: las mismas lengüetas sin el frente\n≈ {g(aro):.0f} g en vez de {g(pas):.0f} g", fontsize=12)
a = axes[1, 1]
a.imshow(recorta(render([(tm(bol), C)], az=160, el=22, size=(520, 520))))
a.set_title("Tapa con bolsillo, por detrás\n(no se ve el interior del hueco)", fontsize=12)
a = axes[1, 2]
marco, marcas, anchos = G.perfil()
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
for cs, color in ((marco, "#e3c896"), (marcas, "#3a3226")):
    vs, cod = [], []
    for pol in cs.to_polygons():                      # los agujeros vienen con el giro contrario
        vs += list(pol) + [pol[0]]
        cod += [MPath.MOVETO] + [MPath.LINETO] * (len(pol) - 1) + [MPath.CLOSEPOLY]
    a.add_patch(PathPatch(MPath(vs, cod), facecolor=color, lw=0))
a.set_aspect("equal"); a.set_xlim(73, -73); a.set_ylim(128, -9)      # girada 180°: la punta estrecha, arriba
a.set_title("Galga escalonada de 128 a 140 mm, vista desde arriba (punta arriba).\n"
            "Cada escalón es 0,5 mm más ancho; se lee el último número que entra", fontsize=12)
for ax in axes.flat: limpio(ax)
fig.suptitle("Tapa de 3 voltes con lengüetas flexibles (sustituye a la de costillas, que se caía) y galga para medir el hueco", fontsize=14, y=0.99)
plt.tight_layout(rect=(0, 0, 1, 0.96))
plt.savefig(os.path.join(AQUI, "..", "tapa_lenguetas.png"), dpi=85)
