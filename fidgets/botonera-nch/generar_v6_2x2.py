"""Botonera NocodeHackers 2×2 con el botón v6 (46 × 46 mm).

Una carcasa con 4 celdas (paredes compartidas), 4 teclas con las formas del
logo, 4 resortes v6 idénticos y una tapa trasera que los apoya a la misma altura
y engancha a presión en una ranura de la carcasa. Todo impreso.
Uso: python3 generar_v6_2x2.py -> botonera_v6_2x2.3mf
"""
import trimesh
from manifold3d import CrossSection, Manifold
import generar_v6  # noqa: F401  (aplica los parámetros de la v6)
import generar_v5 as v5
from generar import casa, circulo, cuadrado_cortado, JoinType

PASO = v5.HUECO + v5.PARED          # distancia entre centros de celda
TOTAL = 2 * v5.HUECO + 3 * v5.PARED
BOTONES = [  # forma, centro (vista desde arriba, como el logo)
    (casa, (-PASO / 2, PASO / 2)),
    (circulo, (PASO / 2, PASO / 2)),
    (circulo, (-PASO / 2, -PASO / 2)),
    (cuadrado_cortado, (PASO / 2, -PASO / 2)),
]


# tapa trasera: bandeja que abraza la carcasa por fuera y engancha en una ranura
GROSOR_TAPA = 1.6
FALDA = 3.0          # altura del borde que sube por la carcasa
PARED_FALDA = 1.2
HOLGURA_TAPA = 0.15
RANURA_Z = (1.0, 2.2)  # ranura en la carcasa (z desde la base)
RANURA_P = 0.5         # profundidad de la ranura
PESTANA_ANCHO = 12.0   # pestaña para tirar y sacar la tapa
PESTANA_VUELO = 5.0


def contorno(extra=0.0):
    return CrossSection.square([TOTAL, TOTAL], center=True).offset(
        -3, JoinType.Round).offset(3 + extra, JoinType.Round, circular_segments=64)


def anillo(r_in, r_out, z0, z1):
    return Manifold.extrude(contorno(r_out) - contorno(r_in), z1 - z0).translate([0, 0, z0])


def tapa():
    """Coordenadas de montaje: la base queda en z < 0, bajo la carcasa."""
    g, h = HOLGURA_TAPA, PARED_FALDA
    base = Manifold.extrude(contorno(g + h), GROSOR_TAPA).translate([0, 0, -GROSOR_TAPA])
    falda = anillo(g, g + h, -0.01, FALDA)
    # cordón de enganche en cuña (entra en la ranura de la carcasa)
    z0, z1 = RANURA_Z
    zc = (z0 + z1) / 2
    cordon = (anillo(-0.05, g + 0.01, z0 + 0.2, z0 + 0.45) + anillo(-0.2, g + 0.01, z0 + 0.45, z1 - 0.45)
              + anillo(-0.05, g + 0.01, z1 - 0.45, z1 - 0.2))
    # pestaña para sacarla: sobresale de un lado, a ras de la base
    borde = TOTAL / 2 + g + h
    pestana = Manifold.extrude(CrossSection.square([PESTANA_ANCHO, PESTANA_VUELO + 3], center=True).offset(
        -1.5, JoinType.Round).offset(1.5, JoinType.Round), GROSOR_TAPA).translate(
        [0, -(borde + PESTANA_VUELO / 2 - 1.5), -GROSOR_TAPA])
    return base + falda + cordon + pestana


def carcasa():
    cuerpo = Manifold.extrude(contorno(), v5.Z_TAPA_SUP)
    cuerpo -= anillo(-RANURA_P, 1, *RANURA_Z)
    for forma, (cx, cy) in BOTONES:
        h = v5.HUECO
        cuerpo -= Manifold.cube([h, h, v5.Z_TAPA_INF + 0.01]).translate([cx - h / 2, cy - h / 2, -0.01])
        guia = Manifold.extrude(forma(v5.TAM).offset(v5.HOLGURA_GUIA, JoinType.Round), v5.TAPA + 1)
        cuerpo -= guia.translate([cx, cy, v5.Z_TAPA_INF - 0.5])
    return cuerpo


def tecla(forma):
    v5.FORMA = forma
    return v5.tecla()


if __name__ == "__main__":
    c = carcasa()
    teclas = [tecla(f).translate([x, y, 0]) for f, (x, y) in BOTONES]
    resortes = [v5.resorte().rotate([180, 0, 0]).translate([x, y, v5.ALTO_MARCO]) for _, (x, y) in BOTONES]
    choque = sum((c ^ k).volume() for k in teclas) + sum((c ^ r).volume() for r in resortes) + \
        sum((k ^ r).volume() for k, r in zip(teclas, resortes))
    tp = tapa()
    choque += (tp ^ c).volume() + sum((tp ^ r).volume() for r in resortes)
    print("choques montado:", round(choque, 3))

    escena = trimesh.Scene()
    def poner(m, nombre, x, y):
        t = v5.a_trimesh(m)
        assert m.status().name == "NoError" and t.is_watertight, nombre
        t.apply_translation([x, y, 0])
        escena.add_geometry(t, geom_name=nombre)
        return t.volume / 1000 * 1.24
    g = poner(v5.boca_abajo(c), "carcasa", 0, 0)
    g += poner(tp.translate([0, 0, GROSOR_TAPA]), "tapa_trasera", 60, 0)
    for i, (f, _) in enumerate(BOTONES):
        g += poner(v5.boca_abajo(tecla(f)), f"tecla_{f.__name__}_{i}", -40 + i * 22 - 5, 45)
        g += poner(v5.resorte(), f"resorte_{i}", -40 + i * 24 - 5, -45)
    escena.export("botonera_v6_2x2.3mf")
    print(f"carcasa {TOTAL:.0f} × {TOTAL:.0f} × {v5.Z_TAPA_SUP:.1f} mm, total {g:.1f} g PLA macizo")
