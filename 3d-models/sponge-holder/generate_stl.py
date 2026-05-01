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
from shapely.geometry import Polygon

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
ARM_LEN              = 30.0   # how far the arm reaches before the 90° turn
ARM_WIDTH_Y          = 22.0

# --- Vertical drop ---
DROP_LEN             = 22.0
DROP_WIDTH_Y         = 30.0   # transitions to the sponge clip width

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


def make_arm():
    """Horizontal arm 'por detrás' (-X side, opposite the mouth)."""
    r_out = CLIP_INNER_D / 2 + WALL_T
    x_start = -r_out + CLIP_OVERLAP
    x_end   = -r_out - ARM_LEN
    z_top   = CLIP_HEIGHT / 2
    z_bot   = z_top - WALL_T
    return box(
        extents=[abs(x_end - x_start), ARM_WIDTH_Y, WALL_T],
        center=[(x_start + x_end) / 2, 0, (z_top + z_bot) / 2],
    )


def make_drop():
    """Vertical drop strap from end of arm down to the sponge clip."""
    r_out = CLIP_INNER_D / 2 + WALL_T
    x_arm_end = -r_out - ARM_LEN
    z_arm_bot = CLIP_HEIGHT / 2 - WALL_T
    return box(
        extents=[WALL_T, DROP_WIDTH_Y, DROP_LEN + CLIP_OVERLAP],
        center=[
            x_arm_end - WALL_T / 2,
            0,
            z_arm_bot - DROP_LEN / 2 + CLIP_OVERLAP / 2,
        ],
    )


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
    r_out_faucet = CLIP_INNER_D / 2 + WALL_T
    x_drop_center = -r_out_faucet - ARM_LEN - WALL_T / 2
    z_drop_bot    = CLIP_HEIGHT / 2 - WALL_T - DROP_LEN
    clip.apply_translation([
        x_drop_center,
        0,
        z_drop_bot - r_out + CLIP_OVERLAP,
    ])
    return clip


# ============================================================================
# Build & write
# ============================================================================
def main():
    parts = [make_faucet_clip(), make_arm(), make_drop(), make_sponge_clip()]
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
