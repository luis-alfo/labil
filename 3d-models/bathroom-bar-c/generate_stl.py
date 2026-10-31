#!/usr/bin/env python3
"""Bathroom bar — Proposal C ("Rama").

Visualisation-grade model of a single curved monolithic PLA arm:
  - Smooth wave-shaped centerline that dips between caño and manilla
    and rises gently at the two tips.
  - Two integrated clip-rings (Ø29 over caño, Ø42 over manilla), each
    welded to the arm with a vertical strut. Because both clips are
    rigidly part of the same body, they reinforce each other under load.
  - Notches every 30 mm on the lower edge for hooks.
  - 1 representative hook plugged into a notch.

In real life this prints in 2-3 segments joined by tongue-and-groove
inserts; here it is shown as one continuous piece for visualisation.
"""

from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Polygon

# ===== Common ================================================================
FAUCET_OD       = 29.0
HANDLE_OD       = 42.0
GAP_EDGE        = 49.0
CTC             = FAUCET_OD/2 + GAP_EDGE + HANDLE_OD/2   # 84.5 mm
WALL_T          = 4.0
PLA_FIT         = 0.4
ARC_SEG         = 64

# ===== Proposal C parameters =================================================
ARM_W_Y         = 12.0      # arm Y-thickness (perpendicular to wall)
ARM_RADIUS      = 6.5       # buffer radius (gives ~13 mm Z-thickness at the spine)
ARM_Y_CENTER    = 9.0
TIP_LIFT        = 18.0      # how much the tips rise above the dip baseline
DIP_Z           = -28.0     # baseline Z between the two cylinders
ARM_TOTAL_LEN   = 485.0

# Integrated clips (closed rings welded to the arm)
CLIP_W_Y        = 14.0
CLIP_OVERLAP    = 0.6

# Notches (slot for hook)
NOTCH_PERIOD    = 30.0
NOTCH_W_X       = 6.0
NOTCH_DEPTH     = 4.0
NOTCH_Y_W       = ARM_W_Y + 2  # cuts all the way through Y

# Hook
HOOK_W_X        = NOTCH_W_X - PLA_FIT
HOOK_NECK_H_Z   = NOTCH_DEPTH + 1.0
HOOK_DROP       = 18.0
HOOK_CURL_R     = 8.0
HOOK_BODY_T     = 4.0
HOOK_X_POS      = -150.0  # 150 mm left of centre, on the left extension

OUT_FILE = Path(__file__).with_name("bathroom_bar_c.stl")
WEB_DIR  = Path(__file__).resolve().parents[2] / "docs" / "models"
WEB_FILE = WEB_DIR / "bathroom_bar_c.glb"


def update_web_version():
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    (WEB_DIR / "version.txt").write_text(str(int(time.time())))


# ===== Helpers ===============================================================
def arm_centerline_pts():
    """Wave-shaped centerline in (X, Z): dips between cylinders, rises at tips."""
    half = ARM_TOTAL_LEN / 2
    return [
        (-half,           DIP_Z + TIP_LIFT),       # left tip, raised
        (-half + 40,      DIP_Z + TIP_LIFT * 0.6),
        (-half + 90,      DIP_Z + TIP_LIFT * 0.15),
        (-CTC/2 - 30,     DIP_Z),                   # approaching caño
        (0,               DIP_Z - 4),               # mid-dip between
        (+CTC/2 + 30,     DIP_Z),                   # leaving manilla
        (+half - 90,      DIP_Z + TIP_LIFT * 0.15),
        (+half - 40,      DIP_Z + TIP_LIFT * 0.6),
        (+half,           DIP_Z + TIP_LIFT),        # right tip, raised
    ]


def make_arm():
    """Buffer the centerline polyline and extrude along Y."""
    line = LineString(arm_centerline_pts())
    poly = line.buffer(ARM_RADIUS, cap_style=1, join_style=1, resolution=12)
    arm = trimesh.creation.extrude_polygon(poly, height=ARM_W_Y)
    # Polygon coords are (X_world, Z_world); extrusion → world Y.
    M = np.eye(4)
    M[:3, :3] = np.array([
        [1, 0, 0],   # world X gets local X
        [0, 0, 1],   # world Y gets local Z (extrusion)
        [0, 1, 0],   # world Z gets local Y
    ])
    arm.apply_transform(M)
    arm.apply_translation([0, ARM_Y_CENTER - ARM_W_Y/2, 0])
    return arm


