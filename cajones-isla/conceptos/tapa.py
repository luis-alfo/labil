"""Tapa autónoma para los huecos de la isla (sin cajón).

Es la puerta de 3 voltes (revoltons3, con línea de sombra) más un faldón de
12 mm por detrás que entra en el hueco. Sirve para dos cosas:
  1. probar la puerta antes de imprimir el cajón entero;
  2. tapar los huecos de abajo que no llevarán cajón.

Sujeción: el faldón tiene la holgura normal (0,5 mm por lado) y 6 costillas
aplastables en los costados que sobresalen un poco más (0,3 mm de apriete).
Si aprieta demasiado, se rebajan con un cúter; si queda floja, se sube
COSTILLA en este archivo.

Variantes:
  - "pasante": la abertura atraviesa; los dedos se enganchan por detrás del frente.
  - "bolsillo": detrás de la abertura hay una cajita cerrada que sube 8 mm por
    encima del arco, así la yema engancha y no se ve el interior.
"""
import os, sys
import trimesh
from manifold3d import CrossSection, Manifold, OpType

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from cajon import W, H, TF, rrect, box, vertical, corte, arcos, ESTILOS, gramos

FALDON = 12.0          # lo que entra en el hueco, por detrás del frente
PARED = 1.6
COSTILLA = 0.8         # lo que sobresale cada costilla (holgura 0,5 → aprieta 0,3)
COSTILLAS_Z = (25.0, 67.0, 109.0)
RADIO, CHAFLAN = 2.0, 1.0


def abertura():
    tipo, aw, ah, zc, n = ESTILOS["revoltons3"]["abertura"]
    return arcos(aw, ah, zc - ah / 2, n), (aw, ah, zc, n)


def costilla(x_lado):
    """Costilla vertical en el costado (x_lado = ±1), con rampa de entrada atrás."""
    y0, y1 = TF + 1.0, TF + FALDON
    x = W / 2
    pts = [(x - 0.01, y0), (x + COSTILLA, y0 + 0.8), (x + COSTILLA, y1 - 3.0), (x - 0.01, y1)]
    if x_lado < 0:
        pts = [(-px, py) for px, py in reversed(pts)]
    return CrossSection([pts]).extrude(1.6)


def tapa(variante="pasante"):
    # un único bloque (frente + faldón) vaciado por detrás: sin caras coincidentes entre piezas
    perfil = rrect(W, H, RADIO).translate((0, H / 2))
    t = vertical(perfil, TF + FALDON, CHAFLAN)
    hueco_int = rrect(W - 2 * PARED, H - 2 * PARED, 0.5).translate((0, H / 2))
    t -= vertical(hueco_int, FALDON + 1, 0.0, y=TF)
    hueco, (aw, ah, zc, n) = abertura()
    t -= corte(hueco, TF, CHAFLAN)

    for lado in (-1, 1):
        for z in COSTILLAS_Z:
            t += costilla(lado).translate((0, 0, z - 0.8))

    if variante == "bolsillo":
        fondo = 8.8                                         # hueco libre detrás del frente
        cav = arcos(aw, ah + 8, zc - ah / 2, n)             # mismo arco, 8 mm más alto
        caja = vertical(cav.offset(1.2, circular_segments=16), fondo + 1.7, 0.0, y=TF - 0.5)
        # la caja solapa 0,5 mm con el frente; el vaciado arranca a la misma profundidad
        # (por encima del arco el frente queda de 1,5 mm, por dentro y sin que se vea)
        t = t + caja - vertical(cav, fondo + 0.5, 0.0, y=TF - 0.5)
    return t


def exportar():
    out = os.path.join(AQUI, "..", "stl")
    os.makedirs(out, exist_ok=True)
    res = {}
    for v in ("pasante", "bolsillo"):
        m = tapa(v)
        imp = m.rotate((90, 0, 0))                          # boca abajo: la cara vista sobre la cama
        bb = imp.bounding_box()
        imp = imp.translate((-bb[0], -bb[1], -bb[2]))
        me = imp.to_mesh()
        t = trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)
        t.export(os.path.join(out, f"tapa_revoltons3_{v}.stl"))
        res[v] = (gramos(m), t.is_watertight, t.bounds[1] - t.bounds[0])
    return res


if __name__ == "__main__":
    for v, (g, ok, ext) in exportar().items():
        print(v, f"{g:.1f} g", ok, ext.round(2))
