"""Shared visual context for bathroom-bar designs.

Provides geometry of the wall-mounted faucet (caño + spout) and the
mixer handle (manilla + lever) so each proposal can be rendered in
its real environment. Returned meshes carry per-face colours so the
fixtures show as matte black against the cream-coloured PLA parts.

This module is NOT a printable design — it lives at the parent of the
design folders so the CI's `for dir in 3d-models/*/` loop ignores it.

Usage from a generator:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from _bathroom_context import make_context_meshes, COLOR_PLA

    ctx = make_context_meshes(faucet_od=29.0, handle_od=42.0, ctc=84.5)
    for name, mesh in ctx:
        scene.add_geometry(mesh, geom_name=name)
"""

from __future__ import annotations

import math
from typing import List, Tuple

import numpy as np
import trimesh

ARC_SEG = 48

# Per-face RGBA colours (uint8). trimesh writes these into the GLB so
# <model-viewer> renders them as flat-shaded materials.
COLOR_BLACK  = [38, 38, 41, 255]      # matte black faucet / plate / lever
COLOR_CHROME = [205, 205, 215, 255]   # chrome rings + spout tip
COLOR_PLA    = [240, 230, 200, 255]   # warm cream PLA for the bar parts


def _rot_x(angle_rad: float):
    return trimesh.transformations.rotation_matrix(angle_rad, [1, 0, 0])


def _rot_y(angle_rad: float):
    return trimesh.transformations.rotation_matrix(angle_rad, [0, 1, 0])


def _coloured(mesh: "trimesh.Trimesh", rgba) -> "trimesh.Trimesh":
    mesh.visual.face_colors = rgba
    return mesh


