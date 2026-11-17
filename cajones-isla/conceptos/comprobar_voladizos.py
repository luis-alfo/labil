"""Comprueba, capa a capa, qué partes de un STL se imprimen en el aire (boca abajo, sin soportes).

Para cada capa de 0,2 mm calcula la zona que no tiene nada debajo a menos de MARGEN mm
(una pared a 45° avanza 0,2 mm por capa, así que con 0,35 pasa). Lo que queda son
puentes o voladizos de verdad; los lista con su altura, área y tamaño.

Uso: python3 comprobar_voladizos.py pieza.stl [...]
"""
import sys
import numpy as np
import trimesh
from manifold3d import JoinType, Manifold, Mesh

CAPA, MARGEN = 0.2, 0.35


def analiza(ruta):
    t = trimesh.load(ruta)
    m = Manifold(Mesh(vert_properties=np.array(t.vertices, dtype=np.float32),
                      tri_verts=np.array(t.faces, dtype=np.uint32)))
    zmax = t.bounds[1][2]
    previa, hallazgos = None, []
    for k in range(int(round(zmax / CAPA))):
        actual = m.slice((k + 0.5) * CAPA)
        if previa is not None and not actual.is_empty():
            aire = actual - previa.offset(MARGEN, JoinType.Round, circular_segments=16)
            for g in aire.decompose():
                if g.area() > 0.3:
                    x0, y0, x1, y1 = g.bounds()
                    hallazgos.append((round(k * CAPA, 1), g.area(), x1 - x0, y1 - y0))
        previa = actual
    return hallazgos


if __name__ == "__main__":
    for ruta in sys.argv[1:]:
        h = analiza(ruta)
        print(f"\n{ruta}: {len(h)} zonas en el aire")
        por_z = {}
        for z, a, dx, dy in h:
            por_z.setdefault(z, []).append((a, dx, dy))
        for z in sorted(por_z):
            zs = por_z[z]
            print(f"  a {z:4.1f} mm: {len(zs):2d} zonas · mayor {max(a for a, *_ in zs):6.1f} mm² "
                  f"({max(zs)[1]:.1f} × {max(zs)[2]:.1f} mm)")
