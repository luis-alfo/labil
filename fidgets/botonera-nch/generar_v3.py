"""Botonera NocodeHackers v3: botones que bajan enteros y rectos, con clic.

Cada botón va sobre un disco unido a la tapa por 4 brazos en espiral
(flexura simétrica): al pulsar, el disco baja paralelo, sin bisagra.
Debajo, dos cuchillas con diente en cuña dan el clic al bajar y al soltar.
Todo impreso en una pieza, sin muelles ni piezas extra.
Uso: python3 generar_v3.py  -> botonera_nch_v3.stl / .3mf / _color.3mf
"""
import math
from manifold3d import CrossSection, Manifold
import generar as v1
from generar import a_trimesh, casa, circulo, cuadrado_cortado

# --- Parámetros (mm) ---
CELDA = 28.0
PARED = 2.0
SUELO = 1.6
ALTO_CAJA = 9.0
TAPA = 1.2
FORMA = 14.0         # tamaño de cada forma (cabe dentro del disco)
ALTO_FORMA = 3.0
DISCO = 9.2          # radio del disco que baja
HOLGURA = 0.6        # ranura entre disco, brazos y marco
BRAZO = 1.4          # ancho de cada brazo en espiral (más = más duro)
ARCO_BRAZO = 60      # grados que recorre cada brazo (más = más blando)
N_BRAZOS = 4
# clic
CUCHILLA = 0.8
LARGO_CUCHILLA = 3.0
SOLAPE = 0.5
HUECO_Z = 0.4
LADO = 2 * CELDA + PARED
SEG = 96

BOTONES = [
    (casa, (-CELDA / 2, CELDA / 2)),
    (circulo, (CELDA / 2, CELDA / 2)),
    (circulo, (-CELDA / 2, -CELDA / 2)),
    (cuadrado_cortado, (CELDA / 2, -CELDA / 2)),
]

R_BRAZO_IN = DISCO + HOLGURA
R_BRAZO_OUT = R_BRAZO_IN + BRAZO
R_CORTE = R_BRAZO_OUT + HOLGURA


def sector(r0, r1, a0, a1):
    n = max(4, int(abs(a1 - a0) / 3))
    ang = [math.radians(a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    pts = [(r1 * math.cos(a), r1 * math.sin(a)) for a in ang]
    pts += [(r0 * math.cos(a), r0 * math.sin(a)) for a in reversed(ang)]
    return CrossSection([pts])


def resorte():
    """Material de tapa dentro del anillo de corte: disco + brazos en espiral."""
    m = CrossSection.circle(DISCO, SEG)
    paso = 360 / N_BRAZOS
    ancho_conector = math.degrees(BRAZO / R_BRAZO_IN)
    for i in range(N_BRAZOS):
        a0 = i * paso
        a1 = a0 + ARCO_BRAZO
        m += sector(R_BRAZO_IN, R_BRAZO_OUT, a0, a1)                      # brazo
        m += sector(DISCO - 0.2, R_BRAZO_IN + 0.2, a0, a0 + ancho_conector)  # al disco
        m += sector(R_BRAZO_OUT - 0.2, R_CORTE + 0.2, a1 - ancho_conector, a1)  # al marco
    return m


def trinquete(angulo):
    """Cuchilla vertical con diente bajo el borde del disco, en `angulo`."""
    z_disco = ALTO_CAJA - TAPA
    z_top = z_disco - HUECO_Z
    z_pico = z_top - 0.6
    z_base = z_pico - 1.4
    r_in, r_out = DISCO, DISCO + CUCHILLA
    perfil = CrossSection([[
        (r_in, SUELO - 0.01), (r_out, SUELO - 0.01), (r_out, z_top),
        (r_in, z_top), (r_in - SOLAPE, z_pico), (r_in, z_base),
    ]])
    pieza = Manifold.extrude(perfil, LARGO_CUCHILLA).translate([0, 0, -LARGO_CUCHILLA / 2])
    return pieza.rotate([90, 0, 0]).rotate([0, 0, angulo])


def construir(con_logo=True):
    h = LADO / 2
    caja = Manifold.cube([LADO, LADO, ALTO_CAJA]).translate([-h, -h, 0])
    redondeo = CrossSection.square([LADO - 6, LADO - 6], center=True).offset(
        3, v1.JoinType.Round, circular_segments=48)
    caja ^= Manifold.extrude(redondeo, ALTO_CAJA)
    paso = 360 / N_BRAZOS
    # dientes en el hueco entre el final de un brazo y el inicio del siguiente
    angulos_clic = [ARCO_BRAZO + (paso - ARCO_BRAZO) / 2 + k * 180 for k in (0, 1)]
    logo = Manifold()
    for forma, (cx, cy) in BOTONES:
        c = CELDA - PARED
        caja -= Manifold.cube([c, c, ALTO_CAJA - SUELO - TAPA]).translate(
            [cx - c / 2, cy - c / 2, SUELO])
        anillo = CrossSection.circle(R_CORTE, SEG) - resorte()
        caja -= Manifold.extrude(anillo, TAPA + 0.2).translate([cx, cy, ALTO_CAJA - TAPA - 0.1])
        for a in angulos_clic:
            caja += trinquete(a).translate([cx, cy, 0])
        logo += Manifold.extrude(forma(FORMA).translate([cx, cy]), ALTO_FORMA).translate(
            [0, 0, ALTO_CAJA])
    return (caja + logo) if con_logo else (caja, logo)


if __name__ == "__main__":
    import exportar_color
    m = construir()
    t = a_trimesh(m)
    assert m.status().name == "NoError" and t.is_watertight
    t.export("botonera_nch_v3.stl")
    t.export("botonera_nch_v3.3mf")
    exportar_color.piezas = lambda: construir(con_logo=False)
    exportar_color.exportar("botonera_nch_v3_color.3mf")
    vol = t.volume / 1000
    print(f"bbox mm: {t.extents.round(1)}  volumen: {vol:.2f} cm3  PLA macizo: {vol * 1.24:.1f} g")
