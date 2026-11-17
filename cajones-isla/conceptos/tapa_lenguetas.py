"""Tapa de 3 voltes con lengüetas flexibles (sustituye a la de costillas, que se caía).

Por qué cambia: la tapa de costillas (tapa.py) era un encaje a presión rígido:
129 mm de cuerpo + costillas que apretaban 0,3 mm por lado contra un hueco que
se suponía de 130,0 mm. Esa medida salió de un flexómetro (±0,5–1 mm) y nunca
se comprobó. Con el hueco real más ancho, las costillas ni tocaban.

Ahora sujetan 4 lengüetas: láminas de 2 mm que flexan en el plano de las capas
(la dirección fuerte) y sobresalen SALIENTE mm por cada costado. Aprietan en
cualquier hueco entre ANCHO_HUECO y ANCHO_HUECO + 2·(SALIENTE − 1).

Ejes de la tapa: x = ancho (centrado), y = fondo (0 = cara vista), z = alto
(0 = estante). Se imprime boca abajo: la y es la altura de impresión.

Uso:
    python3 tapa_lenguetas.py                              # 130 × 135, saliente 4
    python3 tapa_lenguetas.py --ancho-hueco 131.5 --alto-hueco 135.5
"""
import argparse
import os
import sys

import numpy as np
import trimesh
from manifold3d import CrossSection, JoinType, Manifold, OpType

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from cajon import ESTILOS, arcos, box, corte, rrect, vertical  # noqa: E402

PLA = 1.24

# === Hueco (lo que se mide) ===
ANCHO_HUECO = 130.0
ALTO_HUECO = 135.0
HOLGURA = 0.5            # rendija por lado entre el frente y el hueco

# === Frente y faldón ===
TF = 2.0                 # grosor del frente
RADIO, CHAFLAN = 2.0, 1.0
FALDON = 12.0            # lo que entra en el hueco
PARED = 1.2              # pared del faldón (3 líneas)
RETIRO = 7.6             # el faldón va metido esto desde el canto, para dejar sitio a las lengüetas
RETIRO_V = 1.0           # y esto arriba y abajo

# === Lengüetas ===
SALIENTE = 4.0           # lo que sobresale el tope de cada lengüeta fuera del canto del frente, en reposo
LEN_T = 2.0              # grueso de la lámina
LEN_L = 46.0             # largo de la lámina
LEN_DENTRO = 0.4         # la lámina queda esto por dentro del canto (no roza el hueco)
LEN_AIRE = 1.4           # hueco entre la lámina y el frente (se imprime en puente)
RAIZ_MEDIA = 5.0         # media altura del taco que une las dos lengüetas de un lado al faldón
TOPE_L = 6.0             # largo del tope al final de la lámina
TOPE_PLANO = 1.5         # cresta plana del tope
POSTE = (1.8, 0.8)       # apoyos de impresión bajo cada lámina (se sueltan al flexarla)
POSTE_AIRE = 0.2         # una capa de aire entre el apoyo y la lámina

PIE_ANCHO, PIE_X = 14.0, 40.0


def _a_lo_ancho(cs, ancho, x0):
    """Extruye un perfil (y, z) a lo largo de x, desde x0."""
    giro = np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], dtype=np.float32)
    return cs.extrude(ancho).transform(giro).translate((x0, 0, 0))


def medidas(ancho_hueco=ANCHO_HUECO, alto_hueco=ALTO_HUECO, holgura=HOLGURA):
    return ancho_hueco - 2 * holgura, alto_hueco - 2 * holgura


