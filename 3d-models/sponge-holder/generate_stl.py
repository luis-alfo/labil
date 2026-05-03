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
import time
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

# --- Sponge pinch (clothespin-tips fork; replaces the old C-clip) ---
PINCH_GAP_TOP        = 14.0   # wider top: hinge zone, cap base
PINCH_GAP_BOTTOM     = 6.0    # narrow tips: where the actual pinch happens
PINCH_ARM_L          = 14.0   # vertical extent of the prongs (chosen after the
                              # 20mm vs 14mm A/B test — the short version won)
PINCH_LEN_Y          = 55.0   # along sponge top edge
PINCH_NUM_PRONGS     = 2      # only the extremes — middle of the sponge is
                              # left exposed to air for drying
PINCH_PRONG_W_BASE   = 8.0    # Y-width at the cap end (wide → strong root)
PINCH_PRONG_TIP_R    = 1.5    # rounding radius at the open mouth (no sharp
                              # corner; the prong tapers to a soft cylinder edge)
PINCH_WALL_T         = 3.0    # wall thickness in the X direction

# --- Reinforcement gusset at the clip → arm junction ---
GUSSET_H             = 8.0    # vertical extent down the clip outer face
GUSSET_W             = 10.0   # horizontal extent along the arm

ARC_SEG              = 96

OUT_FILE = Path(__file__).with_name("sponge_holder.stl")
OUT_3MF  = Path(__file__).with_name("sponge_holder.3mf")
WEB_DIR  = Path(__file__).resolve().parents[2] / "docs" / "models"
WEB_FILE = WEB_DIR / "sponge_holder.glb"


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


def update_web_version():
    """Bump the cache-buster string read by docs/index.html so mobile
    browsers fetch the freshly regenerated .glb instead of a cached copy."""
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    (WEB_DIR / "version.txt").write_text(str(int(time.time())))


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


def make_clip_arm_gusset():
    """Triangular gusset reinforcing the corner where the horizontal arm
    exits the clip ring. The arm carries the sponge weight as a cantilever,
    so the maximum bending moment is at this junction — without the gusset
    a hairline crack tends to start at the top-back of the clip ring on
    repeated loading. The gusset spreads the bending stress over a 8×10 mm
    triangle and into the lower half of the clip wall."""
    from shapely.geometry import Polygon as _Poly

    r_out = CLIP_INNER_D / 2 + WALL_T
    z_arm_bot = CLIP_HEIGHT / 2 - WALL_T   # bottom face of the arm
    # Triangle in XZ plane: starts at the corner (clip outer, arm bottom),
    # extends DOWN along the clip face by GUSSET_H, and OUT along the arm
    # bottom by GUSSET_W. Hypotenuse is the diagonal between those tips.
    poly = _Poly([
        (-r_out + CLIP_OVERLAP, z_arm_bot),
        (-r_out + CLIP_OVERLAP, z_arm_bot - GUSSET_H),
        (-r_out - GUSSET_W,     z_arm_bot),
    ])
    mesh = trimesh.creation.extrude_polygon(poly, height=ARM_WIDTH_Y)
    Rmat = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    mesh.apply_transform(Rmat)
    mesh.apply_translation([0, ARM_WIDTH_Y / 2, 0])
    return mesh


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
    """Sponge pinch: clothespin-tips fork-pinch with triangular prongs.
    The curved cap sits at the top, merged with the bottom of the drop
    strap. Sponge enters from below by pushing past the rounded narrow
    tips, expands into the wider zone above, and the spring-loaded
    prongs hold it in place."""
    pinch = build_fork_pinch(
        gap_top=PINCH_GAP_TOP,
        gap_bottom=PINCH_GAP_BOTTOM,
        arm_l=PINCH_ARM_L,
        total_y=PINCH_LEN_Y,
        num_prongs=PINCH_NUM_PRONGS,
        prong_w_base=PINCH_PRONG_W_BASE,
        tip_radius=PINCH_PRONG_TIP_R,
        wall_t=PINCH_WALL_T,
        curved_cap=True,
    )

    # Position so the drop strap's bottom face lands inside the SOLID part
    # of the curved cap (above the inner-hole boundary). z_local at the drop
    # bottom must be > half_l + cap_inner_R for a clean weld.
    drop_end_x, drop_end_z = drop_end_xz()
    half_l = PINCH_ARM_L / 2
    cap_inner_R = PINCH_GAP_TOP / 2
    z_local_at_drop = (half_l + cap_inner_R) + CLIP_OVERLAP
    pinch.apply_translation([drop_end_x, 0, drop_end_z - z_local_at_drop])
    return pinch


def build_c_clip(gap, wrap_deg, length_y):
    """Standalone C-clip primitive — axis along Y, mouth toward -Z,
    centred at the origin. Reused by the assembled piece and by the
    sponge-clip variant test scripts."""
    r_in = gap / 2
    r_out = r_in + WALL_T
    half_open = (360 - wrap_deg) / 2

    poly = partial_annulus(r_in, r_out, 90 + half_open, 450 - half_open)
    clip = trimesh.creation.extrude_polygon(poly, height=length_y)
    R = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])
    clip.apply_transform(R)
    clip.apply_translation([0, -length_y / 2, 0])
    return clip


