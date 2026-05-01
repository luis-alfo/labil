#!/usr/bin/env python3
"""Generate sponge_holder.stl as a true 3D model.

Geometry overview (right-handed coords, Z = up):

    Z
    |    +---+
    |    | C |  <- clip (axis = Z), wraps a vertical element of the faucet
    |    +---+      (parallel to the floor: it lies in the horizontal plane)
    |       \
    |        \--- horizontal arm ----+
    |                                 |
    |                                 |  <- vertical drop (the "giro" of 90°)
    |                                 |
    |                  +--------------+   <- cradle back wall
    |                  |                  (sponge stands here, vertically)
    |                  |   sponge
    |                  |     ^
    |                  |     |
    |                  +-----+   <- cradle bottom
    |                        |
    |                        +-- front lip
    +----------------> X

The clip pinches a faucet element of less than 20mm diameter; the cradle is
wider than the clip so the sponge fits comfortably.

Run:   python3 generate_stl.py
Output: sponge_holder.stl
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon

# ============================================================================
# Parameters (mm) — all editable
# ============================================================================
WALL_T          = 4.0     # plastic wall thickness everywhere

# --- Clip (the "pinza", axis vertical, lies in the horizontal plane) ---
CLIP_INNER_D    = 18.0    # < 20 mm so it pinches firmly. Measure your faucet.
CLIP_HEIGHT     = 18.0    # how tall the clip ring is (along Z)
CLIP_WRAP_DEG   = 280.0   # ring coverage (>180 → snap-on with pinch)
CLIP_OVERLAP    = 0.6     # tiny overlap with the arm so booleans weld cleanly

# --- Horizontal arm (continues the clip's plane, parallel to floor) ---
ARM_LEN         = 30.0    # how far the arm reaches before the 90° bend
ARM_WIDTH_Y     = 18.0    # arm width along Y

# --- Vertical drop (the "giro": from horizontal to vertical) ---
DROP_LEN        = 22.0

# --- Cradle (U opening upward; sponge stands vertically inside it) ---
CRADLE_WIDTH_Y  = 30.0    # wider than the clip — the sponge sits across this
CRADLE_BACK_H   = 80.0    # back-wall height (vertical)
CRADLE_BOT_LEN  = 32.0    # bottom length (≈ sponge thickness + walls)
CRADLE_FRONT_H  = 37.0    # front lip — keeps the sponge from falling out

ARC_SEG         = 96      # cylinder smoothness

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
def make_clip():
    """Partial cylinder, axis along Z, mouth opens on +X side."""
    r_in  = CLIP_INNER_D / 2
    r_out = r_in + WALL_T
    half_open = (360 - CLIP_WRAP_DEG) / 2
    # arc goes CCW from +half_open all the way around to (360 - half_open)
    poly = partial_annulus(r_in, r_out, half_open, 360 - half_open)
    clip = trimesh.creation.extrude_polygon(poly, height=CLIP_HEIGHT)
    # Default extrudes from z=0 upwards. Centre vertically on z=0:
    clip.apply_translation([0, 0, -CLIP_HEIGHT / 2])
    return clip


def make_arm():
    """Horizontal arm exits clip on -X side (opposite the mouth)."""
    r_out = CLIP_INNER_D / 2 + WALL_T
    # arm sits on top of the ring, lying flat
    z_top = CLIP_HEIGHT / 2
    z_bot = z_top - WALL_T
    x_start = -r_out + CLIP_OVERLAP        # overlaps the ring
    x_end   = -r_out - ARM_LEN
    return box(
        extents=[abs(x_end - x_start), ARM_WIDTH_Y, WALL_T],
        center=[(x_start + x_end) / 2, 0, (z_top + z_bot) / 2],
    )


def make_drop():
    """Vertical drop strap from end of arm, widening to cradle width."""
    r_out = CLIP_INNER_D / 2 + WALL_T
    x_arm_end = -r_out - ARM_LEN
    z_arm_bot = CLIP_HEIGHT / 2 - WALL_T
    # the strap's +X face aligns with the arm end
    return box(
        extents=[WALL_T, CRADLE_WIDTH_Y, DROP_LEN + CLIP_OVERLAP],
        center=[
            x_arm_end - WALL_T / 2,
            0,
            z_arm_bot - DROP_LEN / 2 + CLIP_OVERLAP / 2,
        ],
    )


def make_cradle():
    """U-shape opening upward, sponge stands vertically inside."""
    r_out = CLIP_INNER_D / 2 + WALL_T
    x_back = -r_out - ARM_LEN - WALL_T          # outer face of drop / back wall
    z_drop_bot = CLIP_HEIGHT / 2 - WALL_T - DROP_LEN

    parts = []

    # --- Back wall (vertical, continues the drop) ---
    back = box(
        extents=[WALL_T, CRADLE_WIDTH_Y, CRADLE_BACK_H + CLIP_OVERLAP],
        center=[
            x_back + WALL_T / 2,
            0,
            z_drop_bot - CRADLE_BACK_H / 2 + CLIP_OVERLAP / 2,
        ],
    )
    parts.append(back)

    # --- Bottom (horizontal, extends in -X direction) ---
    z_bottom_top = z_drop_bot - CRADLE_BACK_H
    bottom = box(
        extents=[CRADLE_BOT_LEN + CLIP_OVERLAP, CRADLE_WIDTH_Y, WALL_T],
        center=[
            x_back - CRADLE_BOT_LEN / 2 + CLIP_OVERLAP / 2,
            0,
            z_bottom_top - WALL_T / 2,
        ],
    )
    parts.append(bottom)

    # --- Front lip (vertical, at -X end of bottom) ---
    x_front = x_back - CRADLE_BOT_LEN
    front = box(
        extents=[WALL_T, CRADLE_WIDTH_Y, CRADLE_FRONT_H + CLIP_OVERLAP],
        center=[
            x_front + WALL_T / 2,
            0,
            z_bottom_top - WALL_T + CRADLE_FRONT_H / 2 + CLIP_OVERLAP / 2,
        ],
    )
    parts.append(front)

    return trimesh.util.concatenate(parts)


# ============================================================================
# Build & write
# ============================================================================
def main():
    parts = [make_clip(), make_arm(), make_drop(), make_cradle()]
    # Boolean union so the slicer sees a single closed shell.
    holder = trimesh.boolean.union(parts, engine="manifold")
    if not holder.is_volume:
        # fallback: just concatenate (slicers usually still cope)
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
