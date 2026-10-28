"""Botón NocodeHackers v5: 3 piezas impresas que encajan (prueba de 1 botón).

Lección de la v4: los brazos en espiral impresos en el aire se rompen.
Aquí cada pieza se imprime en su mejor orientación:
  - resorte: plano sobre la cama, 3 brazos en espiral largos (PETG recomendado)
  - carcasa: boca abajo (la cara superior sobre la cama)
  - tecla:   boca abajo, con valona a 45° que la retiene bajo la tapa
Montaje: tecla por debajo de la carcasa, luego el resorte a presión
(brazos arriba) encajando el pivote de la tecla en el buje.
Uso: python3 generar_v5.py -> boton_v5_*.stl y boton_v5_piezas.3mf
"""
import math
import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold
from generar import a_trimesh, casa, JoinType

# --- Parámetros (mm) ---
LADO = 30.0
PARED = 2.0
HUECO = LADO - 2 * PARED          # interior de la carcasa
AJUSTE = 0.05                     # holgura resorte-carcasa (encaje a presión)
FORMA = casa
TAM = 18.0                        # tamaño de la tecla
HOLGURA_GUIA = 0.3                # tecla-agujero de la tapa
VALONA = 1.5                      # lo que sobresale la valona bajo la tapa
RECORRIDO = 1.5

# resorte
ALTO_MARCO = 3.2                  # el marco apoya en la mesa
GROSOR_BRAZO = 1.2                # brazos y buje (cara superior una vez montado)
ANCHO_BRAZO = 1.6
N_BRAZOS = 3
GIRO_BRAZO = 240                  # grados que recorre cada espiral (más = más blando)
R_BUJE = 4.5
R_AGUJERO = 2.0                   # agujero del buje para el pivote
R_LIBRE = HUECO / 2 - 1.6         # radio útil dentro del marco

# alturas (montado, z desde la mesa)
Z_BUJE = ALTO_MARCO               # cara superior de brazos/buje
Z_VALONA = Z_BUJE + RECORRIDO + 0.7   # base de la valona
Z_TAPA_INF = Z_VALONA + VALONA
TAPA = 2.0
Z_TAPA_SUP = Z_TAPA_INF + TAPA
SOBRESALE = 4.0                   # tecla por encima de la carcasa


def espiral(fase):
    """Brazo en espiral de Arquímedes del buje al marco."""
    r0, r1 = R_BUJE - 0.3, R_LIBRE + 0.6
    n = 120
    t = np.linspace(0, 1, n)
    ang = np.radians(fase + GIRO_BRAZO * t)
    r = r0 + (r1 - r0) * t
    w = ANCHO_BRAZO / 2
    ext = [((r[i] + w) * math.cos(ang[i]), (r[i] + w) * math.sin(ang[i])) for i in range(n)]
    inn = [((r[i] - w) * math.cos(ang[i]), (r[i] - w) * math.sin(ang[i])) for i in reversed(range(n))]
    return CrossSection([ext + inn])


def resorte():
    """Impreso tal cual: brazos sobre la cama (z=0), marco hacia arriba."""
    lado = HUECO - 2 * AJUSTE
    marco2d = CrossSection.square([lado, lado], center=True) - CrossSection.circle(R_LIBRE, 96)
    marco = Manifold.extrude(marco2d, ALTO_MARCO)
    plano = CrossSection.circle(R_BUJE, 96)
    for i in range(N_BRAZOS):
        plano += espiral(i * 360 / N_BRAZOS)
    plano -= CrossSection.circle(R_AGUJERO, 48)
    return marco + Manifold.extrude(plano, GROSOR_BRAZO)


def carcasa():
    """Coordenadas de montaje (z desde la mesa)."""
    cuerpo = Manifold.extrude(CrossSection.square([LADO, LADO], center=True).offset(
        -2, JoinType.Round).offset(2, JoinType.Round), Z_TAPA_SUP)
    hueco = Manifold.cube([HUECO, HUECO, Z_TAPA_INF + 0.01], center=False).translate(
        [-HUECO / 2, -HUECO / 2, -0.01])
    guia = Manifold.extrude(FORMA(TAM).offset(HOLGURA_GUIA, JoinType.Round), TAPA + 1).translate(
        [0, 0, Z_TAPA_INF - 0.5])
    return cuerpo - hueco - guia


def tecla():
    """Coordenadas de montaje."""
    escala = TAM / (TAM + 2 * VALONA)
    valona = Manifold.extrude(FORMA(TAM + 2 * VALONA), VALONA, scale_top=[escala, escala]).translate(
        [0, 0, Z_VALONA])
    cuerpo = Manifold.extrude(FORMA(TAM), Z_TAPA_SUP + SOBRESALE - Z_VALONA - VALONA).translate(
        [0, 0, Z_VALONA + VALONA])
    pivote = Manifold.cylinder(Z_VALONA - Z_BUJE + 0.01, 3.0, 3.0, 64).translate([0, 0, Z_BUJE])
    punta = Manifold.cylinder(GROSOR_BRAZO + 0.01, R_AGUJERO, R_AGUJERO, 48).translate(
        [0, 0, Z_BUJE - GROSOR_BRAZO])
    return valona + cuerpo + pivote + punta


def boca_abajo(m):
    m = m.rotate([180, 0, 0])
    return m.translate([0, 0, -m.bounding_box()[2]])


if __name__ == "__main__":
    piezas = {
        "resorte": resorte(),
        "carcasa": boca_abajo(carcasa()),
        "tecla": boca_abajo(tecla()),
    }
    escena = trimesh.Scene()
    for i, (nombre, m) in enumerate(piezas.items()):
        assert m.status().name == "NoError"
        t = a_trimesh(m)
        assert t.is_watertight, nombre
        t.export(f"boton_v5_{nombre}.stl")
        t.apply_translation([(i - 1) * 40, 0, 0])
        escena.add_geometry(t, geom_name=nombre)
        print(f"{nombre}: {t.extents.round(1)} mm, {t.volume / 1000 * 1.24:.1f} g")
    escena.export("boton_v5_piezas.3mf")
    # comprobación de montaje: sin interferencias
    c, k, r = carcasa(), tecla(), resorte().rotate([180, 0, 0]).translate([0, 0, ALTO_MARCO])
    print("choque tecla-carcasa:", round((c ^ k).volume(), 3),
          "resorte-carcasa:", round((c ^ r).volume(), 3),
          "tecla-resorte:", round((k ^ r).volume(), 3))