def make_context_meshes(faucet_od: float, handle_od: float,
                        ctc: float) -> List[Tuple[str, "trimesh.Trimesh"]]:
    """Build the wall-mounted faucet + handle visualisation context.

    Coords match the bar generators: Z up, Y wall-perpendicular (+Y away
    from wall), X along the rod direction. Origin = midpoint between the
    two cylinder centres at the wall surface (Y=0).
    """
    # ---- dimensions ----
    PLATE_W_X       = 200.0
    PLATE_H_Z       = 90.0
    PLATE_T_Y       = 4.0

    CYL_LEN_Y       = 18.0     # cylinders protrude this much from the wall

    SPOUT_OD        = 9.0
    SPOUT_OUT_LEN   = 14.0     # short straight section before the elbow
    SPOUT_DOWN_LEN  = 60.0     # longer section after the elbow
    SPOUT_ANGLE     = 30.0     # elbow turns the spout this far past vertical

    LEVER_OD        = 7.0
    LEVER_LEN       = 80.0
    LEVER_TILT_DEG  = 12.0     # slight downward tilt
    LEVER_DIR_X     = +1.0     # exits to the right of the handle

    items: List[Tuple[str, "trimesh.Trimesh"]] = []

    # ---- wall plate ----
    plate = trimesh.creation.box(
        extents=[PLATE_W_X, PLATE_T_Y, PLATE_H_Z]
    )
    plate.apply_translation([0, -PLATE_T_Y / 2, 0])
    items.append(("wall_plate", _coloured(plate, COLOR_BLACK)))

    # Helper for a cylinder along +Y
    def cyl_along_y(radius, length, sections=ARC_SEG):
        m = trimesh.creation.cylinder(radius=radius, height=length,
                                      sections=sections)
        m.apply_transform(_rot_x(math.pi / 2))
        return m

    # ---- caño (faucet body) ----
    caño = cyl_along_y(faucet_od / 2, CYL_LEN_Y)
    caño.apply_translation([-ctc / 2, CYL_LEN_Y / 2, 0])
    items.append(("faucet_cylinder", _coloured(caño, COLOR_BLACK)))

    # Chrome ring at the base of the caño, snug against the plate
    ring_caño = trimesh.creation.annulus(r_min=faucet_od / 2 + 0.4,
                                         r_max=faucet_od / 2 + 2.6,
                                         height=2.2,
                                         sections=ARC_SEG)
    ring_caño.apply_transform(_rot_x(math.pi / 2))
    ring_caño.apply_translation([-ctc / 2, 1.2, 0])
    items.append(("faucet_chrome_ring", _coloured(ring_caño, COLOR_CHROME)))

    # ---- spout: short straight + elbow + longer down-and-out ----
    # Segment 1: short straight section continuing along +Y from the cylinder front
    seg1 = trimesh.creation.cylinder(radius=SPOUT_OD / 2,
                                     height=SPOUT_OUT_LEN,
                                     sections=ARC_SEG)
    seg1.apply_transform(_rot_x(math.pi / 2))
    seg1.apply_translation([-ctc / 2,
                            CYL_LEN_Y + SPOUT_OUT_LEN / 2,
                            0])
    items.append(("spout_seg1", _coloured(seg1, COLOR_BLACK)))

    # Elbow: a sphere at the joint
    elbow_pos = np.array([-ctc / 2,
                          CYL_LEN_Y + SPOUT_OUT_LEN,
                          0])
    elbow = trimesh.creation.icosphere(radius=SPOUT_OD / 2 + 0.3,
                                       subdivisions=2)
    elbow.apply_translation(elbow_pos)
    items.append(("spout_elbow", _coloured(elbow, COLOR_BLACK)))

    # Segment 2: angled down-and-forward from the elbow
    angle = math.radians(SPOUT_ANGLE)
    # direction = (0, sin(angle), -cos(angle)) — mostly down, slightly forward
    dir2 = np.array([0, math.sin(angle), -math.cos(angle)])
    seg2 = trimesh.creation.cylinder(radius=SPOUT_OD / 2,
                                     height=SPOUT_DOWN_LEN,
                                     sections=ARC_SEG)
    # Default cylinder along +Z. To align +Z with dir2 = (0, sin, -cos):
    # rotate around +X by (π - angle): +Z → (0, sin(π-angle), cos(π-angle)) = (0, sin, -cos). ✓
    seg2.apply_transform(_rot_x(math.pi - angle))
    seg2.apply_translation(elbow_pos + dir2 * (SPOUT_DOWN_LEN / 2))
    items.append(("spout_seg2", _coloured(seg2, COLOR_BLACK)))

    # Chrome tip at the end of segment 2
    tip_pos = elbow_pos + dir2 * SPOUT_DOWN_LEN
    tip = trimesh.creation.cylinder(radius=SPOUT_OD / 2 + 0.7,
                                    height=10.0,
                                    sections=ARC_SEG)
    tip.apply_transform(_rot_x(math.pi - angle))
    tip.apply_translation(tip_pos - dir2 * 5.0)
    items.append(("spout_chrome_tip", _coloured(tip, COLOR_CHROME)))

    # ---- manilla (handle body) ----
    manilla = cyl_along_y(handle_od / 2, CYL_LEN_Y)
    manilla.apply_translation([+ctc / 2, CYL_LEN_Y / 2, 0])
    items.append(("handle_cylinder", _coloured(manilla, COLOR_BLACK)))

    # Chrome ring at the base of the manilla
    ring_man = trimesh.creation.annulus(r_min=handle_od / 2 + 0.4,
                                        r_max=handle_od / 2 + 2.6,
                                        height=2.2,
                                        sections=ARC_SEG)
    ring_man.apply_transform(_rot_x(math.pi / 2))
    ring_man.apply_translation([+ctc / 2, 1.2, 0])
    items.append(("handle_chrome_ring", _coloured(ring_man, COLOR_CHROME)))

    # ---- lever ----
    tilt = math.radians(LEVER_TILT_DEG)
    # direction = (cos(tilt), 0, -sin(tilt)) — mostly +X, slightly down
    dir_lever = np.array([math.cos(tilt) * LEVER_DIR_X, 0, -math.sin(tilt)])
    # Default cylinder along +Z; rotate around +Y by (π/2 + tilt) so +Z → (sin, 0, cos) at right angle
    # We want +Z → (cos(tilt), 0, -sin(tilt)) for LEVER_DIR_X = +1.
    # Rot_y(θ) maps +Z to (sin(θ), 0, cos(θ)). Want sin(θ) = cos(tilt), cos(θ) = -sin(tilt) → θ = π/2 + tilt.
    rot_lever = math.pi / 2 + tilt
    if LEVER_DIR_X < 0:
        rot_lever = -rot_lever
    lever = trimesh.creation.cylinder(radius=LEVER_OD / 2,
                                      height=LEVER_LEN,
                                      sections=ARC_SEG)
    lever.apply_transform(_rot_y(rot_lever))
    lever_start = np.array([+ctc / 2 + (handle_od / 2 - 1.0) * LEVER_DIR_X,
                            CYL_LEN_Y / 2,
                            0])
    lever.apply_translation(lever_start + dir_lever * (LEVER_LEN / 2))
    items.append(("handle_lever", _coloured(lever, COLOR_BLACK)))

    # Lever tip (small black ball)
    tip_pos2 = lever_start + dir_lever * LEVER_LEN
    lever_tip = trimesh.creation.icosphere(radius=LEVER_OD / 2 + 0.3,
                                           subdivisions=2)
    lever_tip.apply_translation(tip_pos2)
    items.append(("handle_lever_tip", _coloured(lever_tip, COLOR_CHROME)))

    return items


def colour_pla(mesh: "trimesh.Trimesh") -> "trimesh.Trimesh":
    """Convenience wrapper to paint a printed PLA part with the warm cream
    colour used by the viewer."""
    mesh.visual.face_colors = COLOR_PLA
    return mesh
