#!/usr/bin/env python3
"""Generate sponge_holder.stl as a 3D model.

Geometry overview (right-handed coords, Z = up):

    Z
    |    +---+
    |    | C |  <- faucet clip (axis = Z, lies horizontal)
    |    +---+      inner Ø 45 mm, snap-on with pinch
    |       \
    |        \--- horizontal arm "por detrás" of the faucet ---+
    |                                                           |
    |                                                           |  90° drop
    |                                                           |
    |                                                       +---+---+
    |                                                       | (((  | <- sponge clip
    |                                                       +---+---+   (axis Y, mouth -Z)
    |                                                           v
    |                                                       sponge hangs vertically
    |                                                       (its top edge is pinched)
    +----------------> X

The sponge hangs vertically from the C-clip, which grips its top edge by
compressing the < 20 mm inner gap onto the sponge thickness.

Run:    python3 generate_stl.py
Output: sponge_holder.stl
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString

# ============================================================================
# Parameters (mm)
# ============================================================================
WALL_T               = 4.0    # plastic wall thickness everywhere

# --- Faucet clip ---
CLIP_INNER_D         = 45.4   # 45 mm shaft + 0.4 mm fit tolerance for PLA
CLIP_HEIGHT          = 22.0   # along Z (axis of the ring)
CLIP_WRAP_DEG        = 240.0  # PLA-friendly snap (smaller wrap = more flex)
CLIP_OVERLAP         = 0.6    # tiny overlap so booleans weld cleanly

# --- Horizontal arm "por detrás" ---
ARM_LEN              = 30.0   # horizontal centerline length (clip → arc start)
ARM_WIDTH_Y          = 24.0   # uniform width along Y for the swept arm-elbow-drop

# --- 90° fillet (elbow) ---
ELBOW_R              = 8.0    # centerline radius of the bend (more = more elegant)

# --- Vertical drop ---
DROP_LEN             = 18.0   # vertical centerline length (arc end → bottom)

# --- Sponge clip (C-clip, axis Y, mouth -Z; the sponge top edge is pinched) ---
SPONGE_GAP           = 14.0   # inner gap < 20 mm: pinches the sponge thickness
SPONGE_CLIP_LEN_Y    = 50.0   # length along the sponge's top edge
SPONGE_CLIP_WRAP_DEG = 220.0  # less wrap → flexes well in PLA

ARC_SEG              = 96

OUT_FILE = Path(__file__).with_name("sponge_holder.stl")


# ============================================================================
# Helpers
# ============================================================================
def partial_annulus(r_in: float, r_out: float,
                    a_start_deg: float, a_end_deg: float,
                    segments: int = ARC_SEG) -> Polygon:
    """2D polygon: annulus arc going CCW from a_start_deg to a_end_deg."""
    a0, a1 = math.radians(a_start_deg), math.radians(a_end_deg)
    angles = np.linspace(a0, a1, segments)
    outer = [(r_out * math.cos(a), r_out * math.sin(a)) for a in angles]
    inner = [(r_in  * math.cos(a), r_in  * math.sin(a)) for a in angles[::-1]]
    return Polygon(outer + inner)


def box(extents, center):
    m = trimesh.creation.box(extents=list(extents))
    m.apply_translation(list(center))
    return m


# ============================================================================
# Parts
# ============================================================================
def make_faucet_clip():
    """Partial cylinder, axis along Z, mouth opens on +X side."""
    r_in  = CLIP_INNER_D / 2
    r_out = r_in + WALL_T
    half_open = (360 - CLIP_WRAP_DEG) / 2
    # arc CCW from +half_open through 180° back around to (360 - half_open)
    poly = partial_annulus(r_in, r_out, half_open, 360 - half_open)
    clip = trimesh.creation.extrude_polygon(poly, height=CLIP_HEIGHT)
    clip.apply_translation([0, 0, -CLIP_HEIGHT / 2])
    return clip


def arm_drop_centerline():
    """(x, z) keypoints of the arm + 90° fillet + drop centerline."""
    r_out = CLIP_INNER_D / 2 + WALL_T
    z_arm = CLIP_HEIGHT / 2 - WALL_T / 2

    pts = []
    # arm start (slightly inside clip wall so the boolean welds cleanly)
    x_arm_start = -r_out + CLIP_OVERLAP
    pts.append((x_arm_start, z_arm))
    # arc start (end of arm)
    x_corner = x_arm_start - ARM_LEN
    pts.append((x_corner, z_arm))
    # quarter-circle CCW from angle 90° to 180° around (x_corner, z_arm - ELBOW_R)
    cx, cz = x_corner, z_arm - ELBOW_R
    n_arc = 28
    for i in range(1, n_arc + 1):
        a = math.radians(90 + 90 * i / n_arc)
        pts.append((cx + ELBOW_R * math.cos(a), cz + ELBOW_R * math.sin(a)))
    # drop end
    arc_end_x, arc_end_z = cx - ELBOW_R, cz
    pts.append((arc_end_x, arc_end_z - DROP_LEN))
    return pts


def drop_end_xz():
    """Convenience: (x, z) of the drop centerline's lowest point."""
    return arm_drop_centerline()[-1]


