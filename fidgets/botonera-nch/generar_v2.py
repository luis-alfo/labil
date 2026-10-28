"""Botonera NocodeHackers v2: clic real, 100 % impreso.

Igual que la v1, pero bajo el borde libre de cada lengüeta hay una cuchilla
vertical flexible con un diente en cuña. Al pulsar, la lengüeta empuja el
diente, la cuchilla cede y vuelve de golpe: clic al bajar y otro al soltar.
Uso: python3 generar_v2.py
"""
import generar as v1
from generar import CELDA, PARED, SUELO, ALTO_CAJA, TAPA, LENGUA, BOTONES, a_trimesh
from manifold3d import CrossSection, Manifold

# --- Parámetros del clic (mm) ---
CUCHILLA = 0.8      # grosor de la cuchilla (más fina = clic más suave)
LARGO_CUCHILLA = 8.0
SOLAPE = 0.5        # cuánto se mete el diente bajo la lengüeta (más = clic más fuerte)
HUECO_Z = 0.4       # holgura vertical diente-lengüeta (2 capas a 0,2 mm)

# hacia dónde mira el borde libre (opuesto a la bisagra), en grados
GIRO = {"izq": 0, "arriba": 270, "abajo": 90, "der": 180}


def trinquete():
    """Cuchilla + diente para un borde libre en +x, centrado en la celda."""
    borde = LENGUA / 2                      # x del borde libre de la lengüeta
    z_lengua = ALTO_CAJA - TAPA             # cara inferior de la lengüeta
    z_top = z_lengua - HUECO_Z              # techo del diente
    z_pico = z_top - 0.6
    z_base = z_pico - 1.4                   # cara inferior a 45°: imprimible
    exterior = borde + CUCHILLA
    # perfil XZ de cuchilla + diente
    perfil = CrossSection([[
        (borde, SUELO - 0.01), (exterior, SUELO - 0.01), (exterior, z_top),
        (borde, z_top), (borde - SOLAPE, z_pico), (borde, z_base),
    ]])
    pieza = Manifold.extrude(perfil, LARGO_CUCHILLA).translate([0, 0, -LARGO_CUCHILLA / 2])
    return pieza.rotate([90, 0, 0])         # XZ -> plano vertical, largo en Y


def construir():
    caja = v1.construir()
    base = trinquete()
    for _, (cx, cy), bisagra in BOTONES:
        caja += base.rotate([0, 0, GIRO[bisagra]]).translate([cx, cy, 0])
    return caja


if __name__ == "__main__":
    m = construir()
    t = a_trimesh(m)
    assert m.status().name == "NoError" and t.is_watertight
    t.export("botonera_nch_v2.stl")
    t.export("botonera_nch_v2.3mf")
    vol = t.volume / 1000
    print(f"bbox mm: {t.extents.round(1)}  volumen: {vol:.2f} cm3  PLA macizo: {vol * 1.24:.1f} g")
