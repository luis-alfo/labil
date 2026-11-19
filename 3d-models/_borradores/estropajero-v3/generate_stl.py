"""Soporte de estropajo V3: regenera piezas, placa 3MF para la A1 y los GLB del visor.

La fuente de verdad del modelo es `estropajero_v3.scad` (paramétrico). Este
script lo pasa por OpenSCAD y prepara todo lo demás:

  - pieza_A.stl, pieza_B_bastidor.stl, pieza_C_bandeja.stl  (orientación de impresión)
  - docs/models/estropajero_v3_abajo.glb       montado, bandeja abajo
  - docs/models/estropajero_v3_levantada.glb   montado, bandeja levantada
  - docs/models/estropajero_v3_placa.glb       las 3 piezas en la placa de la A1
  - docs/files/estropajero-v3/                 descargas (STL, 3MF A1, SCAD, notas)

Si OpenSCAD no está instalado no regenera nada y deja los ficheros como están.
"""

import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix

HERE = Path(__file__).resolve().parent
SCAD = HERE / "estropajero_v3.scad"
REPO = HERE.parents[1]
WEB_DIR = REPO / "docs" / "models"
FILES_DIR = REPO / "docs" / "files" / "estropajero-v3"

# Deben coincidir con los parámetros del .scad (eje de la bisagra y su tope)
X_AXIS, Z_AXIS, FOLD_MAX = 24.0, -69.0, 95.0

PRINT_PARTS = {          # part= del .scad -> STL de impresión
    "A": "pieza_A.stl",
    "B": "pieza_B_bastidor.stl",
    "C": "pieza_C_bandeja.stl",
}
# Placa de la A1 (256 × 256 mm): nombre, STL, giro en Z, centro XY
PLATE = [
    ("A - Pinza y brazo", "pieza_A.stl", 90, (48, 128)),
    ("B - Bastidor (de pie)", "pieza_B_bastidor.stl", 0, (124, 128)),
    ("C - Bandeja rejilla", "pieza_C_bandeja.stl", 0, (200, 128)),
]

COLORS = {               # RGBA 0–1, PBR simple
    "A": (0.55, 0.57, 0.60, 1.0),
    "B": (0.80, 0.78, 0.73, 1.0),
    "C": (0.97, 0.96, 0.93, 1.0),
    "encimera": (0.95, 0.93, 0.89, 1.0),
    "cromo": (0.82, 0.84, 0.87, 1.0),
    "placa": (0.20, 0.20, 0.22, 1.0),
}


def openscad(part, out):
    subprocess.run(["openscad", "-q", "-D", f'part="{part}"', "-o", str(out), str(SCAD)],
                   check=True)
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


def context():
    """Trozo de encimera con el hueco redondo del fregadero (Ø 400) + grifo."""
    slab = trimesh.creation.box(bounds=[[-100, -65, -20], [30, 65, 0]])
    hole = trimesh.creation.cylinder(radius=200, height=60, sections=180)
    hole.apply_translation([200, 0, -10])
    slab = trimesh.boolean.difference([slab, hole], engine="manifold")
    flange = trimesh.creation.cylinder(radius=27, height=8, sections=96)
    flange.apply_translation([-68, 0, 4])
    column = trimesh.creation.cylinder(radius=23, height=45, sections=96)
    column.apply_translation([-68, 0, 22.5])
    return [painted(slab, "encimera", roughness=0.4),
            painted(flange, "cromo", metallic=1.0, roughness=0.25),
            painted(column, "cromo", metallic=1.0, roughness=0.25)]


def plate_layout():
    placed = []
    for _, fname, rz, (cx, cy) in PLATE:
        m = trimesh.load(HERE / fname)
        if rz:
            m.apply_transform(rotation_matrix(np.radians(rz), [0, 0, 1]))
        c = (m.bounds[0] + m.bounds[1]) / 2
        m.apply_translation([cx - c[0], cy - c[1], -m.bounds[0, 2]])
        placed.append(m)
    return placed


def write_3mf(path):
    """3MF estándar con las 3 piezas ya colocadas en la placa de la A1."""
    objs, items = [], []
    for i, ((name, *_), m) in enumerate(zip(PLATE, plate_layout()), 1):
        v = "\n".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in m.vertices)
        t = "\n".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
        objs.append(f'<object id="{i}" name="{name}" type="model"><mesh>'
                    f"<vertices>\n{v}\n</vertices><triangles>\n{t}\n</triangles></mesh></object>")
        items.append(f'<item objectid="{i}" printable="1"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="es-ES" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
             '<metadata name="Title">Soporte estropajo V3</metadata>\n'
             f'<resources>\n{chr(10).join(objs)}\n</resources>\n'
             f'<build>\n{chr(10).join(items)}\n</build>\n</model>')
    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                     '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def main():
    if not shutil.which("openscad"):
        print("OpenSCAD no está instalado: se mantienen los STL/GLB ya generados.")
        return
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)

    for part, fname in PRINT_PARTS.items():
        m = openscad(part, HERE / fname)
        print(f"{fname}: {np.round(m.extents, 1)} mm · {m.volume / 1000:.1f} cm³ · sólido={m.is_volume}")

    with tempfile.TemporaryDirectory() as tmp:
        a = painted(trimesh.load(HERE / "pieza_A.stl"), "A")
        b = painted(openscad("B_use", Path(tmp) / "b.stl"), "B")
        c = openscad("C_use", Path(tmp) / "c.stl")
    c_up = c.copy()
    c_up.apply_transform(rotation_matrix(np.radians(-FOLD_MAX), [0, 1, 0], [X_AXIS, 0, Z_AXIS]))
    env = context()
    export_glb(env + [a, b, painted(c, "C")], "estropajero_v3_abajo.glb")
    export_glb(env + [a, b, painted(c_up, "C")], "estropajero_v3_levantada.glb")

    bed = trimesh.creation.box(bounds=[[0, 0, -1.5], [256, 256, 0]])
    placed = plate_layout()
    export_glb([painted(bed, "placa", roughness=0.8)]
               + [painted(m, k) for m, k in zip(placed, "ABC")], "estropajero_v3_placa.glb")

    write_3mf(FILES_DIR / "estropajero_v3_A1.3mf")
    for f in [*PRINT_PARTS.values(), SCAD.name, "APRENDIZAJES.md"]:
        shutil.copy(HERE / f, FILES_DIR / f)

    (WEB_DIR / "version.txt").write_text(str(int(time.time())))
    print("GLB, 3MF y descargas actualizados.")


if __name__ == "__main__":
    main()
