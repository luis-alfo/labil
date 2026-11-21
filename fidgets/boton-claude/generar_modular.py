#!/usr/bin/env python3
"""Botón Claude modular — dos piezas que encajan, más una galga.

  base   aloja la placa (se deja caer desde arriba) y lleva las muescas para medir
         dónde cae de verdad el botón BOOT. Si la placa no encaja, solo se repite la base.
  tapa   techo con la palanca y el tetón. Se engancha por detrás con dos uñas y hace
         clic delante en un brazo de la base. Aquí irá el relieve de La Guarida.
  galga  escalera de 1,8 a 2,8 mm para leer el alto del pulsador.

Marco (montado): x a lo ancho (0 en el centro), y a lo largo (0 = borde delantero de la
placa; el USB en +y), z hacia arriba (0 = suelo interior, donde apoya la placa).
La base se imprime tal cual; la tapa, boca abajo (techo sobre la placa PEI).

Radios de LG Casa: esquina 4 (delante), canto 2 (detrás). La palanca es el arco de La Guarida.

Uso: python3 generar_modular.py
"""
from pathlib import Path

import numpy as np
import trimesh
from shapely.affinity import translate
from shapely.geometry import LineString, Polygon
from shapely.geometry import box as rect

import generar as g
from generar import caja, cilindro, restar, unir

AQUI = Path(__file__).parent

# === Placa: mismos datos que la funda (generar.py) ===
PCB_W, PCB_L, PCB_T = g.PCB_W, g.PCB_L, g.PCB_T
TETON_X, TETON_Y = g.TETON_X, g.TETON_Y        # centro nominal de BOOT: -3,4 / 13,8

# === Encaje de la placa en la base ===
HOLGURA = 0.2            # por lado
MEDIO = PCB_W / 2 + HOLGURA          # 9,2
CAJ_L = PCB_L + 0.4                  # largo del cajeado: 22,9
SUELO = 1.0
MURO = 1.0               # pared lateral de la base
MURO_H = 1.4             # alto de las paredes de la base sobre el suelo
POSTE = 1.1              # grueso de los postes traseros (aguantan el tirón del cable)
BOCA = 6.5               # media anchura de la boca del USB: el cuerpo del cable mide ~12,4

# === Brazo de cierre (delante, impreso tumbado sobre la placa) ===
MURO_DEL = 0.8           # pared delantera del cajeado
CORTE = 0.7
BRAZO_T = 1.2
BRAZO_X0, BRAZO_X1 = -5.7, 7.0       # punta y raíz
DIENTE = 0.8
DIENTE_X = (-5.2, -1.8)
Y_DEL = -(MURO_DEL + CORTE + BRAZO_T)  # cara delantera de la base: -3,1

# === Tapa ===
JUEGO = 0.2              # entre base y tapa
FALDA = 1.2
TECHO = 1.6
TECHO_Z = g.TECHO_Z      # 4,8
REPISA = 0.8
R_ESQUINA, R_CANTO = 4.0, 2.0

EXT = MEDIO + MURO + JUEGO + FALDA   # media anchura exterior: 11,6
Y0 = Y_DEL - JUEGO - FALDA           # frente exterior: -4,5
Y_POSTE = CAJ_L + POSTE              # trasera de la base: 24,0
Y1 = Y_POSTE + JUEGO + FALDA         # trasera exterior: 25,4
Z0, Z1 = -SUELO, TECHO_Z + TECHO


def planta(x, ya, yb, r_del, r_tras):
    """Rectángulo con las esquinas de delante y de detrás redondeadas a radios distintos."""
    def red(r):
        return rect(-x, ya, x, yb).buffer(-r).buffer(r, resolution=16) if r > 0.01 else rect(-x, ya, x, yb)
    ym = (ya + yb) / 2
    return red(r_del).intersection(rect(-x, ya, x, ym)).union(red(r_tras).intersection(rect(-x, ym, x, yb)))


def prisma(pl, z0, z1):
    m = trimesh.creation.extrude_polygon(pl, z1 - z0)
    m.apply_translation([0, 0, z0])
    return m


def cuna(x0, x1, yz):
    """Prisma a lo largo de x con sección (y, z) dada."""
    return trimesh.convex.convex_hull(np.array([[x, y, z] for x in (x0, x1) for y, z in yz]))