def _build_triangular_prong(y_c, sign, half_top, half_bot, half_l,
                            x_top_outer, x_bot_outer,
                            prong_w_base, tip_radius):
    """One triangular prong: wide rectangle at the top (cap base, full
    `prong_w_base` Y-width) tapering down to a half-cylinder rounded tip
    of radius `tip_radius` at the bottom. Built as the convex hull of
    the corner vertices."""
    x_out_top = sign * x_top_outer
    x_in_top  = sign * half_top
    x_out_bot = sign * x_bot_outer
    x_in_bot  = sign * half_bot

    half_w = prong_w_base / 2
    R = tip_radius

    verts = [
        # Top rectangle (base; widest part, where cap connects)
        [x_out_top, y_c - half_w, +half_l],
        [x_in_top,  y_c - half_w, +half_l],
        [x_in_top,  y_c + half_w, +half_l],
        [x_out_top, y_c + half_w, +half_l],
    ]
    # Bottom rounded tip — half-cylinder of radius R, axis along X.
    # Sample the lower half-circle (theta 180° → 360°) at both X faces.
    n_arc = 9
    for x in (x_out_bot, x_in_bot):
        for i in range(n_arc):
            theta = math.radians(180 + 180 * i / (n_arc - 1))
            dy = R * math.cos(theta)
            dz = R * math.sin(theta)
            verts.append([x, y_c + dy, -half_l + R + dz])

    return trimesh.points.PointCloud(np.array(verts)).convex_hull


def build_fork_pinch(
    gap_top, gap_bottom, arm_l, total_y,
    num_prongs=2,
    prong_w_base=8.0,
    tip_radius=1.5,
    wall_t=None, curved_cap=True,
):
    """Fork-pinch with triangular prongs that taper from a wide base
    (cap end) to a rounded tip (open mouth). Wide base = stiff root,
    less prone to snapping; rounded tip = no stress-concentration corner.

    The two walls converge (gap_bottom at -Z = narrow tips; gap_top at
    +Z = wider hinge zone) and a half-cylinder arch caps the top.

                                +Z   ╭───── arch cap ─────╮
                                     ▲ wide       wide ▲       ← prong base
                                     │              │           (full prong_w_base)
                                     │              │
                                -Z   ▼ rounded tip ▼   ← rounded edge,
                                     ←─── total_y ───→     no sharp corner
    """
    t = WALL_T if wall_t is None else wall_t

    half_top = gap_top / 2
    half_bot = gap_bottom / 2
    half_l = arm_l / 2
    x_top_outer = half_top + t
    x_bot_outer = half_bot + t

    # Distribute prongs along Y. With 2 prongs we want them at the extremes.
    if num_prongs == 1:
        y_centres = [0.0]
    else:
        usable = total_y - prong_w_base
        y_centres = [
            -total_y / 2 + prong_w_base / 2 + i * usable / (num_prongs - 1)
            for i in range(num_prongs)
        ]

    parts = []
    for yc in y_centres:
        for sign in (-1, +1):
            parts.append(_build_triangular_prong(
                yc, sign, half_top, half_bot, half_l,
                x_top_outer, x_bot_outer,
                prong_w_base, tip_radius,
            ))

    if curved_cap:
        cap_poly = partial_annulus(half_top, x_top_outer, 0, 180)
        cap = trimesh.creation.extrude_polygon(cap_poly, height=total_y)
        Rmat = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
        cap.apply_transform(Rmat)
        cap.apply_translation([0, total_y / 2, half_l - CLIP_OVERLAP])
    else:
        cap = box(
            extents=[2 * x_top_outer, total_y, t],
            center=[0, 0, half_l + t / 2 - CLIP_OVERLAP / 2],
        )
    parts.append(cap)

    pinch = trimesh.boolean.union(parts, engine="manifold")
    if not pinch.is_volume:
        pinch = trimesh.util.concatenate(parts)
    return pinch


def build_parallel_pinch(gap, arm_l, length_y, wall_t=None):
    """Long-walled clothespin-style pinch — two parallel rectangular walls
    spaced `gap` apart in X, joined at the +Z end by a horizontal cap, open
    at -Z. Y axis runs along the sponge's top edge. Centred at the origin."""
    t = WALL_T if wall_t is None else wall_t

    half_g = gap / 2
    half_l = arm_l / 2

    left_wall = box(
        extents=[t, length_y, arm_l],
        center=[-(half_g + t / 2), 0, 0],
    )
    right_wall = box(
        extents=[t, length_y, arm_l],
        center=[+(half_g + t / 2), 0, 0],
    )
    cap = box(
        extents=[gap + 2 * t, length_y, t],
        center=[0, 0, half_l + t / 2 - CLIP_OVERLAP / 2],
    )
    pinch = trimesh.boolean.union([left_wall, right_wall, cap], engine="manifold")
    if not pinch.is_volume:
        pinch = trimesh.util.concatenate([left_wall, right_wall, cap])
    return pinch


# ============================================================================
# Build & write
# ============================================================================
def main():
    parts = [
        make_faucet_clip(),
        make_clip_arm_gusset(),
        make_arm_drop(),
        make_sponge_clip(),
    ]
    holder = trimesh.boolean.union(parts, engine="manifold")
    if not holder.is_volume:
        holder = trimesh.util.concatenate(parts)

    holder.export(OUT_FILE)
    holder.export(OUT_3MF)
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    holder.export(WEB_FILE)
    update_web_version()

    bbox_min, bbox_max = holder.bounds
    size = bbox_max - bbox_min
    print(f"Wrote {OUT_FILE}")
    print(f"Wrote {OUT_3MF}")
    print(f"Wrote {WEB_FILE}  (web viewer)")
    print(f"Triangles: {len(holder.faces)}")
    print(f"Bounding box (mm): X {size[0]:.1f}  Y {size[1]:.1f}  Z {size[2]:.1f}")
    print(f"Volume:    {holder.volume / 1000:.1f} cm³  (manifold={holder.is_volume})")


if __name__ == "__main__":
    main()