def make_integrated_clip(cyl_od: float, x_pos: float):
    """Closed ring around the cylinder + a strut down to the arm."""
    r_in  = cyl_od/2 + PLA_FIT/2
    r_out = r_in + WALL_T
    # Closed ring along Y
    outer = trimesh.creation.cylinder(radius=r_out, height=CLIP_W_Y,
                                      sections=ARC_SEG)
    inner = trimesh.creation.cylinder(radius=r_in,  height=CLIP_W_Y + 2,
                                      sections=ARC_SEG)
    R = trimesh.transformations.rotation_matrix(math.pi/2, [1, 0, 0])
    outer.apply_transform(R)
    inner.apply_transform(R)
    outer.apply_translation([x_pos, ARM_Y_CENTER, 0])
    inner.apply_translation([x_pos, ARM_Y_CENTER, 0])
    ring = trimesh.boolean.difference([outer, inner], engine="manifold")

    # Strut from ring bottom (Z = -r_out) down to arm top (Z ≈ DIP_Z + ARM_RADIUS)
    z_top = -r_out + CLIP_OVERLAP
    z_bot = DIP_Z + ARM_RADIUS - CLIP_OVERLAP
    h = z_top - z_bot
    if h > 0:
        strut = trimesh.creation.box(extents=[WALL_T * 2, CLIP_W_Y, h])
        strut.apply_translation([x_pos, ARM_Y_CENTER, (z_top + z_bot) / 2])
        clip = trimesh.boolean.union([ring, strut], engine="manifold")
    else:
        clip = ring
    return clip


def make_notches():
    """Subtract small rectangular notches at NOTCH_PERIOD intervals from the
    arm's underside."""
    notches = []
    half = ARM_TOTAL_LEN / 2 - 25
    n = int(half * 2 // NOTCH_PERIOD)
    start = -((n // 2) * NOTCH_PERIOD)
    for i in range(n + 1):
        x = start + i * NOTCH_PERIOD
        # Don't cut the area where the integrated clips sit
        if abs(x - (-CTC/2)) < 25 or abs(x - (+CTC/2)) < 30:
            continue
        if abs(x) > ARM_TOTAL_LEN/2 - 20:
            continue
        # Notch is centred under the arm at the lowest expected Z (around DIP_Z + something)
        notch = trimesh.creation.box(
            extents=[NOTCH_W_X, NOTCH_Y_W, NOTCH_DEPTH * 3]
        )
        # Position so the top of the notch is at arm bottom (rough estimate)
        # Place at z so notch goes from below arm into arm by NOTCH_DEPTH
        # The arm bottom at midline is around DIP_Z - ARM_RADIUS = DIP_Z - 6.5
        z_arm_bottom = DIP_Z - ARM_RADIUS + 1.0  # approximate
        notch.apply_translation([x, ARM_Y_CENTER,
                                 z_arm_bottom - (NOTCH_DEPTH * 3) / 2 + NOTCH_DEPTH])
        notches.append(notch)
    return notches


def make_hook():
    """Hook with a small tongue at the top that plugs into a notch, plus
    drop+J-curl below."""
    z_arm_bottom = DIP_Z - ARM_RADIUS + 1.0
    # Tongue
    tongue = trimesh.creation.box(
        extents=[HOOK_W_X, ARM_W_Y - 0.3, HOOK_NECK_H_Z]
    )
    tongue.apply_translation([HOOK_X_POS, ARM_Y_CENTER,
                              z_arm_bottom + HOOK_NECK_H_Z/2 - 0.5])
    # Body: vertical drop + J curl in YZ plane, extruded along X
    z_body_top = z_arm_bottom - 0.3
    pts = [(0, z_body_top), (0, z_body_top - HOOK_DROP)]
    cy = z_body_top - HOOK_DROP
    cx = HOOK_CURL_R
    n = 16
    for i in range(1, n + 1):
        a = math.radians(180 + 180 * i / n)
        pts.append((cx + HOOK_CURL_R * math.cos(a),
                    cy + HOOK_CURL_R * math.sin(a)))
    pts.append((2 * HOOK_CURL_R, cy + 6))
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
    body.apply_translation([HOOK_X_POS - HOOK_W_X/2, ARM_Y_CENTER, 0])
    return [tongue, body]


# ===== Build & write =========================================================
def main():
    arm = make_arm()
    clip_caño    = make_integrated_clip(FAUCET_OD, -CTC/2)
    clip_manilla = make_integrated_clip(HANDLE_OD, +CTC/2)

    # Union the arm with both clips first
    body = trimesh.boolean.union([arm, clip_caño, clip_manilla],
                                 engine="manifold")
    if not body.is_volume:
        body = trimesh.util.concatenate([arm, clip_caño, clip_manilla])

    # Subtract notches
    notches = make_notches()
    if notches:
        body_notched = trimesh.boolean.difference([body] + notches,
                                                  engine="manifold")
        if body_notched.is_volume:
            body = body_notched

    hook_parts = make_hook()

    printed_parts = [body] + hook_parts
    printed = trimesh.boolean.union(printed_parts, engine="manifold")
    if not printed.is_volume:
        printed = trimesh.util.concatenate(printed_parts)
    printed.export(OUT_FILE)

    scene = trimesh.Scene()
    scene.add_geometry(body, geom_name="arm_with_clips")
    for i, p in enumerate(hook_parts):
        scene.add_geometry(p, geom_name=f"hook_part_{i}")
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
