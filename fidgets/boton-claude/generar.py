#!/usr/bin/env python3
"""Botón Claude — funda de una pieza para un ESP32-C3 Super Mini.

La placa entra deslizando por detrás (el lado del USB) y queda cogida por dos pestañas.
El techo lleva una palanca recortada en U con un tetón que pulsa el botón BOOT.

Marco del modelo (montado): x a lo ancho (0 en el centro), y a lo largo (0 = cara interior
del frente; el USB queda en +y), z hacia arriba (0 = suelo interior, donde apoya la placa).
Se imprime BOCA ABAJO: el techo y la palanca sobre la placa PEI.

Uso: python3 generar.py  -> boton_claude.stl, boton_claude.3mf (proyecto A1) y los números.
"""
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import box as rect
from shapely.ops import unary_union

AQUI = Path(__file__).parent

# === Placa (mm). De dónde sale cada dato: APRENDIZAJES.md ===
PCB_W = 18.0          # ancho (fichas)
PCB_L = 22.5          # largo (fichas)
PCB_T = 1.0           # grosor (ficha ambigua: 0,8–1,2)
BOOT_X = 5.6          # centro de BOOT desde el borde largo izquierdo (medido en foto, ±0,5)
BOOT_USB = 8.7        # centro de BOOT desde el borde del USB (medido en foto, ±0,5)
BOTON_ALTO = 2.25     # alto del pulsador sobre la placa (supuesto: 2,0–2,5)
USB_ALTO = 3.2        # alto del conector USB-C sobre la placa

# === Funda ===
HOLGURA = 0.2         # por lado, entre placa y pared
PARED = 1.6           # 4 líneas de 0,4
SUELO = 1.0
TECHO = 1.6
RANURA_H = 1.4        # alto del carril de la placa (placa 1,0 + margen para el puente)
REPISA = 0.8          # lo que tapa la repisa sobre la fila de pines, por lado
TECHO_Z = 4.8         # cara interior del techo (USB a 4,2 + 0,6)

# === Palanca ===
PAL_T = 1.0           # grosor de la palanca (5 capas)
PAL_W = 11.0          # ancho
PAL_Y0 = 1.0          # raíz (bisagra), cerca del frente
PAL_Y1 = 17.5         # punta
CORTE = 0.7           # ancho del corte en U
TETON_D = 3.0         # diámetro del tetón: cubre ±0,7 mm de error en la posición de BOOT
TETON_Z = 3.7         # cara inferior del tetón. Si el botón queda pulsado, subir; si no llega, bajar

# === Pestañas que retienen la placa ===
PEST_Y0 = 14.0        # dónde empiezan (ahí acaban suelo y repisas)
PEST_Y1 = PCB_L + 1.7 # sobresalen por detrás, a los lados del conector del cable
LABIO = 0.6           # labio bajo la placa en las pestañas
DIENTE = 0.45         # lo que entra el diente tras el borde de la placa

# === Material: PLA ===
E_PLA = 2300.0        # MPa
ROTURA_PLA = 55.0     # MPa

MEDIO = PCB_W / 2 + HOLGURA            # media anchura del carril: 9,2
EXT = MEDIO + PARED                    # media anchura exterior: 10,8
TETON_X = BOOT_X - PCB_W / 2           # -3,4
TETON_Y = PCB_L - BOOT_USB             # 13,8
Z0, Z1 = -SUELO, TECHO_Z + TECHO       # -1,0 … 6,4
LEJOS = 40.0


def caja(x0, x1, y0, y1, z0, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


def cilindro(x, y, r, z0, z1):
    m = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=48)
    m.apply_translation([x, y, (z0 + z1) / 2])
    return m


def unir(ms):
    return trimesh.boolean.union(ms, engine="manifold")


def restar(a, bs):
    return trimesh.boolean.difference([a, unir(bs)], engine="manifold")


