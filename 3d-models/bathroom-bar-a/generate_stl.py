#!/usr/bin/env python3
"""Bathroom bar — Proposal A ("Hilo").

Visualisation-grade model of:
  - 2 PLA snap clamps (Ø29 over caño, Ø42 over manilla) with mouth +Z
  - Strut down to a horizontal rod socket
  - Ø6 mm aluminum rod, 485 mm long, with a subtle upward bend at each end
  - 1 representative J-hook hanging from the rod

Install orientation (Z up, Y wall-perpendicular, X along rod). The
aluminum rod is included so the GLB shows the full assembly; in real
life the rod is bought, cut, bent at the ends, and slid through both
clamp sockets before the clamps are pressed onto the cylinders.
"""

from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon

# ===== Common (all proposals share these) ====================================
FAUCET_OD       = 29.0
HANDLE_OD       = 42.0
GAP_EDGE        = 49.0
CTC             = FAUCET_OD/2 + GAP_EDGE + HANDLE_OD/2   # = 84.5 mm
WALL_T          = 4.0
PLA_FIT         = 0.4
ARC_SEG         = 64

# ===== Proposal A ============================================================
CLAMP_W_Y       = 12.0      # along cylinder axis (Y); cylinders expose 15-20 mm
CLAMP_WRAP_DEG  = 240.0     # snap-fit, mouth +Z (push up onto cylinder)
CLAMP_OVERLAP   = 0.6
CLAMP_Y_CENTER  = 9.0       # 9 mm out from wall (centred in 12-mm exposed cyl.)

ROD_OD          = 6.0
ROD_HOLE_ID     = ROD_OD + PLA_FIT      # 6.4 socket bore
SOCKET_OD       = ROD_HOLE_ID + 2 * WALL_T   # 14.4
ROD_DROP        = 38.0      # rod centerline below cylinder centers

ROD_LEN_SIDE    = 200.0     # "un palmo" beyond each clamp center
ROD_BEND_LEN    = 30.0
ROD_BEND_DEG    = 10.0

# Demo hook (J-shape) for visualisation
HOOK_ID         = ROD_OD + PLA_FIT
HOOK_OD         = HOOK_ID + 2 * 2.5
HOOK_W_X        = 10.0      # along rod
HOOK_WRAP_DEG   = 230.0
HOOK_DROP       = 18.0
HOOK_CURL_R     = 8.0
HOOK_X_POS      = -CTC/2 - 60.0  # 60 mm left of caño centre

OUT_FILE = Path(__file__).with_name("bathroom_bar_a.stl")
WEB_DIR  = Path(__file__).resolve().parents[2] / "docs" / "models"
WEB_FILE = WEB_DIR / "bathroom_bar_a.glb"


# ===== Helpers ===============================================================
def partial_annulus(r_in: float, r_out: float,
                    a_start_deg: float, a_end_deg: float,
                    segments: int = ARC_SEG) -> Polygon:
    a0, a1 = math.radians(a_start_deg), math.radians(a_end_deg)
    angles = np.linspace(a0, a1, segments)
    outer = [(r_out * math.cos(a), r_out * math.sin(a)) for a in angles]
    inner = [(r_in  * math.cos(a), r_in  * math.sin(a)) for a in angles[::-1]]
    return Polygon(outer + inner)


def update_web_version():
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    (WEB_DIR / "version.txt").write_text(str(int(time.time())))


# ===== Parts =================================================================
def make_clamp_ring(cyl_od: float, x_pos: float):
    """C-clip ring around a cylinder whose axis runs along +Y.
    Mouth opens +Z (push up onto the cylinder)."""
    r_in  = cyl_od / 2 + PLA_FIT / 2
    r_out = r_in + WALL_T
    half_open = (360 - CLAMP_WRAP_DEG) / 2
    # Polygon with mouth at +Y_local (so after +90° X-rotation it ends at +Z world).
    poly = partial_annulus(r_in, r_out,
                           90 + half_open,
                           90 + half_open + CLAMP_WRAP_DEG)
    ring = trimesh.creation.extrude_polygon(poly, height=CLAMP_W_Y)
    R = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    ring.apply_transform(R)
    # After rotation, extrusion spans Y in [-CLAMP_W_Y, 0]; centre on CLAMP_Y_CENTER.
    ring.apply_translation([x_pos, CLAMP_Y_CENTER + CLAMP_W_Y / 2, 0])
    return ring


