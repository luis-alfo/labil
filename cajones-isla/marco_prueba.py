"""Marco de prueba de encaje para los huecos de la isla de la cocina.

Genera un "marco de puerta": un anillo rectangular de pared fina con un poco
de profundidad, cuyas medidas EXTERIORES son las que tendría el cuerpo del
cajón. Sirve para comprobar el encaje en el hueco gastando el mínimo plástico.

Uso:
    python3 marco_prueba.py                       # valores por defecto
    python3 marco_prueba.py --holgura 0.8         # más holgura por lado
    python3 marco_prueba.py --profundidad 15 --pared 2

Requiere: pip install manifold3d trimesh
"""

import argparse

import numpy as np
import trimesh
from manifold3d import CrossSection

PLA_DENSIDAD = 1.24  # g/cm³


def construir_marco(ancho_hueco, alto_hueco, holgura, pared, profundidad,
                    escuadra, chaflan_base):
    # Medidas exteriores = hueco menos la holgura en cada lado.
    ancho = ancho_hueco - 2 * holgura
    alto = alto_hueco - 2 * holgura

    # Interior con las esquinas cortadas a 45°: esas "escuadras" mantienen el
    # marco a 90° y lo rigidizan casi sin añadir material.
    ia, ib = ancho / 2 - pared, alto / 2 - pared
    e = escuadra
    interior = CrossSection([[
        (-ia + e, -ib), (ia - e, -ib), (ia, -ib + e), (ia, ib - e),
        (ia - e, ib), (-ia + e, ib), (-ia, ib - e), (-ia, -ib + e),
    ]])
    # Cuerpo exterior. La base lleva un chaflán a 45° en la arista exterior
    # para compensar la "pata de elefante" (la primera capa sale más ancha).
    c = chaflan_base
    cuerpo = CrossSection.square((ancho, alto), center=True) \
        .extrude(profundidad - c).translate((0, 0, c))
    if c > 0:
        base = CrossSection.square((ancho - 2 * c, alto - 2 * c), center=True)
        cuerpo += base.extrude(c, scale_top=((ancho) / (ancho - 2 * c),
                                             (alto) / (alto - 2 * c)))

    marco = cuerpo - interior.extrude(profundidad + 2).translate((0, 0, -1))
    return marco, ancho, alto


def a_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=mesh.vert_properties[:, :3],
                           faces=mesh.tri_verts)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ancho-hueco", type=float, default=130.0, help="mm")
    p.add_argument("--alto-hueco", type=float, default=135.0, help="mm")
    p.add_argument("--holgura", type=float, default=0.5,
                   help="holgura por lado en mm (0.5 → 1 mm en total)")
    p.add_argument("--pared", type=float, default=1.6,
                   help="grosor de pared en mm (1.6 = 4 líneas con boquilla 0.4)")
    p.add_argument("--profundidad", type=float, default=10.0, help="mm")
    p.add_argument("--escuadra", type=float, default=6.0,
                   help="cateto de las escuadras interiores en mm (0 = sin)")
    p.add_argument("--chaflan-base", type=float, default=0.4, help="mm")
    p.add_argument("--salida", default="marco_prueba_130x135.stl")
    a = p.parse_args()

    marco, ancho, alto = construir_marco(
        a.ancho_hueco, a.alto_hueco, a.holgura, a.pared, a.profundidad,
        a.escuadra, a.chaflan_base)

    malla = a_trimesh(marco)
    assert malla.is_watertight, "la malla no es cerrada"
    malla.export(a.salida)

    vol_cm3 = malla.volume / 1000
    print(f"STL: {a.salida}")
    print(f"Exterior: {ancho:.1f} x {alto:.1f} mm, profundidad {a.profundidad} mm")
    print(f"Hueco:    {a.ancho_hueco:.1f} x {a.alto_hueco:.1f} mm "
          f"(holgura {a.holgura} mm por lado)")
    print(f"Volumen: {vol_cm3:.2f} cm³ ≈ {vol_cm3 * PLA_DENSIDAD:.1f} g de PLA (macizo)")


if __name__ == "__main__":
    main()
