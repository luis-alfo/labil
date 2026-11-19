"""larc hq: cajonera colgada del elevador de pantalla. Regenera piezas, GLB y descargas.

La fuente de verdad es `larc_hq.scad`. Este script lo pasa por OpenSCAD y escribe:

  - pieza_A_carcasa.stl, pieza_B_cajon_a5.stl, pieza_C_cajon_pequeno.stl, prueba_pinza.stl
    (orientación de impresión)
  - docs/models/larc_hq_cerrada.glb   colgada del elevador, con el portátil debajo
  - docs/models/larc_hq_abierta.glb   con los cajones abiertos y su contenido
  - docs/models/larc_hq_placa.glb     la carcasa de pie en la placa de la A1
  - docs/models/larc_hq_prueba_pinza.glb
  - docs/files/larc-hq/               descargas (STL, SCAD, notas)

Si OpenSCAD no está instalado no regenera nada y deja los ficheros como están.
"""

import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, box as sbox
from trimesh.transformations import rotation_matrix

HERE = Path(__file__).resolve().parent
SCAD = HERE / "larc_hq.scad"
REPO = HERE.parents[1]
WEB_DIR = REPO / "docs" / "models"
FILES_DIR = REPO / "docs" / "files" / "larc-hq"

# Deben coincidir con el .scad
BOARD_T, BOARD_DEPTH, FREE_H = 12.0, 225.0, 85.0
# Elevador, solo para el contexto del visor (estimado en las fotos, no condiciona las piezas)
TOP_FLAT, FEET_OUT, BEND_R = 300.0, 512.0, 45.0
OPEN = 150.0   # cuánto salen los cajones en la vista «abierta»

PRINT_PARTS = {
    "A": "pieza_A_carcasa.stl",
    "B": "pieza_B_cajon_a5.stl",
    "C": "pieza_C_cajon_pequeno.stl",
    "T": "prueba_pinza.stl",
}

COLORS = {               # RGBA 0–1
    "A": (0.30, 0.31, 0.33, 1.0),
    "B": (0.80, 0.80, 0.78, 1.0),
    "C": (0.80, 0.80, 0.78, 1.0),
    "madera": (0.70, 0.47, 0.25, 1.0),
    "mesa": (0.93, 0.93, 0.92, 1.0),
    "portatil": (0.78, 0.78, 0.76, 1.0),
    "monitor": (0.20, 0.21, 0.23, 1.0),
    "boli": (0.14, 0.91, 0.14, 1.0),
    "papel": (0.98, 0.98, 0.96, 1.0),
    "cargador": (0.97, 0.97, 0.97, 1.0),
    "placa": (0.20, 0.20, 0.22, 1.0),
}


def openscad(part, out):
    subprocess.run(["openscad", "-q", "-D", f'part="{part}"', "-o", str(out), str(SCAD)], check=True)
    mesh = trimesh.load(out)
    if not mesh.is_volume:
        sys.exit(f"{out.name}: la malla no es un sólido cerrado")
    return mesh


def painted(mesh, key, metallic=0.0, roughness=0.6):
    mesh = mesh.copy()
    mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        baseColorFactor=COLORS[key], metallicFactor=metallic, roughnessFactor=roughness))
    return mesh


def export_glb(meshes, name):
    """Escena en metros y con Y hacia arriba (glTF): así el AR sale a tamaño real."""
    scene = trimesh.Scene()
    for i, m in enumerate(meshes):
        scene.add_geometry(m, geom_name=f"{name}_{i}")
    scene.apply_transform(rotation_matrix(-np.pi / 2, [1, 0, 0]))
    scene.apply_scale(0.001)
    scene.export(WEB_DIR / name)


def caja(x0, x1, y0, y1, z0, z1):
    return trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])


def redondear(pts, r, n=16):
    """Polilínea con las esquinas interiores sustituidas por arcos de radio r."""
    pts = [np.array(p, float) for p in pts]
    out = [pts[0]]
    for a, p, b in zip(pts, pts[1:], pts[2:]):
        u, v = (a - p) / np.linalg.norm(a - p), (b - p) / np.linalg.norm(b - p)
        half = np.arccos(np.clip(u @ v, -1, 1)) / 2
        d = r / np.tan(half)
        centro = p + (u + v) / np.linalg.norm(u + v) * r / np.sin(half)
        a0, a1 = p + u * d - centro, p + v * d - centro
        t0, t1 = np.arctan2(a0[1], a0[0]), np.arctan2(a1[1], a1[0])
        dt = (t1 - t0 + np.pi) % (2 * np.pi) - np.pi
        out += [centro + r * np.array([np.cos(t0 + dt * i / n), np.sin(t0 + dt * i / n)]) for i in range(n + 1)]
    return out + [pts[-1]]