def make_arm_drop():
    """Smooth swept solid: arm + 90° fillet + drop, all one continuous piece.

    Built by taking the centerline polyline in the XZ plane, buffering it by
    WALL_T/2 in shapely (so the corners get the fillet for free), and then
    extruding the resulting 2D polygon along Y.
    """
    pts = arm_drop_centerline()
    line = LineString(pts)
    poly = line.buffer(WALL_T / 2, cap_style=2, join_style=2)

    mesh = trimesh.creation.extrude_polygon(poly, height=ARM_WIDTH_Y)
    # The polygon was given in (x, z) of the design frame but shapely / extrude
    # treat the 2D as XY and extrude along +Z. Rotate so the polygon's "Y"
    # becomes design Z and the extrusion direction becomes design Y.
    R = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    mesh.apply_transform(R)
    mesh.apply_translation([0, ARM_WIDTH_Y / 2, 0])  # centre on Y=0
    return mesh


def make_sponge_clip():
    """C-clip with axis along Y. Mouth opens -Z so the user pushes the
    sponge up into the clip from below; the clip's <20 mm inner gap pinches
    the sponge thickness."""
    r_in  = SPONGE_GAP / 2
    r_out = r_in + WALL_T
    half_open = (360 - SPONGE_CLIP_WRAP_DEG) / 2

    # In local 2D frame: mouth on +Y (angle 90°). Arc covers 90+half CCW
    # through 180, 270, 360, back to 90-half (= 450-half).
    poly = partial_annulus(r_in, r_out, 90 + half_open, 450 - half_open)
    clip = trimesh.creation.extrude_polygon(poly, height=SPONGE_CLIP_LEN_Y)
    # extruded along +Z. Rotate by -90° around +X: sends +Y mouth to -Z and
    # the +Z extrusion axis to +Y, which is what we want.
    R = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])
    clip.apply_transform(R)
    # extrusion now spans Y in [0, SPONGE_CLIP_LEN_Y]; center it
    clip.apply_translation([0, -SPONGE_CLIP_LEN_Y / 2, 0])

    # Position so the +Z top of the outer surface meets the bottom of the drop.
    drop_end_x, drop_end_z = drop_end_xz()
    # the drop's flat cap is at z = drop_end_z; we want the sponge clip's
    # +Z outer to coincide (with a tiny overlap for clean booleans)
    clip.apply_translation([
        drop_end_x,
        0,
        drop_end_z - r_out + CLIP_OVERLAP,
    ])
    return clip


# ============================================================================
# Build & write
# ============================================================================
def main():
    parts = [make_faucet_clip(), make_arm_drop(), make_sponge_clip()]
    holder = trimesh.boolean.union(parts, engine="manifold")
    if not holder.is_volume:
        holder = trimesh.util.concatenate(parts)

    holder.export(OUT_FILE)

    bbox_min, bbox_max = holder.bounds
    size = bbox_max - bbox_min
    print(f"Wrote {OUT_FILE}")
    print(f"Triangles: {len(holder.faces)}")
    print(f"Bounding box (mm): X {size[0]:.1f}  Y {size[1]:.1f}  Z {size[2]:.1f}")
    print(f"Volume:    {holder.volume / 1000:.1f} cm³  (manifold={holder.is_volume})")


if __name__ == "__main__":
    main()
