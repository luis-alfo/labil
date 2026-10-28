"""Botonera fidget NocodeHackers: 4 pulsadores flexibles print-in-place.

Genera botonera_nch.stl y botonera_nch.3mf. Sin muelles ni piezas extra:
cada botón va sobre una lengüeta de PLA recortada en la tapa, que flexa.
Uso: python3 generar.py
"""
import math
import numpy as np
import trimesh
from manifold3d import CrossSection, JoinType, Manifold

# --- Parámetros (mm) ---
CELDA = 24.0        # paso entre botones
PARED = 2.0         # pared exterior y tabiques
SUELO = 1.6
ALTO_CAJA = 9.0     # altura total de la caja
TAPA = 1.2          # grosor tapa / lengüeta (más fino = más blando)
RANURA = 0.8        # hueco alrededor de la lengüeta (holgura print-in-place)
LENGUA = 19.0       # lado de la lengüeta
FORMA = 16.0        # tamaño de cada forma del logo
ALTO_FORMA = 3.0    # relieve del botón
RADIO = 2.5         # redondeo de las esquinas de las formas
LADO = 2 * CELDA + PARED


def poligono(pts):
    return CrossSection([pts])


def casa(s):  # arriba-izq: pentágono tipo "casa"
    h = s / 2
    return poligono([(-h, -h), (h, -h), (h, h * 0.15), (0, h), (-h, h * 0.15)]).offset(
        -RADIO, JoinType.Round).offset(RADIO, JoinType.Round)


def circulo(s):
    return CrossSection.circle(s / 2, 96)


def cuadrado_cortado(s):  # abajo-der: cuadrado con esquina inf-izq achaflanada
    h = s / 2
    return poligono([(-h * 0.1, -h), (h, -h), (h, h), (-h, h), (-h, -h * 0.1)]).offset(
        -RADIO, JoinType.Round).offset(RADIO, JoinType.Round)


# (forma, centro, lado de la bisagra)
BOTONES = [
    (casa, (-CELDA / 2, CELDA / 2), "izq"),
    (circulo, (CELDA / 2, CELDA / 2), "arriba"),
    (circulo, (-CELDA / 2, -CELDA / 2), "abajo"),
    (cuadrado_cortado, (CELDA / 2, -CELDA / 2), "der"),
]


def ranura_u(cx, cy, bisagra):
    """Recorte en U alrededor de la lengüeta; el lado `bisagra` queda unido."""
    a, r = LENGUA / 2, RANURA
    exterior = CrossSection.square([LENGUA + 2 * r] * 2, center=True)
    interior = CrossSection.square([LENGUA] * 2, center=True)
    # alargamos el interior por el lado de la bisagra para no cortarlo
    dx, dy = {"izq": (-1, 0), "der": (1, 0), "arriba": (0, 1), "abajo": (0, -1)}[bisagra]
    interior = interior + interior.translate([dx * 2 * r, dy * 2 * r])
    return (exterior - interior).translate([cx, cy])


def construir():
    h = LADO / 2
    caja = Manifold.cube([LADO, LADO, ALTO_CAJA], center=False).translate([-h, -h, 0])
    # cavidades: 4 huecos separados por tabiques (puentes cortos, imprimibles)
    for _, (cx, cy), _ in BOTONES:
        c = CELDA - PARED
        hueco = Manifold.cube([c, c, ALTO_CAJA - SUELO - TAPA]).translate(
            [cx - c / 2, cy - c / 2, SUELO])
        caja -= hueco
    # bordes redondeados en planta
    redondeo = CrossSection.square([LADO - 6, LADO - 6], center=True).offset(
        3, JoinType.Round, circular_segments=48)
    caja ^= Manifold.extrude(redondeo, ALTO_CAJA + ALTO_FORMA + 1)
    # ranuras y botones
    for forma, (cx, cy), bisagra in BOTONES:
        corte = Manifold.extrude(ranura_u(cx, cy, bisagra), TAPA + 0.2).translate(
            [0, 0, ALTO_CAJA - TAPA - 0.1])
        caja -= corte
        boton = Manifold.extrude(forma(FORMA).translate([cx, cy]), ALTO_FORMA).translate(
            [0, 0, ALTO_CAJA])
        caja += boton
    return caja


def a_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=True, merge_tex=True, merge_norm=True)


if __name__ == "__main__":
    m = construir()
    print("manifold genus:", m.genus(), "status:", m.status())
    t = a_trimesh(m)
    t.merge_vertices()
    assert t.is_watertight
    t.export("botonera_nch.stl")
    t.export("botonera_nch.3mf")
    vol_cm3 = t.volume / 1000
    print(f"bbox mm: {t.extents.round(1)}  volumen: {vol_cm3:.2f} cm3  "
          f"PLA macizo: {vol_cm3 * 1.24:.1f} g")
