"""Botonera NocodeHackers v4: mecanismo oculto.

Mismo principio que la v3 (disco con brazos en espiral + clic), pero el resorte
es más pequeño y cada forma del logo es una tecla grande que lo tapa entero.
La tecla se apoya en un vástago y su cara inferior es un cono a 45°, así que
se imprime sin soportes y deja holgura para bajar.
Uso: python3 generar_v4.py -> botonera_nch_v4.stl / .3mf / _color.3mf
"""
import math
from manifold3d import CrossSection, Manifold
import generar_v3 as v3

# resorte compacto (3 brazos de 95° para que siga siendo blando)
v3.DISCO = 5.0
v3.BRAZO = 1.2
v3.N_BRAZOS = 3
v3.ARCO_BRAZO = 95
v3.LARGO_CUCHILLA = 2.0
v3.R_BRAZO_IN = v3.DISCO + v3.HOLGURA
v3.R_BRAZO_OUT = v3.R_BRAZO_IN + v3.BRAZO
v3.R_CORTE = v3.R_BRAZO_OUT + v3.HOLGURA

TECLA = 20.0        # tamaño de cada forma (tapa el resorte)
VASTAGO = 5.0       # radio del vástago que une disco y tecla
ALTO_VASTAGO = 1.6  # holgura bajo la tecla > recorrido del botón
GROSOR_TECLA = 1.6  # parte plana superior de la tecla
PENDIENTE = 1.4     # mm de vuelo por mm de altura (~55°, imprimible en la A1)


def tecla(forma, cx, cy):
    """Tecla con la forma del logo; por debajo, cono que la une al vástago."""
    z0 = v3.ALTO_CAJA
    perfil2d = forma(TECLA)
    r_max = max(math.hypot(x, y) for poly in perfil2d.to_polygons() for x, y in poly)
    alto_cono = (r_max - VASTAGO) / PENDIENTE
    alto = ALTO_VASTAGO + alto_cono + GROSOR_TECLA
    vastago = Manifold.cylinder(ALTO_VASTAGO + 0.01, VASTAGO, VASTAGO, 96).translate([0, 0, z0])
    cono = Manifold.cylinder(alto_cono, VASTAGO, r_max + 0.1, 96).translate(
        [0, 0, z0 + ALTO_VASTAGO])
    plano = Manifold.cylinder(GROSOR_TECLA, r_max + 0.1, r_max + 0.1, 96).translate(
        [0, 0, z0 + ALTO_VASTAGO + alto_cono])
    cuerpo = (vastago + cono + plano) ^ Manifold.extrude(perfil2d, alto).translate([0, 0, z0])
    return cuerpo.translate([cx, cy, 0])


def construir(con_logo=True):
    caja, _ = v3.construir(con_logo=False)
    logo = Manifold()
    for forma, (cx, cy) in v3.BOTONES:
        logo += tecla(forma, cx, cy)
    return (caja + logo) if con_logo else (caja, logo)


if __name__ == "__main__":
    import exportar_color
    m = construir()
    t = v3.a_trimesh(m)
    assert m.status().name == "NoError" and t.is_watertight
    t.export("botonera_nch_v4.stl")
    t.export("botonera_nch_v4.3mf")
    exportar_color.piezas = lambda: construir(con_logo=False)
    exportar_color.exportar("botonera_nch_v4_color.3mf")
    vol = t.volume / 1000
    print(f"bbox mm: {t.extents.round(1)}  PLA macizo: {vol * 1.24:.1f} g")