def make_socket(x_pos: float):
    """Horizontal cylindrical socket along X for the Ø6 rod, centred at clamp."""
    sock = trimesh.creation.annulus(r_min=ROD_HOLE_ID/2, r_max=SOCKET_OD/2,
                                    height=CLAMP_W_Y, sections=ARC_SEG)
    # annulus is along Z by default; rotate so axis becomes X
    R = trimesh.transformations.rotation_matrix(math.pi/2, [0, 1, 0])
    sock.apply_transform(R)
    sock.apply_translation([x_pos, CLAMP_Y_CENTER, -ROD_DROP])
    return sock


def make_strut(cyl_od: float, x_pos: float):
    """Rectangular strut from clip outer (Z = -r_out) down to socket top."""
    r_out = cyl_od/2 + PLA_FIT/2 + WALL_T
    z_top = -r_out + CLAMP_OVERLAP
    z_bot = -ROD_DROP + SOCKET_OD/2 - CLAMP_OVERLAP
    h = z_top - z_bot
    if h <= 0:
        return None
    strut = trimesh.creation.box(extents=[WALL_T * 2, CLAMP_W_Y, h])
    strut.apply_translation([x_pos, CLAMP_Y_CENTER, (z_top + z_bot) / 2])
    return strut


def make_clamp(cyl_od: float, x_pos: float):
    parts = [make_clamp_ring(cyl_od, x_pos), make_socket(x_pos)]
    s = make_strut(cyl_od, x_pos)
    if s is not None:
        parts.append(s)
    union = trimesh.boolean.union(parts, engine="manifold")
    return union if union.is_volume else trimesh.util.concatenate(parts)


def make_rod():
    """Aluminum rod centerline along X, with subtle upward bend at each end."""
    n_arc = 12
    bend_rad = math.radians(ROD_BEND_DEG)
    # Build polyline of centerline in (X, Z), rod axis along X, in the XZ plane.
    pts = []
    x_start_straight = -ROD_LEN_SIDE
    x_end_straight   = +ROD_LEN_SIDE
    # Left bend (curving up from X = -ROD_LEN_SIDE to X = -ROD_LEN_SIDE + ROD_BEND_LEN)
    # Approximate as a small circular arc.
    pts.append((-ROD_LEN_SIDE - ROD_BEND_LEN * math.cos(bend_rad),
                ROD_BEND_LEN * math.sin(bend_rad)))
    for i in range(n_arc + 1):
        t = i / n_arc
        a = bend_rad * (1 - t)  # 10° → 0°
        pts.append((-ROD_LEN_SIDE - 0 + (1 - t) * (-ROD_BEND_LEN * math.cos(a) + ROD_BEND_LEN), 0))
    # Simpler: just two segments with the bend approximated.
    pts = [
        (-ROD_LEN_SIDE - ROD_BEND_LEN * math.cos(bend_rad),
         ROD_BEND_LEN * math.sin(bend_rad)),
        (-ROD_LEN_SIDE, 0),
        (+ROD_LEN_SIDE, 0),
        (+ROD_LEN_SIDE + ROD_BEND_LEN * math.cos(bend_rad),
         ROD_BEND_LEN * math.sin(bend_rad)),
    ]
    line = LineString(pts)
    poly = line.buffer(ROD_OD/2, cap_style=1, join_style=1, resolution=12)
    rod = trimesh.creation.extrude_polygon(poly, height=ROD_OD)
    # Polygon is in (X, Z). Extrusion is +Z which we want to be Y-thickness.
    # Rotate +90° around X: polygon Y → +Z, polygon Z (extrusion) → -Y.
    R = trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0])
    rod.apply_transform(R)
    # Centre Y on CLAMP_Y_CENTER (rod span on Y is [-ROD_OD, 0] after rotation)
    rod.apply_translation([0, CLAMP_Y_CENTER + ROD_OD/2, -ROD_DROP])
    return rod


