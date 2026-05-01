#!/usr/bin/env python3
"""Bathroom bar — Proposal B ("Carril").

Visualisation-grade model of:
  - 2 PLA two-half clamps with M3 screw bosses (compression, no snap-flex)
  - PLA rectangular rail with a T-channel along its underside
  - 1 representative T-head hook sliding in the rail
  - All PLA — no aluminum rod

In real life the rail is printed in 3 segments (~210 + 85 + 210 mm) joined
by tongue-and-groove; here it is shown as one piece for visualisation.
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _bathroom_context import make_context_meshes, colour_pla

# ===== Common ================================================================
FAUCET_OD       = 29.0
HANDLE_OD       = 42.0
GAP_EDGE        = 49.0
CTC             = FAUCET_OD/2 + GAP_EDGE + HANDLE_OD/2   # 84.5 mm
WALL_T          = 4.0
PLA_FIT         = 0.4
ARC_SEG         = 64

# ===== Proposal B parameters =================================================
CLAMP_W_Y       = 14.0      # along cylinder axis (Y)
CLAMP_Y_CENTER  = 9.0
CLAMP_OVERLAP   = 0.6

# Rail cross-section (rectangular with a T-channel cut underneath)
RAIL_W_Y        = 14.0      # rail Y-thickness (perpendicular to wall)
RAIL_H_Z        = 18.0      # rail Z-height
RAIL_LEN        = 485.0     # total length along X (visualised as one piece)
TSLOT_OPEN_Y    = 6.0       # mouth width
TSLOT_INNER_Y   = 10.0      # inner slot width (the wider chamber)
TSLOT_NECK_Z    = 3.0       # mouth height (from rail bottom upward)
TSLOT_INNER_Z   = 5.0       # inner chamber height

# Clamp overall: a closed ring around the cylinder + a rail-grabbing block
CLAMP_BLOCK_OUT_Z = -28.0   # Z of the rail centre (rail centre is here)
RAIL_Z_CENTER   = CLAMP_BLOCK_OUT_Z

SCREW_HEAD_R    = 3.0       # M3 visualisation
SCREW_HEAD_OFFSET_Z = 0.0   # screw axis at clamp midplane

# Hook (T-head sliding in the rail, J-arm hanging)
HOOK_W_X        = 18.0      # along X (rail axis)
HOOK_HEAD_W_Y   = TSLOT_INNER_Y - PLA_FIT  # 9.6
HOOK_HEAD_H_Z   = TSLOT_INNER_Z - PLA_FIT  # 4.6
HOOK_NECK_W_Y   = TSLOT_OPEN_Y - PLA_FIT   # 5.6
HOOK_NECK_H_Z   = TSLOT_NECK_Z + 1.0
HOOK_DROP       = 18.0
HOOK_CURL_R     = 8.0
HOOK_BODY_T     = 4.0
HOOK_X_POS      = -CTC/2 - 60.0

OUT_FILE = Path(__file__).with_name("bathroom_bar_b.stl")
WEB_DIR  = Path(__file__).resolve().parents[2] / "docs" / "models"
WEB_FILE = WEB_DIR / "bathroom_bar_b.glb"


def update_web_version():
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    (WEB_DIR / "version.txt").write_text(str(int(time.time())))


# ===== Parts =================================================================
def make_clamp_ring_closed(cyl_od: float, x_pos: float):
    """Closed ring (the two halves bolted together) around the cylinder."""
    r_in  = cyl_od/2 + PLA_FIT/2
    r_out = r_in + WALL_T
    # Outer cylinder along Y, then subtract inner cylinder
    outer = trimesh.creation.cylinder(radius=r_out, height=CLAMP_W_Y,
                                      sections=ARC_SEG)
    inner = trimesh.creation.cylinder(radius=r_in,  height=CLAMP_W_Y + 2,
                                      sections=ARC_SEG)
    R = trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0])
    outer.apply_transform(R)
    inner.apply_transform(R)
    outer.apply_translation([x_pos, CLAMP_Y_CENTER, 0])
    inner.apply_translation([x_pos, CLAMP_Y_CENTER, 0])
    ring = trimesh.boolean.difference([outer, inner], engine="manifold")
    return ring


def make_clamp_screw_bosses(cyl_od: float, x_pos: float):
    """Two cylinder-bosses + M3 screws on each side of the ring (visualisation)."""
    r_out = cyl_od/2 + PLA_FIT/2 + WALL_T
    boss_r  = 3.5
    boss_h  = CLAMP_W_Y
    # bosses sit horizontally, axis along Y, at +X and -X tangent of ring
    R = trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0])

    bosses = []
    for sign in (-1, +1):
        boss = trimesh.creation.cylinder(radius=boss_r, height=boss_h,
                                         sections=ARC_SEG)
        boss.apply_transform(R)
        boss.apply_translation([x_pos + sign * (r_out + boss_r - 1.0),
                                CLAMP_Y_CENTER, 0])
        bosses.append(boss)

    # M3 screw heads (cosmetic): tiny cylinders along Y at the boss face
    screws = []
    for sign in (-1, +1):
        head = trimesh.creation.cylinder(radius=SCREW_HEAD_R, height=1.5,
                                         sections=24)
        head.apply_transform(R)
        head.apply_translation([x_pos + sign * (r_out + boss_r - 1.0),
                                CLAMP_Y_CENTER + CLAMP_W_Y/2 + 0.75,
                                SCREW_HEAD_OFFSET_Z])
        screws.append(head)
    return bosses, screws


def make_clamp_rail_block(cyl_od: float, x_pos: float):
    """Block under the clamp that grabs the rail (the rail passes through it)."""
    r_out = cyl_od/2 + PLA_FIT/2 + WALL_T
    z_top = -r_out + CLAMP_OVERLAP
    z_bot = RAIL_Z_CENTER - RAIL_H_Z/2 - WALL_T
    h = z_top - z_bot
    if h <= 0:
        return None
    # block envelopes the rail with a rectangular hole
    outer_block = trimesh.creation.box(
        extents=[RAIL_W_Y + 2 * WALL_T, CLAMP_W_Y, h]
    )
    outer_block.apply_translation([x_pos, CLAMP_Y_CENTER, (z_top + z_bot) / 2])
    rail_hole = trimesh.creation.box(
        extents=[RAIL_W_Y + PLA_FIT, CLAMP_W_Y + 2, RAIL_H_Z + PLA_FIT]
    )
    rail_hole.apply_translation([x_pos, CLAMP_Y_CENTER, RAIL_Z_CENTER])
    block = trimesh.boolean.difference([outer_block, rail_hole],
                                       engine="manifold")
    return block


def make_clamp(cyl_od: float, x_pos: float):
    ring = make_clamp_ring_closed(cyl_od, x_pos)
    bosses, screws = make_clamp_screw_bosses(cyl_od, x_pos)
    rail_block = make_clamp_rail_block(cyl_od, x_pos)
    parts = [ring] + bosses
    if rail_block is not None:
        parts.append(rail_block)
    union = trimesh.boolean.union(parts, engine="manifold")
    if not union.is_volume:
        union = trimesh.util.concatenate(parts)
    return union, screws


def rail_cross_section_polygon() -> Polygon:
    """Rectangular outer minus T-slot in the bottom face. Returns 2D polygon."""
    # Outer rectangle in (Y, Z)
    y_half = RAIL_W_Y / 2
    z_top  = +RAIL_H_Z / 2
    z_bot  = -RAIL_H_Z / 2
    outer = Polygon([
        (-y_half, z_bot), (+y_half, z_bot),
        (+y_half, z_top), (-y_half, z_top),
    ])
    # T-slot: neck (mouth) + inner chamber, opening downward
    neck_y = TSLOT_OPEN_Y / 2
    neck_z_top = z_bot + TSLOT_NECK_Z
    inner_y = TSLOT_INNER_Y / 2
    inner_z_top = neck_z_top + TSLOT_INNER_Z
    slot_pts = [
        (-neck_y, z_bot - 0.1),
        (+neck_y, z_bot - 0.1),
        (+neck_y, neck_z_top),
        (+inner_y, neck_z_top),
        (+inner_y, inner_z_top),
        (-inner_y, inner_z_top),
        (-inner_y, neck_z_top),
        (-neck_y, neck_z_top),
    ]
    slot = Polygon(slot_pts)
    return outer.difference(slot)


def make_rail():
    """Extrude the rail cross-section along X. Centred at X=0, Z=RAIL_Z_CENTER,
    Y=CLAMP_Y_CENTER."""
    poly = rail_cross_section_polygon()
    # extrude_polygon: poly is in (X_local, Y_local), extruded along +Z_local.
    # Our polygon coords are (Y_world, Z_world). So local X→Y_world, local Y→Z_world.
    # Extrusion direction (local Z) → world X.
    rail = trimesh.creation.extrude_polygon(poly, height=RAIL_LEN)
    M = np.eye(4)
    M[:3, :3] = np.array([
        [0, 0, 1],   # world X gets local Z (extrusion)
        [1, 0, 0],   # world Y gets local X
        [0, 1, 0],   # world Z gets local Y
    ])
    rail.apply_transform(M)
    rail.apply_translation([-RAIL_LEN/2, CLAMP_Y_CENTER, RAIL_Z_CENTER])
    return rail


def make_hook():
    """T-head + neck + drop+J-curl. The T-head slides inside the rail T-slot."""
    # T-head: inner cuboid that sits in the inner chamber
    head = trimesh.creation.box(
        extents=[HOOK_W_X, HOOK_HEAD_W_Y, HOOK_HEAD_H_Z]
    )
    z_head_center = RAIL_Z_CENTER - RAIL_H_Z/2 + TSLOT_NECK_Z + TSLOT_INNER_Z/2
    head.apply_translation([HOOK_X_POS, CLAMP_Y_CENTER, z_head_center])

    # Neck: smaller cuboid between the head and below the rail
    neck = trimesh.creation.box(
        extents=[HOOK_W_X, HOOK_NECK_W_Y, HOOK_NECK_H_Z + 1]
    )
    z_neck_center = RAIL_Z_CENTER - RAIL_H_Z/2 + (TSLOT_NECK_Z - 0.5) / 2
    neck.apply_translation([HOOK_X_POS, CLAMP_Y_CENTER, z_neck_center])

    # Body: vertical drop + J curl in the YZ plane, extruded along X by HOOK_W_X
    z_body_top = RAIL_Z_CENTER - RAIL_H_Z/2 - 0.5
    pts = [(0, z_body_top), (0, z_body_top - HOOK_DROP)]
    cy = z_body_top - HOOK_DROP
    cx = HOOK_CURL_R
    n = 16
    for i in range(1, n + 1):
        a = math.radians(180 + 180 * i / n)
        pts.append((cx + HOOK_CURL_R * math.cos(a),
                    cy + HOOK_CURL_R * math.sin(a)))
    pts.append((2 * HOOK_CURL_R, cy + 6))
    from shapely.geometry import LineString
    line = LineString(pts)
    poly = line.buffer(HOOK_BODY_T/2 * 1.4, cap_style=1, join_style=1,
                       resolution=10)
    body = trimesh.creation.extrude_polygon(poly, height=HOOK_W_X)
    M = np.eye(4)
    M[:3, :3] = np.array([
        [0, 0, 1],
        [1, 0, 0],
        [0, 1, 0],
    ])
    body.apply_transform(M)
    body.apply_translation([HOOK_X_POS - HOOK_W_X/2, CLAMP_Y_CENTER, 0])

    return [head, neck, body]


# ===== Build & write =========================================================
def main():
    clamp_caño,    screws_a = make_clamp(FAUCET_OD, -CTC/2)
    clamp_manilla, screws_b = make_clamp(HANDLE_OD, +CTC/2)
    rail = make_rail()
    hook_parts = make_hook()

    printed_parts = [clamp_caño, clamp_manilla, rail] + hook_parts
    printed = trimesh.boolean.union(printed_parts, engine="manifold")
    if not printed.is_volume:
        printed = trimesh.util.concatenate(printed_parts)
    printed.export(OUT_FILE)

    colour_pla(clamp_caño)
    colour_pla(clamp_manilla)
    colour_pla(rail)
    for p in hook_parts:
        colour_pla(p)
    for s in screws_a + screws_b:
        s.visual.face_colors = [180, 180, 188, 255]  # M3 stainless

    scene = trimesh.Scene()
    scene.add_geometry(clamp_caño,    geom_name="clamp_caño")
    scene.add_geometry(clamp_manilla, geom_name="clamp_manilla")
    scene.add_geometry(rail,          geom_name="rail")
    for i, p in enumerate(hook_parts):
        scene.add_geometry(p, geom_name=f"hook_part_{i}")
    for i, s in enumerate(screws_a + screws_b):
        scene.add_geometry(s, geom_name=f"m3_screw_{i}")
    for name, mesh in make_context_meshes(FAUCET_OD, HANDLE_OD, CTC):
        scene.add_geometry(mesh, geom_name=name)
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    scene.export(WEB_FILE)
    update_web_version()

    bb_min, bb_max = printed.bounds
    size = bb_max - bb_min
    print(f"Wrote {OUT_FILE}")
    print(f"Wrote {WEB_FILE}")
    print(f"Printed bounding box (mm): "
          f"X {size[0]:.1f}  Y {size[1]:.1f}  Z {size[2]:.1f}")
    print(f"Printed volume:  {printed.volume / 1000:.1f} cm³  "
          f"(manifold={printed.is_volume})")


if __name__ == "__main__":
    main()
