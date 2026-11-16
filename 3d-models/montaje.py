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
    salida = {"orden": [k for k in ORDEN if k in piezas], "piezas": piezas,
              "desplazamiento": d.T.flatten().round(6).tolist(), "contexto": contexto}
    (MODELOS / "el_secadero_v2_montaje.json").write_text(json.dumps(salida) + "\n")


if __name__ == "__main__":
    main()