def make_hook():
    """J-hook ring around rod (axis +X), with drop+curl in the YZ plane."""
    # Ring (axis +X, mouth -Z so we push the hook up onto the rod from below)
    r_in  = HOOK_ID / 2
    r_out = HOOK_OD / 2
    half_open = (360 - HOOK_WRAP_DEG) / 2
    # Polygon mouth at -Y_local (so after rotation it ends at -Z world).
    poly = partial_annulus(r_in, r_out,
                           270 + half_open,
                           270 + half_open + HOOK_WRAP_DEG)
    ring = trimesh.creation.extrude_polygon(poly, height=HOOK_W_X)
    # Polygon in local (x_local, y_local), extruded along +Z. We want the ring
    # axis to be world X. Rotate -90° around Y: local +Z → world +X, local +X → world -Z.
    R = trimesh.transformations.rotation_matrix(-math.pi/2, [0, 1, 0])
    ring.apply_transform(R)
    # After rotation, extrusion (was +Z) → +X, span [HOOK_X_POS - HOOK_W_X/2, +HOOK_W_X/2]
    ring.apply_translation([HOOK_X_POS + HOOK_W_X/2, CLAMP_Y_CENTER, -ROD_DROP])

    # Drop+curl in YZ plane (centerline buffered into solid)
    z_ring_bot = -ROD_DROP - HOOK_OD/2 + CLAMP_OVERLAP
    pts = [(0, z_ring_bot), (0, z_ring_bot - HOOK_DROP)]
    cy = z_ring_bot - HOOK_DROP
    cx = HOOK_CURL_R
    n = 16
    for i in range(1, n + 1):
        a = math.radians(180 + 180 * i / n)
        pts.append((cx + HOOK_CURL_R * math.cos(a), cy + HOOK_CURL_R * math.sin(a)))
    # Small upturn
    pts.append((2 * HOOK_CURL_R, cy + 6))
    line = LineString(pts)
    poly = line.buffer(WALL_T/2 * 1.4, cap_style=1, join_style=1, resolution=10)
    body = trimesh.creation.extrude_polygon(poly, height=HOOK_W_X)
    # Polygon in (Y, Z), extruded along +Z; rotate so polygon Y→Y, polygon Z→Z
    # Wait: the polygon is in (Y_world, Z_world) but extrude_polygon treats it as (X_local, Y_local) extruded along +Z_local.
    # So polygon's X (= our Y_world) → world X, polygon Y (= our Z_world) → world Y, extrusion → world Z.
    # We want polygon X → world Y, polygon Y → world Z, extrusion → world X.
    # Rotate so X_local→Y_world, Y_local→Z_world, Z_local→X_world.
    # That's a permutation: rotate +90° around Y (sends X→-Z, Z→+X) then +90° around X (sends Y→Z, Z→-Y).
    # Easier: build a 3x3 perm matrix manually.
    M = np.eye(4)
    M[:3, :3] = np.array([
        [0, 0, 1],   # world X gets local Z (extrusion)
        [1, 0, 0],   # world Y gets local X
        [0, 1, 0],   # world Z gets local Y
    ])
    body.apply_transform(M)
    body.apply_translation([HOOK_X_POS - HOOK_W_X/2, CLAMP_Y_CENTER, 0])
    return [ring, body]


# ===== Build & write =========================================================
def main():
    clamp_caño    = make_clamp(FAUCET_OD, -CTC/2)
    clamp_manilla = make_clamp(HANDLE_OD, +CTC/2)
    rod           = make_rod()
    hook_ring, hook_body = make_hook()

    # Print scene = clamps + hook only (rod is metal, not printed)
    printed = trimesh.boolean.union(
        [clamp_caño, clamp_manilla, hook_ring, hook_body],
        engine="manifold",
    )
    if not printed.is_volume:
        printed = trimesh.util.concatenate(
            [clamp_caño, clamp_manilla, hook_ring, hook_body]
        )
    printed.export(OUT_FILE)

    # Web scene = everything (clamps, hook, rod) for visualisation
    scene = trimesh.Scene()
    scene.add_geometry(clamp_caño,    geom_name="clamp_caño",    node_name="clamp_caño")
    scene.add_geometry(clamp_manilla, geom_name="clamp_manilla", node_name="clamp_manilla")
    scene.add_geometry(rod,           geom_name="rod_aluminum",  node_name="rod_aluminum")
    scene.add_geometry(hook_ring,     geom_name="hook_ring",     node_name="hook_ring")
    scene.add_geometry(hook_body,     geom_name="hook_body",     node_name="hook_body")
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