def elevador():
    """Contrachapado curvado: tablero plano, dos curvas y dos patas abiertas hasta la mesa."""
    zc = BOARD_T / 2
    pie = (FEET_OUT / 2 - 8, -FREE_H - 10)
    eje = LineString(redondear([(-pie[0], pie[1]), (-TOP_FLAT / 2 - 28, zc),
                                (TOP_FLAT / 2 + 28, zc), pie], BEND_R))
    perfil = eje.buffer(zc, cap_style=2, join_style=1).intersection(sbox(-400, -FREE_H, 400, 60))
    m = trimesh.creation.extrude_polygon(perfil, BOARD_DEPTH)           # (x, z) -> extruido en y
    m.apply_transform(rotation_matrix(np.pi / 2, [1, 0, 0]))            # y_perfil -> z
    m.apply_translation([0, BOARD_DEPTH, 0])
    return m


def contexto():
    mesa = caja(-290, 290, -200, 250, -FREE_H - 20, -FREE_H)
    portatil = caja(-152, 152, -175, 40, -FREE_H, -FREE_H + 11.5)
    pie = caja(-125, 125, 45, 215, BOARD_T, BOARD_T + 6)
    cuello = trimesh.creation.cylinder(radius=38, height=110, sections=64)
    cuello.apply_translation([0, 165, BOARD_T + 6 + 55])
    return [painted(elevador(), "madera", roughness=0.7), painted(mesa, "mesa", roughness=0.5),
            painted(portatil, "portatil", metallic=0.6, roughness=0.35),
            painted(pie, "monitor", roughness=0.5), painted(cuello, "monitor", roughness=0.5)]


def bolis():
    out = []
    for y in (7.5, 19.0):
        b = trimesh.creation.cylinder(radius=5.2, height=142, sections=32)
        b.apply_transform(rotation_matrix(np.pi / 2, [0, 1, 0]))
        b.apply_translation([0, y, BOARD_T + 0.4 + 2.4 + 5.2])
        out.append(painted(b, "boli", roughness=0.4))
    return out


def main():
    if not shutil.which("openscad"):
        print("OpenSCAD no está instalado: se mantienen los STL/GLB ya generados.")
        return
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)

    printed = {}
    for part, fname in PRINT_PARTS.items():
        printed[part] = m = openscad(part, HERE / fname)
        print(f"{fname}: {np.round(m.extents, 1)} mm · {m.volume / 1000:.1f} cm³ · sólido={m.is_volume}")

    with tempfile.TemporaryDirectory() as tmp:
        use = {k: openscad(f"{k}_use", Path(tmp) / f"{k}.stl") for k in "ABC"}
    env = contexto()
    export_glb(env + [painted(use[k], k) for k in "ABC"] + bolis(), "larc_hq_cerrada.glb")

    abiertos = []
    for k in "BC":
        m = use[k].copy()
        m.apply_translation([0, -OPEN, 0])
        abiertos.append(painted(m, k))
    b0 = use["B"].bounds
    papel = caja(b0[0][0] + 5, b0[0][0] + 5 + 148, -OPEN - 1, -OPEN + 209, -40, -35)   # A5
    c0 = use["C"].bounds
    cargador = caja(c0[0][0] + 5, c0[0][0] + 80, -OPEN + 100, -OPEN + 175, -40, -12)
    export_glb(env + [painted(use["A"], "A")] + abiertos + bolis()
               + [painted(papel, "papel", roughness=0.9), painted(cargador, "cargador", roughness=0.4)],
               "larc_hq_abierta.glb")

    placa = caja(0, 256, 0, 256, -1.5, 0)
    a = printed["A"].copy()
    c = (a.bounds[0] + a.bounds[1]) / 2
    a.apply_translation([128 - c[0], 128 - c[1], -a.bounds[0][2]])
    export_glb([painted(placa, "placa", roughness=0.8), painted(a, "A")], "larc_hq_placa.glb")

    t = printed["T"].copy()
    t.apply_translation([-t.bounds[0][0], -t.bounds[0][1], 0])
    export_glb([painted(t, "A")], "larc_hq_prueba_pinza.glb")

    for f in [*PRINT_PARTS.values(), SCAD.name, "APRENDIZAJES.md"]:
        if (HERE / f).exists():
            shutil.copy(HERE / f, FILES_DIR / f)

    (WEB_DIR / "version.txt").write_text(str(int(time.time())))
    print("GLB y descargas actualizados.")


if __name__ == "__main__":
    main()