def lenguetas(wp, hp, holgura, saliente, lado):
    """Las dos lengüetas de un costado (lado = ±1) con su taco, topes y apoyos."""
    zc = holgura + hp / 2
    x_ext = wp / 2 - LEN_DENTRO                 # cara exterior de la lámina
    x_int = x_ext - LEN_T
    x_fal = wp / 2 - RETIRO                     # cara exterior del faldón
    y_lam = TF + LEN_AIRE                       # donde empieza la lámina (deja aire con el frente)
    y_fin = TF + FALDON

    def rect(x0, x1, z0, z1):
        return CrossSection([[(x0, z0), (x1, z0), (x1, z1), (x0, z1)]])

    # Las piezas se solapan siempre con volumen (nunca cara contra arista): así la malla sale limpia.
    taco = rect(x_fal - 0.5, x_ext - 0.2, zc - RAIZ_MEDIA, zc + RAIZ_MEDIA)
    laminas = rect(x_int, x_ext, zc - RAIZ_MEDIA - LEN_L, zc + RAIZ_MEDIA + LEN_L)
    # radio de 2 mm en el arranque de cada lámina: ahí se concentra el esfuerzo
    r = 2.0
    for s_ in (1, -1):
        zr = zc + s_ * RAIZ_MEDIA
        cuadro = rect(x_int - r, x_int + 0.2, min(zr - s_ * 0.2, zr + s_ * r), max(zr - s_ * 0.2, zr + s_ * r))
        laminas += cuadro - CrossSection.circle(r, 48).translate((x_int - r, zr + s_ * r))
    m = vertical(taco, y_fin - TF + 0.5, 0.0, y=TF - 0.5)
    m += vertical(laminas, y_fin - y_lam, 0.0, y=y_lam)

    # tope: rampa a ~45° por delante (se imprime sin soporte) y rampa de entrada por detrás
    h = saliente + LEN_DENTRO
    cresta0 = y_lam + h
    tope = CrossSection([[(x_ext - 0.3, y_lam + 0.05), (x_ext + h, cresta0),
                          (x_ext + h, cresta0 + TOPE_PLANO), (x_ext - 0.3, y_fin - 0.05)]])
    assert cresta0 + TOPE_PLANO < y_fin - 1.0, "saliente demasiado grande para este faldón"
    for z_punta, sentido in ((zc + RAIZ_MEDIA + LEN_L, -1), (zc - RAIZ_MEDIA - LEN_L, 1)):
        z_a, z_b = z_punta + sentido * 0.4, z_punta + sentido * (0.4 + TOPE_L)
        m += tope.extrude(TOPE_L).translate((0, 0, min(z_a, z_b)))
        # apoyos de impresión: a 1/3, a 2/3 y bajo la punta
        for f in (1 / 3, 2 / 3, 1.0):
            z = z_punta + sentido * ((1 - f) * LEN_L + (1.5 if f == 1.0 else 0))
            m += box(x_int + 0.1, TF - 0.3, z - POSTE[1] / 2, POSTE[0], y_lam - POSTE_AIRE - TF + 0.3, POSTE[1])
    return m if lado > 0 else m.mirror((1, 0, 0))


def pies(wp, holgura):
    """Dos pies bajo el faldón: levantan el frente HOLGURA del estante (rendija igual abajo que arriba)."""
    # la rampa a 45° arranca 0,2 mm antes de la cara trasera del frente: se imprime sin soporte
    perfil = CrossSection([[(TF - 0.5, holgura + 0.3), (TF - 0.2 + holgura, 0.0), (TF + FALDON, 0.0),
                            (TF + FALDON, holgura + RETIRO_V + 0.5), (TF - 0.5, holgura + RETIRO_V + 0.5)]])
    return (_a_lo_ancho(perfil, PIE_ANCHO, PIE_X - PIE_ANCHO / 2)
            + _a_lo_ancho(perfil, PIE_ANCHO, -PIE_X - PIE_ANCHO / 2))


