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


# tapa trasera: placa que entra en un rebaje de la carcasa, a ras por debajo
GROSOR_TAPA = 1.6
HOLGURA_TAPA = 0.15
CORDON = 0.3           # lo que sobresale el cordón de enganche del canto de la tapa
UNA_ANCHO = 10.0       # muesca para meter la uña y sacar la tapa
UNA_HUECO = 0.8        # hueco libre sobre la pestaña


def contorno(extra=0.0):
    return CrossSection.square([TOTAL, TOTAL], center=True).offset(
        -3, JoinType.Round).offset(3 + extra, JoinType.Round, circular_segments=64)


def capa(forma2d, z0, z1):
    return Manifold.extrude(forma2d, z1 - z0).translate([0, 0, z0])


def muesca():
    """Hueco en la pared de un lado (y negativo) para la pestaña y la uña."""
    return Manifold.cube([UNA_ANCHO, v5.PARED + 2, GROSOR_TAPA + 0.01]).translate(
        [-UNA_ANCHO / 2, -TOTAL / 2 - 1, -GROSOR_TAPA - 0.01])


def tapa():
    """Coordenadas de montaje: ocupa z en [-GROSOR_TAPA, 0], dentro del rebaje."""
    g, e = HOLGURA_TAPA, GROSOR_TAPA
    placa = capa(contorno(-v5.PARED - g), -e, 0)
    cordon = (capa(contorno(-v5.PARED - g + CORDON * 0.5), -e + 0.3, -e + 0.55)
              + capa(contorno(-v5.PARED - g + CORDON), -e + 0.55, -e + 0.85)
              + capa(contorno(-v5.PARED - g + CORDON * 0.5), -e + 0.85, -e + 1.1))
    pestana = Manifold.cube([UNA_ANCHO - 2 * g, v5.PARED + 0.1, e - UNA_HUECO]).translate(
        [-(UNA_ANCHO - 2 * g) / 2, -TOTAL / 2 + 0.2, -e])
    return placa + (cordon - muesca()) + pestana


def carcasa():
    cuerpo = Manifold.extrude(contorno(), v5.Z_TAPA_SUP)
    # rebaje inferior para la tapa: solo queda la pared exterior, con ranura y muesca
    e = GROSOR_TAPA
    aro = capa(contorno() - contorno(-v5.PARED), -e, 0.01)
    ranura = capa(contorno(-v5.PARED + CORDON + 0.1), -e + 0.25, -e + 1.15)
    cuerpo += aro - ranura - muesca()
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
    print(f"altura total con tapa: {v5.Z_TAPA_SUP + GROSOR_TAPA:.1f} mm")
    for i, (f, _) in enumerate(BOTONES):
        g += poner(v5.boca_abajo(tecla(f)), f"tecla_{f.__name__}_{i}", -40 + i * 22 - 5, 45)
        g += poner(v5.resorte(), f"resorte_{i}", -40 + i * 24 - 5, -45)
    escena.export("botonera_v6_2x2.3mf")
    print(f"carcasa {TOTAL:.0f} × {TOTAL:.0f} × {v5.Z_TAPA_SUP:.1f} mm, total {g:.1f} g PLA macizo")