def arco_guarida():
    """El arco de La Guarida (marca/arco-la-guarida.svg, de LG Casa) como eje del corte de la palanca.

    Trazado original: M155 310 V245 Q155 222 178 213 L246 189 Q250 188 254 189 L322 213
    Q345 222 345 245 V310. Se escala a lo ancho de la palanca y la cumbre va en la punta.
    Las patas se alargan hasta la bisagra: la proporción del arco no da brazo suficiente.
    """
    def q(p0, p1, p2, n=10):
        t = np.linspace(0, 1, n)[:, None]
        return (1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t ** 2 * np.array(p2)
    pts = np.vstack([[[155, 245]], q((155, 245), (155, 222), (178, 213)), q((246, 189), (250, 188), (254, 189)),
                     q((322, 213), (345, 222), (345, 245))])
    s = (g.PAL_W + g.CORTE) / 190.0
    cumbre = g.PAL_Y1 + g.CORTE / 2
    xy = [((X - 250) * s, cumbre - (Y - 188) * s) for X, Y in pts]
    return LineString([(xy[0][0], g.PAL_Y0)] + xy + [(xy[-1][0], g.PAL_Y0)])


def base():
    d = FALDA + JUEGO
    pl = planta(EXT - d, Y0 + d, Y1 - d, R_ESQUINA - d, R_CANTO - d)
    cuerpo = prisma(pl, Z0, MURO_H)
    yb = -MURO_DEL                       # cara delantera de la pared del cajeado
    huecos = [
        caja(-MEDIO, MEDIO, 0, CAJ_L, 0, MURO_H + 1),                 # cajeado de la placa
        caja(-BOCA, BOCA, PCB_L, Y1 + 5, Z0 - 1, MURO_H + 1),         # boca del USB, también en el suelo
        # el brazo: suelto del cajeado y del suelo, cogido solo por su raíz
        caja(BRAZO_X0 - CORTE, BRAZO_X1, yb - CORTE, yb, Z0 - 1, MURO_H + 1),
        caja(BRAZO_X0 - CORTE, BRAZO_X0, Y_DEL - 1, yb, Z0 - 1, MURO_H + 1),
        cilindro(BRAZO_X1, yb - CORTE / 2, 0.6, Z0 - 1, MURO_H + 1),  # raíz redondeada
    ]
    for s in (-1, 1):                    # chaflán trasero donde entran las uñas de la tapa
        a, b = sorted((s * BOCA, s * (EXT + 1)))
        huecos.append(cuna(a, b, [(Y_POSTE + 0.01, Z0 - 0.01), (Y_POSTE - 1.01, Z0 - 0.01), (Y_POSTE + 0.01, 0.01)]))
    # muescas de medida: 1 mm de ancho cada 2 mm; la central, más honda, es el centro nominal de BOOT
    for k in range(-2, 3):
        z = 0.6 if k == 0 else 0.9
        y = TETON_Y + 2 * k
        huecos.append(caja(-EXT, -MEDIO + 0.01, y - 0.5, y + 0.5, z, MURO_H + 1))
        huecos.append(caja(MEDIO - 0.01, EXT, y - 0.5, y + 0.5, z, MURO_H + 1))
    for k in range(-1, 2):
        z = 0.6 if k == 0 else 0.9
        x = TETON_X + 2 * k
        huecos.append(caja(x - 0.5, x + 0.5, yb - 0.01, 0.01, z, MURO_H + 1))
    pieza = restar(cuerpo, huecos)
    # diente del brazo: rampa arriba (entra la tapa), cara plana abajo (la retiene)
    y = Y_DEL + 0.05
    diente = cuna(DIENTE_X[0], DIENTE_X[1], [(y, 0.0), (y, 1.3), (y - DIENTE, 0.0), (y - DIENTE, 0.6)])
    return unir([pieza, diente])


def tapa():
    cuerpo = prisma(planta(EXT, Y0, Y1, R_ESQUINA, R_CANTO), Z0, Z1)
    dentro = planta(EXT - FALDA, Y0 + FALDA, Y1 - FALDA, R_ESQUINA - FALDA, R_CANTO - FALDA)
    xp = g.PAL_W / 2
    # la palanca tiene la forma del arco de La Guarida: el corte que la suelta es el arco
    eje = arco_guarida()
    corte = eje.buffer(g.CORTE / 2, resolution=12)
    pal = Polygon(list(eje.coords))
    huecos = [
        prisma(dentro, Z0 - 1, MURO_H + 0.15),                                    # donde entra la base
        caja(-MEDIO + REPISA, MEDIO - REPISA, -0.2, CAJ_L, MURO_H, TECHO_Z),       # hueco de componentes
        caja(-BOCA, BOCA, PCB_L, Y1 + 5, Z0 - 1, Z1 + 1),                          # boca del USB
        prisma(pal.union(corte), TECHO_Z - 0.01, Z1 - g.PAL_T),                   # palanca más fina
        prisma(corte, TECHO_Z - 0.01, Z1 + 1),                                    # el corte: el arco
        cilindro(-xp - g.CORTE / 2, g.PAL_Y0, 0.6, TECHO_Z - 0.01, Z1 + 1),
        cilindro(xp + g.CORTE / 2, g.PAL_Y0, 0.6, TECHO_Z - 0.01, Z1 + 1),
        # ventana del diente: por ella se empuja para abrir
        caja(DIENTE_X[0] - 0.4, DIENTE_X[1] + 0.4, Y0 - 1, Y0 + FALDA + 0.1, -0.3, 1.5),
    ]
    pieza = restar(cuerpo, huecos)
    extras = [cilindro(TETON_X, TETON_Y, g.TETON_D / 2, g.TETON_Z, Z1 - g.PAL_T + 0.1)]
    yi = Y1 - FALDA                       # cara interior de la trasera: 24,2
    for s in (-1, 1):                     # uñas traseras: entran bajo el chaflán de la base
        a, b = sorted((s * (BOCA + 0.2), s * (EXT - FALDA + 0.1)))
        extras.append(cuna(a, b, [(yi + 0.1, Z0), (yi - 0.85, Z0), (yi + 0.1, Z0 + 0.95)]))
    return unir([pieza] + extras)


def galga():
    """Escalera: se apoya en la tira de pines, junto al botón; el escalón que enrasa da el alto."""
    return unir([caja(2.0 * i, 2.0 * i + 2.01, 0, 2.4, 0, 1.8 + 0.2 * i) for i in range(6)])


def placa_de_prueba():
    """La placa con sus botones y el USB, para comprobar choques."""
    return [caja(-9, 9, 0, PCB_L, 0, PCB_T),
            caja(TETON_X - 1.5, TETON_X + 1.5, TETON_Y - 2, TETON_Y + 2, PCB_T, PCB_T + g.BOTON_ALTO),
            caja(3.2 - 1.5, 3.2 + 1.5, TETON_Y - 2, TETON_Y + 2, PCB_T, PCB_T + g.BOTON_ALTO),
            caja(-4.5, 4.5, 16.5, 24.0, PCB_T, PCB_T + g.USB_ALTO)]


def numeros():
    L = BRAZO_X1 - sum(DIENTE_X) / 2
    d = DIENTE - JUEGO
    s = 3 * g.E_PLA * BRAZO_T * d / (2 * L ** 2)
    f = g.E_PLA * (MURO_H - Z0) * BRAZO_T ** 3 * d / (4 * L ** 3)
    return (g.numeros().rsplit("\n", 1)[0] +
            f"\n  brazo de cierre al poner la tapa: flecha {d:.2f} mm, {s:.0f} MPa (×{g.ROTURA_PLA / s:.1f}), {f:.1f} N")


def main():
    b, t, ga = base(), tapa(), galga()
    for n, m in (("base", b), ("tapa", t), ("galga", ga)):
        bb = m.bounds[1] - m.bounds[0]
        print(f"{n:6s} {bb[0]:.1f} × {bb[1]:.1f} × {bb[2]:.1f} mm · {m.volume / 1000 * 1.24:.1f} g · "
              f"cerrada {m.is_volume} · cuerpos {m.body_count}")
    choque = trimesh.boolean.intersection([b, t], engine="manifold").volume
    con_placa = sum(trimesh.boolean.intersection([unir([b, t]), p], engine="manifold").volume for p in placa_de_prueba())
    print(f"Choque base–tapa: {choque:.3f} mm³ · con la placa: {con_placa:.3f} mm³")
    print(numeros())

    trimesh.util.concatenate([b, t]).export(AQUI / "boton_modular_montado.stl")
    b.export(AQUI / "boton_modular_base.stl")
    ti = t.copy()                          # la tapa, boca abajo
    ti.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0]))
    ti.apply_translation([0, 0, -ti.bounds[0][2]])
    ti.export(AQUI / "boton_modular_tapa.stl")
    ga.export(AQUI / "boton_modular_galga.stl")

    # placa de impresión: tapa, base y galga, apoyadas en z = 0
    bi, gi = b.copy(), ga.copy()
    bi.apply_translation([27, 0, -bi.bounds[0][2]])
    gi.apply_translation([-27, 4, 0])
    try:
        import sys
        sys.path.insert(0, str(AQUI.parents[1] / "llaveros" / "st26" / "fuente"))
        from make_3mf import build_3mf, project_settings
        from make_a1 import miniatura
        aj = project_settings(
            "Bambu Lab A1 0.4 nozzle", "0.20mm Standard @BBL A1", "Bambu PLA Basic @BBL A1", ["#F2EFE6"],
            {"curr_bed_type": "Textured PEI Plate", "wall_loops": "4", "sparse_infill_density": "100%",
             "enable_support": "0", "brim_type": "no_brim"})
        partes = [("tapa", ti, 1), ("base", bi, 1), ("galga", gi, 1)]
        build_3mf(str(AQUI / "boton_modular.3mf"), "boton claude modular", partes, aj, (128.0, 128.0),
                  miniatura([(m, "#F2EFE6") for _, m, _ in partes], [(128.0, 128.0)]))
        print("Proyecto A1: boton_modular.3mf")
    except Exception as e:
        print(f"Proyecto A1 NO escrito: {e}")


if __name__ == "__main__":
    main()