def tapa(variante="pasante", ancho_hueco=ANCHO_HUECO, alto_hueco=ALTO_HUECO,
         holgura=HOLGURA, saliente=SALIENTE):
    wp, hp = medidas(ancho_hueco, alto_hueco, holgura)
    zc = holgura + hp / 2

    t = vertical(rrect(wp, hp, RADIO).translate((0, zc)), TF, CHAFLAN)

    # faldón: anillo metido RETIRO por los lados
    fw, fh = wp - 2 * RETIRO, hp - 2 * RETIRO_V
    aro = rrect(fw, fh, 1.5).translate((0, zc)) - rrect(fw - 2 * PARED, fh - 2 * PARED, 0.6).translate((0, zc))
    t += vertical(aro, FALDON + 0.5, 0.0, y=TF - 0.5)
    t += pies(wp, holgura)
    for lado in (1, -1):
        t += lenguetas(wp, hp, holgura, saliente, lado)

    _, aw, ah, zrel, n = ESTILOS["revoltons3"]["abertura"]
    z_arco = holgura + zrel * hp / 134.0 - ah / 2
    hueco = arcos(aw, ah, z_arco, n)
    if variante == "aro":
        # solo el contorno: prueba barata de las lengüetas y del encaje
        vx, vz = fw - 2 * PARED - 4.0, fh - 2 * PARED - 4.0
        t -= corte(rrect(vx, vz, 6.0).translate((0, zc)), TF)
        return t
    t -= corte(hueco, TF, CHAFLAN)
    if variante == "bolsillo":
        fondo = 8.8
        cav = arcos(aw, ah + 8, z_arco, n)                 # mismo arco, 8 mm más alto: ahí engancha la yema
        caja = vertical(cav.offset(1.2, JoinType.Round, circular_segments=16), fondo + 1.7, 0.0, y=TF - 0.5)
        t = t + caja - vertical(cav, fondo + 0.5, 0.0, y=TF - 0.5)
    return t


def para_imprimir(m):
    """Boca abajo, apoyada en la cama y en el origen."""
    imp = m.rotate((90, 0, 0))
    bb = imp.bounding_box()
    return imp.translate((-bb[0], -bb[1], -bb[2]))


def malla(m):
    me = m.to_mesh()
    return trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts)


def rigidez(saliente=SALIENTE, e_pla=3000.0):
    """N/mm de una lengüeta y deformación máxima (%) si se aplasta del todo."""
    b = FALDON - LEN_AIRE
    largo = LEN_L - TOPE_L / 2
    k = 3 * e_pla * (b * LEN_T ** 3 / 12) / largo ** 3
    return k, 100 * 3 * LEN_T * saliente / (2 * largo ** 2)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ancho-hueco", type=float, default=ANCHO_HUECO)
    p.add_argument("--alto-hueco", type=float, default=ALTO_HUECO)
    p.add_argument("--holgura", type=float, default=HOLGURA)
    p.add_argument("--saliente", type=float, default=SALIENTE)
    p.add_argument("--sufijo", default="", help="se añade al nombre de los STL, p. ej. _131x136")
    a = p.parse_args()

    out = os.path.join(AQUI, "..", "stl")
    os.makedirs(out, exist_ok=True)
    wp, hp = medidas(a.ancho_hueco, a.alto_hueco, a.holgura)
    k, eps = rigidez(a.saliente)
    print(f"Frente {wp:.1f} × {hp:.1f} mm · en reposo mide {wp + 2 * a.saliente:.1f} mm de tope a tope")
    print(f"Aprieta en huecos de {a.ancho_hueco:.1f} a {wp + 2 * (a.saliente - 1):.1f} mm de ancho")
    print(f"Lengüeta: {k:.2f} N/mm · deformación máxima {eps:.2f} %")
    for v in ("aro", "pasante", "bolsillo"):
        m = tapa(v, a.ancho_hueco, a.alto_hueco, a.holgura, a.saliente)
        t = malla(para_imprimir(m))
        assert t.is_watertight, f"la malla de {v} no es cerrada"
        t.export(os.path.join(out, f"tapa_lenguetas_{v}{a.sufijo}.stl"))
        e = t.bounds[1] - t.bounds[0]
        print(f"{v:9s} {m.volume() / 1000 * PLA:5.1f} g macizo · {e[0]:.1f} × {e[1]:.1f} × {e[2]:.1f} mm · piezas sueltas: {len(m.decompose())}")


if __name__ == "__main__":
    main()
