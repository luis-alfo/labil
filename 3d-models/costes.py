#!/usr/bin/env python3
"""Coste de filamento de cada pieza a partir de su 3MF o STL.

Un laminador simplificado con el perfil de la A1 (`perfiles/perfil_estimacion_a1_pla.ini`):
corta la malla en capas de 0,2 mm y, en cada capa, separa
  - pared: 4 líneas de 0,42 mm (1,68 mm hacia dentro del contorno). El perfil tiene
    2 perímetros, pero con 2 el cálculo se queda corto: el laminador real añade
    relleno de huecos y solapes en piezas finas. Con 4 líneas coincide con él
    (error medio 4 %, máximo 9 % en las 8 piezas de referencia).
  - relleno macizo: lo que no tiene pieza encima en las 5 capas siguientes (techo)
    o debajo en las 3 anteriores (suelo),
  - relleno disperso: el resto, al 15 %.
gramos = volumen extruido × 1,26 g/cm³ × CALIBRADO; coste = gramos × 20 €/kg.

CALIBRADO ajusta el resultado a los gramos que dio el laminador de verdad en piezas
de este repo (ver `REFERENCIAS`). El script imprime el error de cada referencia.

Uso:  python3 3d-models/costes.py --calibrar     → compara con las referencias
      python3 3d-models/costes.py pieza.stl ...  → gramos y euros de cada archivo
La web usa gramos() desde 3d-models/web.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon

RAIZ = Path(__file__).resolve().parents[1]

# === Perfil (A1 0.4 · 0.20 mm Standard · PLA Basic) ===
CAPA = 0.20          # mm
PERIMETROS = 4       # pared efectiva (ver arriba), no los perímetros del perfil
ANCHO_LINEA = 0.42   # mm
CAPAS_TECHO = 5
CAPAS_SUELO = 3
RELLENO = 0.15
DENSIDAD = 1.26      # g/cm³ (PLA)
EUROS_KG = 20.0      # precio del plástico que fija Luis
CALIBRADO = 1.03     # de --calibrar (16 nov 2026)

# Gramos que dio un laminador con este perfil (APRENDIZAJES.md de cada diseño).
REFERENCIAS = {
    "3d-models/el-secadero-v2/pieza_A_brazo.stl": 15.8,
    "3d-models/el-secadero-v2/pieza_K_cuna_apriete.stl": 2.5,
    "3d-models/el-secadero-v2/pieza_B_marco.stl": 14.4,
    "3d-models/el-secadero-v2/pieza_C_cuna.stl": 11.2,
    "3d-models/_borradores/estropajero-v4/pieza_A_brazo.stl": 16.8,
    "3d-models/_borradores/estropajero-v4/pieza_K_llave.stl": 1.7,
    "3d-models/_borradores/estropajero-v4/pieza_B_colgador.stl": 8.6,
    "3d-models/_borradores/estropajero-v4/pieza_C_bandeja.stl": 17.8,
}


def cargar(ruta: Path) -> trimesh.Trimesh:
    m = trimesh.load(ruta, force="mesh")
    m.apply_translation([0, 0, -m.bounds[0][2]])  # apoyada en la cama
    return m


def gramos(malla: trimesh.Trimesh) -> float:
    alto = malla.bounds[1][2]
    n = max(1, int(np.ceil(alto / CAPA)))
    alturas = (np.arange(n) + 0.5) * CAPA
    capas = []
    for z in alturas:
        s = malla.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if s is None:
            capas.append(Polygon())
            continue
        polys = []
        for p in s.discrete:
            if len(p) >= 4:
                polys.append(Polygon(p[:, :2]))
        # regla par-impar: los agujeros son polígonos dentro de otros
        geo = Polygon()
        for p in sorted(polys, key=lambda q: -q.area):
            geo = geo.symmetric_difference(p.buffer(0))
        capas.append(geo.buffer(0))

    pared = PERIMETROS * ANCHO_LINEA
    vol = 0.0
    for i, capa in enumerate(capas):
        if capa.is_empty:
            continue
        interior = capa.buffer(-pared)
        perim = capa.area - interior.area
        arriba = capas[i + 1:i + 1 + CAPAS_TECHO]
        abajo = capas[max(0, i - CAPAS_SUELO):i]
        cubierto_arriba = interior
        if len(arriba) < CAPAS_TECHO:
            cubierto_arriba = Polygon()
        else:
            for c in arriba:
                cubierto_arriba = cubierto_arriba.intersection(c)
        cubierto_abajo = interior
        if len(abajo) < CAPAS_SUELO:
            cubierto_abajo = Polygon()
        else:
            for c in abajo:
                cubierto_abajo = cubierto_abajo.intersection(c)
        disperso = cubierto_arriba.intersection(cubierto_abajo)
        macizo = interior.area - disperso.area
        vol += CAPA * (perim + macizo + RELLENO * disperso.area)
    return vol / 1000.0 * DENSIDAD * CALIBRADO


def calibrar() -> float:
    filas = []
    for ruta, real in REFERENCIAS.items():
        g = gramos(cargar(RAIZ / ruta))
        filas.append((ruta, real, g))
    k = sum(r for _, r, _ in filas) / sum(g for _, _, g in filas)
    for ruta, real, g in filas:
        print(f"{Path(ruta).parent.name:>16}/{Path(ruta).name:<26} laminador {real:5.1f} g · "
              f"estimado {g:5.1f} g · calibrado {g*k:5.1f} g ({(g*k-real)/real:+.0%})")
    print(f"factor de calibrado: {k:.3f}")
    return k


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] != "--calibrar":
        for ruta in sys.argv[1:]:
            g = gramos(cargar(Path(ruta)))
            print(f"{g:7.1f} g  {g * EUROS_KG / 1000:5.2f} €  {ruta}")
        return
    calibrar()


if __name__ == "__main__":
    main()
