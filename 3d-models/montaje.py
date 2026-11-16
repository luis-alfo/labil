"""Transformaciones de la placa de impresión al objeto montado (El Secadero v2).

La portada de la web imprime la placa real (el_secadero_v2_placa.glb) y luego hace que
cada pieza salga de la placa y vaya a su sitio montado (el_secadero_v2_abajo.glb).
Para eso hace falta, por pieza, la transformación rígida placa → montaje, en el
sistema de coordenadas crudo de los GLB (mm, z arriba).

- PCA para orientar (las 4 combinaciones de signo con giro propio) + ICP punto a punto
  con árbol KD (scipy). Sin rtree, que CI no instala. Los vértices no salen en el
  mismo orden en los dos GLB, así que no vale emparejarlos por índice.

Escribe docs/models/el_secadero_v2_montaje.json (matrices 4×4 por columnas, como three.js).
"""
from __future__ import annotations

import itertools
import json
import math
import re
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree

RAIZ = Path(__file__).resolve().parents[1]
MODELOS = RAIZ / "docs" / "models"
CAMA = (51, 51, 56)
NOMBRES = {(140, 145, 153): "A", (204, 199, 186): "B", (247, 245, 237): "C", (102, 107, 115): "K"}
ORDEN = ["A", "K", "B", "C"]  # orden de montaje: brazo, cuña, marco, cuna
CONTEXTO = {(242, 237, 227): "encimera", (41, 41, 43): "fregadero", (209, 214, 222): "cromo",
            (245, 214, 51): "estropajo"}


def _color(g) -> tuple:
    return tuple(int(v) for v in g.visual.material.baseColorFactor[:3])


def _kabsch(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ca, cb = a.mean(0), b.mean(0)
    u, _, vt = np.linalg.svd((a - ca).T @ (b - cb))
    d = np.sign(np.linalg.det(vt.T @ u.T))
    r = vt.T @ np.diag([1, 1, d]) @ u.T
    m = np.eye(4); m[:3, :3] = r; m[:3, 3] = cb - r @ ca
    return m


def _icp(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, float]:
    arbol = cKDTree(b)
    ca, cb = a.mean(0), b.mean(0)
    _, va = np.linalg.eigh(np.cov((a - ca).T)); _, vb = np.linalg.eigh(np.cov((b - cb).T))
    mejor = (None, np.inf)
    for signos in itertools.product([1, -1], repeat=3):
        r = vb @ np.diag(signos) @ va.T
        if np.linalg.det(r) < 0:
            continue
        m = np.eye(4); m[:3, :3] = r; m[:3, 3] = cb - r @ ca
        for _ in range(60):
            t = trimesh.transform_points(a, m)
            _, idx = arbol.query(t)
            m = _kabsch(a, b[idx])
        d, _ = arbol.query(trimesh.transform_points(a, m))
        if d.mean() < mejor[1]:
            mejor = (m, float(d.mean()))
    return mejor


SCAD = RAIZ / "3d-models" / "el-secadero-v2" / "el_secadero_v2.scad"
GENERADOR = RAIZ / "3d-models" / "el-secadero-v2" / "generate_stl.py"


def _param(texto: str, nombre: str) -> float:
    return float(re.search(rf"^\s*{nombre}\s*=\s*([-\d.]+)", texto, re.M).group(1))


def movimientos() -> dict:
    """Movimientos reales del montaje (APRENDIZAJES.md de el-secadero-v2), en mm, z arriba:
    A se desliza hacia la pared hasta abrazar la columna · K baja desde arriba ·
    B entra inclinado hk_ang° hacia fuera por el enganche y cae a vertical ·
    C entra a slot_ang° por las ranuras y baja hasta horizontal · el estropajo cae en la cuna.
    Los puntos de giro salen de las mismas fórmulas que el .scad."""
    scad, gen = SCAD.read_text(), GENERADOR.read_text()
    p = lambda n: _param(scad, n)
    sponge = [float(v) for v in re.search(r"^\s*sponge\s*=\s*\[([^\]]+)\]", scad, re.M).group(1).split(",")]
    in_y = sponge[1] + 6
    cr_y = in_y / 2 + p("wall")
    fin_y1 = cr_y + p("fin_clr") + p("fin_t")
    sag = p("sink_d") / 2 - math.sqrt((p("sink_d") / 2) ** 2 - fin_y1 ** 2)
    frame_x0 = max(7, p("sink_wall_x") + sag + 0.1)
    hx, hz = frame_x0 + p("hk_len") / 2, p("hk_floor") + p("hk_r")
    x_axis, z_axis = (float(v) for v in re.search(r"X_AXIS, Z_AXIS, FOLD_REST = ([-\d.]+), ([-\d.]+)", gen).groups())
    return {
        "A": {"tipo": "desliza", "desde": [70, 0, 0]},
        "K": {"tipo": "desliza", "desde": [0, 0, 45]},
        "B": {"tipo": "gira", "punto": [hx, 0, hz], "angulo": -p("hk_ang"), "entrada": [0, 0, 30]},
        "C": {"tipo": "gira", "punto": [x_axis, 0, z_axis], "angulo": -p("slot_ang"), "entrada": [0, 0, 30]},
        "estropajo": {"tipo": "desliza", "desde": [0, 0, 110]},
    }


def main() -> None:
    placa = trimesh.load(MODELOS / "el_secadero_v2_placa.glb")
    abajo = trimesh.load(MODELOS / "el_secadero_v2_abajo.glb")
    destino = {NOMBRES[_color(g)]: g for g in abajo.geometry.values() if _color(g) in NOMBRES}
    piezas = {}
    for g in placa.geometry.values():
        c = _color(g)
        if c == CAMA or c not in NOMBRES:
            continue
        k = NOMBRES[c]; gb = destino[k]
        # aunque tengan el mismo número de vértices, el orden no coincide: siempre ICP
        m, err = _icp(np.asarray(g.vertices), np.asarray(gb.vertices))
        piezas[k] = {"color": list(c), "matriz": m.T.flatten().round(6).tolist(), "error_mm": round(err, 3)}
        print(f"pieza {k}: error medio {err:.3f} mm")
    # desplazamiento: el objeto montado se coloca centrado sobre la placa (x, y) y apoyado en z = 0
    caja = np.vstack([trimesh.transform_points(destino[k].vertices, np.eye(4)) for k in piezas])
    cama = next(g for g in placa.geometry.values() if _color(g) == CAMA)
    centro_cama = cama.bounds.mean(0)
    d = np.eye(4); d[0, 3] = centro_cama[0] - caja[:, 0].mean(); d[1, 3] = centro_cama[1] - caja[:, 1].mean()
    d[2, 3] = 40 - caja[:, 2].min()  # 40 mm por encima de la placa: «sale de la placa»
    contexto = [{"nombre": CONTEXTO[_color(g)], "color": list(_color(g))}
                for g in abajo.geometry.values() if _color(g) in CONTEXTO]
    salida = {"orden": [k for k in ORDEN if k in piezas], "piezas": piezas, "movimientos": movimientos(),
              "desplazamiento": d.T.flatten().round(6).tolist(), "contexto": contexto}
    (MODELOS / "el_secadero_v2_montaje.json").write_text(json.dumps(salida) + "\n")


if __name__ == "__main__":
    main()
