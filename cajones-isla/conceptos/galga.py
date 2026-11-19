"""Galga escalonada para medir el hueco de verdad (ancho y alto) con 0,5 mm de precisión.

Por qué existe: todo el proyecto partía de «13 × 13,5 cm» medido con flexómetro.
Esa medida falló (la tapa de costillas se caía). Esta pieza la sustituye por un dato.

Es una chapa con escalones: cada escalón mide 0,5 mm más de ancho que el anterior.
Se mete por la punta estrecha, plana y recta, hasta que no entra más. El último
número que ha entrado es la medida del hueco (si entró también el escalón sin
número que le sigue, se suman 0,5 mm). De lado mide el ancho; de pie, el alto.

Uso:  python3 galga.py            # 128 a 140 mm
      python3 galga.py --desde 126 --hasta 134
"""
import argparse
import os

import trimesh
from manifold3d import CrossSection, JoinType, Manifold, OpType

AQUI = os.path.dirname(os.path.abspath(__file__))

PASO = 0.5           # mm de ancho por escalón
LARGO_PASO = 5.0     # mm de fondo de cada escalón
GROSOR = 1.6
BANDA = 4.5          # ancho del marco
ESPINA = 11.0        # barra central, donde van los números
PUNTA = 6.0          # entrada en cuña
RELIEVE = 0.4        # altura de los números
PIE_ELEFANTE = 0.3   # las 2 primeras capas van metidas, para que no falseen la medida

# dígitos de 7 segmentos: a arriba, b/c derecha, d abajo, e/f izquierda, g centro
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc",
       "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg"}
DIG_W, DIG_H, TRAZO, DIG_SEP = 2.4, 4.0, 0.6, 0.9


def digito(c):
    w, h, t = DIG_W, DIG_H, TRAZO
    r = lambda x, y, sx, sy: CrossSection.square((sx, sy)).translate((x, y))  # noqa: E731
    seg = {"a": r(0, h - t, w, t), "d": r(0, 0, w, t), "g": r(0, h / 2 - t / 2, w, t),
           "f": r(0, h / 2, t, h / 2), "b": r(w - t, h / 2, t, h / 2),
           "e": r(0, 0, t, h / 2), "c": r(w - t, 0, t, h / 2)}
    return CrossSection.batch_boolean([seg[s] for s in SEG[c]], OpType.Add)


def numero(texto):
    """Texto centrado en el origen, girado 180°: se lee con la punta estrecha hacia el hueco."""
    ancho = len(texto) * DIG_W + (len(texto) - 1) * DIG_SEP
    cs = CrossSection.batch_boolean(
        [digito(c).translate((i * (DIG_W + DIG_SEP) - ancho / 2, -DIG_H / 2)) for i, c in enumerate(texto)],
        OpType.Add)
    return cs.rotate(180)


def perfil(desde=128.0, hasta=140.0):
    """Devuelve el marco y los números como perfiles 2D, y la lista de anchos."""
    n = int(round((hasta - desde) / PASO)) + 1
    anchos = [desde + i * PASO for i in range(n)]
    largo = n * LARGO_PASO
    # contorno: punta en cuña (y < 0) y escalones (y ≥ 0); la punta apunta a −y
    der = [(anchos[0] / 2 - 3.0, -PUNTA), (anchos[0] / 2, 0.0)]
    for i, w in enumerate(anchos):
        der += [(w / 2, i * LARGO_PASO), (w / 2, (i + 1) * LARGO_PASO)]
    izq = [(-x, y) for x, y in reversed(der)]
    contorno = CrossSection([der + izq])

    hueco = contorno.offset(-BANDA, JoinType.Miter)
    hueco -= CrossSection.square((ESPINA, largo + PUNTA + 2)).translate((-ESPINA / 2, -PUNTA - 1))
    for y in (largo * 0.33, largo * 0.66):                       # dos travesaños para que no se deforme
        hueco -= CrossSection.square((hasta + 2, 3.0)).translate((-hasta / 2 - 1, y - 1.5))
    marco = contorno - hueco
    marcas = []
    for i, w in enumerate(anchos):
        if abs(w - round(w)) < 1e-6:
            marcas.append(numero(str(int(round(w)))).translate((0, (i + 0.5) * LARGO_PASO)))
    return marco, CrossSection.batch_boolean(marcas, OpType.Add), anchos


def galga(desde=128.0, hasta=140.0):
    marco, marcas, anchos = perfil(desde, hasta)
    m = marco.offset(-PIE_ELEFANTE, JoinType.Miter).extrude(0.4)
    m += marco.extrude(GROSOR - 0.3).translate((0, 0, 0.3))
    m += marcas.extrude(RELIEVE + 0.2).translate((0, 0, GROSOR - 0.2))
    return m, anchos


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--desde", type=float, default=128.0)
    p.add_argument("--hasta", type=float, default=140.0)
    a = p.parse_args()
    m, anchos = galga(a.desde, a.hasta)
    bb = m.bounding_box()
    me = m.translate((-bb[0], -bb[1], -bb[2])).to_mesh()
    t = trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts)
    assert t.is_watertight, "la malla no es cerrada"
    out = os.path.join(AQUI, "..", "stl", f"galga_hueco_{a.desde:g}-{a.hasta:g}.stl")
    t.export(out)
    e = t.bounds[1] - t.bounds[0]
    print(f"{os.path.basename(out)}: {len(anchos)} escalones de {anchos[0]:g} a {anchos[-1]:g} mm · "
          f"{e[0]:.1f} × {e[1]:.1f} × {e[2]:.1f} mm · {m.volume() / 1000 * 1.24:.1f} g macizo")


if __name__ == "__main__":
    main()
