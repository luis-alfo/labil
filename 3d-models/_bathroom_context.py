"""Shared visual context + GLB export for the bathroom-bar designs.

Not a printable design: it lives beside the design folders so the CI loop
(`for dir in 3d-models/*/`) ignores it.

Model frame used by every bathroom-bar generator (millimetres):

    x  → right, as seen by someone standing in front of the wall
    y  → out of the wall, towards that person (y = 0 is the black plate's face)
    z  → up
    origin = midpoint between the caño and manilla axes

That frame is left-handed, so `export_glb()` mirrors it into glTF's
right-handed Y-up frame and scales mm → m. Without that step the model shows
lying on its back, mirrored, and 1000x too large in AR.

The fixture geometry is estimated from the user's photos: only the two
diameters and the edge-to-edge gap were measured. Everything else (plate
size, flange thickness, spout reach, lever angle) is approximate and exists
only to judge the design in context.
"""

from __future__ import annotations

import math
from typing import Iterable, List, Tuple

import numpy as np
import trimesh
from shapely.geometry import Point
from trimesh.visual.material import PBRMaterial

ARC_SEG = 48

# (rgba 0-255, metallic, roughness)
MAT_BLACK  = ([34, 34, 37, 255], 0.35, 0.55)     # matte black fixtures
MAT_CHROME = ([212, 214, 220, 255], 1.0, 0.18)   # chrome rings / aerator
MAT_WALL   = ([150, 146, 139, 255], 0.0, 0.95)   # grey microcement panel
MAT_PLA    = ([214, 214, 209, 255], 0.0, 0.6)    # the printed line: light grey
MAT_PLA_2  = ([236, 94, 28, 255], 0.0, 0.55)     # interchangeable hooks: orange

# Kept for the older A/B/C generators, which paint with face colours.
COLOR_BLACK  = MAT_BLACK[0]
COLOR_CHROME = MAT_CHROME[0]
COLOR_PLA    = MAT_PLA[0]

# model (x right, y out, z up; mm)  →  glTF (X right, Y up, Z towards viewer; m)
_GLTF_FROM_MODEL = np.array([
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1000.0],
], dtype=float) / 1000.0


def paint(mesh: "trimesh.Trimesh", mat) -> "trimesh.Trimesh":
    """Give a mesh a flat PBR material (no texture)."""
    rgba, metallic, roughness = mat
    mesh.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(
        baseColorFactor=[c / 255.0 for c in rgba],
        metallicFactor=metallic,
        roughnessFactor=roughness,
    ))
    return mesh


def colour_pla(mesh: "trimesh.Trimesh") -> "trimesh.Trimesh":
    return paint(mesh, MAT_PLA)


def export_glb(items, path) -> None:
    """Write named meshes (or a Scene) as a GLB in glTF's frame and units."""
    if isinstance(items, trimesh.Scene):
        items = list(items.geometry.items())
    scene = trimesh.Scene()
    for name, mesh in items:
        m = mesh.copy()
        m.apply_transform(_GLTF_FROM_MODEL)   # mirror: trimesh re-winds faces
        scene.add_geometry(m, geom_name=name, node_name=name)
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.export(path)


def _cyl_y(radius: float, y0: float, y1: float, x: float, z: float = 0.0):
    """Cylinder whose axis runs along +y from y0 to y1."""
    m = trimesh.creation.cylinder(radius=radius, height=y1 - y0,
                                  sections=ARC_SEG)
    m.apply_transform(trimesh.transformations.rotation_matrix(
        math.pi / 2, [1, 0, 0]))
    m.apply_translation([x, (y0 + y1) / 2, z])
    return m


def _tube(points: Iterable[Tuple[float, float, float]], radius: float):
    """Round tube through 3D points (sphere-capped cylinder chain)."""
    pts = [np.asarray(p, dtype=float) for p in points]
    parts = []
    for a, b in zip(pts[:-1], pts[1:]):
        seg = trimesh.creation.cylinder(radius=radius, segment=[a, b],
                                        sections=ARC_SEG)
        parts.append(seg)
    for p in pts[1:-1]:
        ball = trimesh.creation.icosphere(radius=radius, subdivisions=2)
        ball.apply_translation(p)
        parts.append(ball)
    return trimesh.util.concatenate(parts)


def make_context_meshes(faucet_od: float, handle_od: float, ctc: float,
                        wall: bool = True, cano_flange: float = 6.0,
                        mani_flange: float = 2.0
                        ) -> List[Tuple[str, "trimesh.Trimesh"]]:
    """Wall panel, black plate, caño with its spout, manilla with its lever."""
    PLATE_T    = 4.0
    xc, xm = -ctc / 2, +ctc / 2
    items: List[Tuple[str, "trimesh.Trimesh"]] = []

    if wall:
        panel = trimesh.creation.box(extents=[620, 4, 250])
        panel.apply_translation([0, -PLATE_T - 2, -30])
        items.append(("pared", paint(panel, MAT_WALL)))

    # Black plate: ~150 x 68 mm (from the frontal photo of 17 Nov 2026).
    plate = trimesh.creation.box(extents=[150, PLATE_T, 68])
    plate.apply_translation([-1, -PLATE_T / 2, -2.5])
    items.append(("placa", paint(plate, MAT_BLACK)))

    # ---- caño: chrome flange, Ø29 tube that reaches out and turns down ----
    items.append(("cano_embellecedor", paint(
        _cyl_y(faucet_od / 2 + 4, 0, cano_flange, xc), MAT_CHROME)))
    reach, bend_r = 78.0, 40.0
    path = [(xc, 0.0, 0.0), (xc, reach, 0.0)]
    for i in range(1, 13):
        a = math.radians(82 * i / 12)
        path.append((xc, reach + bend_r * math.sin(a),
                     -bend_r * (1 - math.cos(a))))
    end = np.array(path[-1])
    direction = end - np.array(path[-2])
    direction /= np.linalg.norm(direction)
    path.append(tuple(end + direction * 8))
    items.append(("cano", paint(_tube(path, faucet_od / 2), MAT_BLACK)))
    tip_a = np.array(path[-1])
    items.append(("cano_aireador", paint(
        _tube([tip_a, tip_a + direction * 20], faucet_od / 2 + 0.4),
        MAT_CHROME)))

    # ---- manilla: flange, fixed sleeve, chrome dome, moving cap, lever ----
    items.append(("manilla_embellecedor", paint(
        _cyl_y(handle_od / 2 + 3.5, 0, mani_flange, xm), MAT_CHROME)))
    items.append(("manilla_casquillo_fijo", paint(
        _cyl_y(handle_od / 2, mani_flange, 15, xm), MAT_BLACK)))
    dome = trimesh.creation.icosphere(radius=handle_od / 2 - 2.5,
                                      subdivisions=3)
    dome.apply_translation([xm, 17, 0])
    items.append(("manilla_rotula", paint(dome, MAT_CHROME)))
    items.append(("manilla_mando", paint(
        _cyl_y(handle_od / 2, 21, 44, xm), MAT_BLACK)))
    lean = math.radians(24)                     # lever hangs down-right
    start = np.array([xm + 6 * math.sin(lean), 33, -handle_od / 2 + 4])
    lever_dir = np.array([math.sin(lean), 0, -math.cos(lean)])
    items.append(("manilla_palanca", paint(
        _tube([start, start + lever_dir * 78], 4.0), MAT_BLACK)))

    return items