def funda():
    # contorno: esquinas del frente redondeadas (r 1,5); las pestañas acaban rectas
    frente = rect(-EXT, -PARED, EXT, 4).buffer(-1.5).buffer(1.5, resolution=12)
    planta = unary_union([frente, rect(-EXT, 1.5, EXT, PEST_Y1)])
    cuerpo = trimesh.creation.extrude_polygon(planta, Z1 - Z0)
    cuerpo.apply_translation([0, 0, Z0])

    xp = PAL_W / 2
    huecos = [
        caja(-MEDIO, MEDIO, 0, LEJOS, 0, RANURA_H),                               # carril de la placa
        caja(-MEDIO + REPISA, MEDIO - REPISA, 0, LEJOS, RANURA_H - 0.01, TECHO_Z),  # hueco de componentes
        caja(-MEDIO, MEDIO, PEST_Y0, LEJOS, 0, TECHO_Z),                          # pestañas sin repisa
        caja(-MEDIO, MEDIO, PCB_L, LEJOS, TECHO_Z - 0.01, Z1 + 1),                # el techo acaba con la placa
        caja(-MEDIO, MEDIO, PEST_Y0, LEJOS, Z0 - 1, 0.01),                        # el suelo acaba en las pestañas
        # cortes que sueltan las pestañas del techo
        caja(-MEDIO, -MEDIO + CORTE, PEST_Y0, LEJOS, TECHO_Z - 0.01, Z1 + 1),
        caja(MEDIO - CORTE, MEDIO, PEST_Y0, LEJOS, TECHO_Z - 0.01, Z1 + 1),
        # la palanca es más fina que el techo
        caja(-xp, xp, PAL_Y0, PAL_Y1, TECHO_Z - 0.01, Z1 - PAL_T),
        # corte en U
        caja(-xp - CORTE, -xp, PAL_Y0, PAL_Y1 + CORTE, TECHO_Z - 0.01, Z1 + 1),
        caja(xp, xp + CORTE, PAL_Y0, PAL_Y1 + CORTE, TECHO_Z - 0.01, Z1 + 1),
        caja(-xp - CORTE, xp + CORTE, PAL_Y1, PAL_Y1 + CORTE, TECHO_Z - 0.01, Z1 + 1),
        # taladros de alivio donde nace el corte: sin esquina viva en la raíz de la palanca
        cilindro(-xp - CORTE / 2, PAL_Y0, 0.6, TECHO_Z - 0.01, Z1 + 1),
        cilindro(xp + CORTE / 2, PAL_Y0, 0.6, TECHO_Z - 0.01, Z1 + 1),
    ]
    pieza = restar(cuerpo, huecos)

    extras = [cilindro(TETON_X, TETON_Y, TETON_D / 2, TETON_Z, Z1 - PAL_T + 0.1)]
    for s in (-1, 1):
        a, b = sorted((s * MEDIO, s * (MEDIO - LABIO)))
        extras.append(caja(a, b, PEST_Y0 + 0.3, PCB_L, Z0, 0))           # labio bajo la placa
        # diente: cara recta contra la placa, rampa hacia atrás (entrada) y hacia arriba (para imprimir)
        y0, y1 = PCB_L + 0.25, PEST_Y1
        xw, xd = s * (MEDIO + 0.1), s * (MEDIO - DIENTE)
        pts = [[xw, y0, 0], [xw, y1, 0], [xw, y0, RANURA_H], [xw, y1, RANURA_H],
               [xd, y0, 0], [xd, y0, RANURA_H - 0.5], [xd, y0 + 0.3, 0], [xd, y0 + 0.3, RANURA_H - 0.5]]
        extras.append(trimesh.convex.convex_hull(np.array(pts)))
    return unir([pieza] + extras)


def numeros():
    """Tensión y fuerza en la palanca y en las pestañas (viga en voladizo)."""
    L = TETON_Y - PAL_Y0
    out = []
    for nombre, alto in (("botón alto (2,5)", 2.5), ("botón nominal (2,25)", BOTON_ALTO), ("botón bajo (2,0)", 2.0)):
        juego = TETON_Z - (PCB_T + alto)
        d = juego + 0.25                                   # juego + recorrido del pulsador
        s = 3 * E_PLA * PAL_T * d / (2 * L ** 2)
        f = E_PLA * PAL_W * PAL_T ** 3 * d / (4 * L ** 3)
        out.append(f"  palanca, {nombre}: juego {juego:.2f} mm, flecha {d:.2f} mm, "
                   f"{s:.0f} MPa (×{ROTURA_PLA / s:.1f}), {f:.1f} N + pulsador")
    Lp = PCB_L + 0.25 - PEST_Y0
    d = DIENTE - HOLGURA
    s = 3 * E_PLA * PARED * d / (2 * Lp ** 2)
    f = E_PLA * (Z1 - Z0) * PARED ** 3 * d / (4 * Lp ** 3)
    out.append(f"  pestaña al meter la placa: flecha {d:.2f} mm, {s:.0f} MPa (×{ROTURA_PLA / s:.1f}), {f:.1f} N por lado")
    return "\n".join(out)


def proyecto_a1(malla, ruta):
    """Proyecto de Bambu Studio para la A1: PLA, 0,20 mm, PEI texturizada, sin soportes."""
    sys.path.insert(0, str(AQUI.parents[1] / "llaveros" / "st26" / "fuente"))
    from make_3mf import build_3mf, project_settings
    from make_a1 import miniatura
    ajustes = project_settings(
        "Bambu Lab A1 0.4 nozzle", "0.20mm Standard @BBL A1", "Bambu PLA Basic @BBL A1", ["#F2EFE6"],
        {"curr_bed_type": "Textured PEI Plate", "wall_loops": "4", "sparse_infill_density": "100%",
         "enable_support": "0", "brim_type": "no_brim"})
    centro = (128.0, 128.0)
    build_3mf(str(ruta), "boton claude", [("funda", malla, 1)], ajustes, centro,
              miniatura([(malla, "#F2EFE6")], [centro]))


def main():
    montada = funda()
    # para imprimir: boca abajo (techo en la placa) y apoyada en z = 0
    imprimir = montada.copy()
    imprimir.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0]))
    imprimir.apply_translation([0, 0, -imprimir.bounds[0][2]])
    imprimir.export(AQUI / "boton_claude.stl")
    montada.export(AQUI / "boton_claude_montada.stl")

    bb = montada.bounds[1] - montada.bounds[0]
    print(f"Medidas (mm): {bb[0]:.1f} × {bb[1]:.1f} × {bb[2]:.1f}")
    print(f"Volumen:   {montada.volume / 1000:.2f} cm³  (~{montada.volume / 1000 * 1.24:.1f} g macizo)")
    print(f"Cerrada:   {montada.is_volume}   cuerpos: {montada.body_count}")
    print(numeros())
    try:
        proyecto_a1(imprimir, AQUI / "boton_claude.3mf")
        print("Proyecto A1: boton_claude.3mf")
    except Exception as e:  # sin red no se pueden bajar los perfiles
        print(f"Proyecto A1 NO escrito: {e}")


if __name__ == "__main__":
    main()
