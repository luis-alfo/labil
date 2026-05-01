#!/usr/bin/env python3
"""Generate sponge_holder.stl by sweeping a rectangular cross-section
along a 2D centerline (XZ plane) and extruding it in Y.

The geometry follows the dimensions sketched on the photo:
    50mm hook wrap, 57mm vertical span on faucet, 55mm cradle bottom,
    37mm front lip, 80mm cradle back wall.

Run:   python3 generate_stl.py
Output: sponge_holder.stl  (binary)
"""

from __future__ import annotations

import os
import math
from pathlib import Path

import numpy as np
from stl import mesh as stl_mesh


# ====== Parameters (mm) ======
FAUCET_D        = 32.0   # faucet shaft diameter where the hook clips
STRAP_T         = 4.0    # plastic thickness
STRAP_W         = 28.0   # strap width (Y depth)
HOOK_WRAP_DEG   = 220.0  # >180 makes it a snap-on clip

DESCENT_H       = 30.0   # vertical drop from hook end to cradle arm
ARM_L           = 50.0   # horizontal arm from descent to cradle
CRADLE_BACK_H   = 80.0   # cradle back wall (vertical)
CRADLE_BOTTOM_L = 55.0   # cradle bottom (horizontal)
CRADLE_FRONT_H  = 37.0   # cradle front lip (vertical, holds sponge in)

HOOK_STEPS      = 48

OUT_FILE = Path(__file__).with_name("sponge_holder.stl")


# ---------- helpers ----------
def arc(center, radius, a_start_deg, a_end_deg, steps):
    cx, cz = center
    out = []
    for i in range(steps + 1):
        t = i / steps
        a = math.radians(a_start_deg + (a_end_deg - a_start_deg) * t)
        out.append((cx + radius * math.cos(a), cz + radius * math.sin(a)))
    return out


def build_centerline():
    """Sharp-corner centerline. The miter offset at the corner gives the
    outer rounding for free; sharp inside corners are intentional and act
    as cradle-floor edges."""
    pts = []

    # 1. Hook arc around faucet (wrap > 180° for snap fit), CW from back to front
    extra = (HOOK_WRAP_DEG - 180.0) / 2.0
    a_back  = 180.0 + extra
    a_front = -extra
    R_c     = FAUCET_D / 2 + STRAP_T / 2
    pts.extend(arc((0, 0), R_c, a_back, a_front, HOOK_STEPS))

    # 2. Vertical descent (sharp corner)
    last = pts[-1]
    pts.append((last[0], last[1] - DESCENT_H))

    # 3. Horizontal arm
    last = pts[-1]
    pts.append((last[0] + ARM_L, last[1]))

    # 4. Cradle back wall (down)
    last = pts[-1]
    pts.append((last[0], last[1] - CRADLE_BACK_H))

    # 5. Cradle bottom (right)
    last = pts[-1]
    pts.append((last[0] + CRADLE_BOTTOM_L, last[1]))

    # 6. Front lip (up)
    last = pts[-1]
    pts.append((last[0], last[1] + CRADLE_FRONT_H))

    # de-duplicate consecutive identical points
    cleaned = [pts[0]]
    for p in pts[1:]:
        if (p[0] - cleaned[-1][0]) ** 2 + (p[1] - cleaned[-1][1]) ** 2 > 1e-8:
            cleaned.append(p)
    return cleaned


def offset_polyline(points, t):
    """Compute miter-joined left/right offsets at distance t from centerline."""
    pts = [np.array(p, dtype=float) for p in points]
    n = len(pts)
    # segment unit directions and outward (left) normals
    dirs    = [pts[i + 1] - pts[i] for i in range(n - 1)]
    dirs    = [d / np.linalg.norm(d) for d in dirs]
    normals = [np.array([-d[1], d[0]]) for d in dirs]   # rotate +90°

    left, right = [], []
    for i in range(n):
        if i == 0:
            m = normals[0]
        elif i == n - 1:
            m = normals[-1]
        else:
            n1, n2 = normals[i - 1], normals[i]
            denom = 1.0 + float(np.dot(n1, n2))
            if denom < 1e-6:
                m = n1
            else:
                m = (n1 + n2) / denom
        left.append(pts[i] + t * m)
        right.append(pts[i] - t * m)
    return left, right


def build_mesh(centerline):
    left, right = offset_polyline(centerline, STRAP_T / 2)
    n = len(centerline)
    half_w = STRAP_W / 2

    def v(p2d, y):
        return [float(p2d[0]), float(y), float(p2d[1])]

    triangles = []

    # Top (+Y) and bottom (-Y) faces, segment by segment.
    # Each segment forms a quad: left[i], left[i+1], right[i+1], right[i]
    for i in range(n - 1):
        L0, L1 = left[i],  left[i + 1]
        R0, R1 = right[i], right[i + 1]
        # Top face — outward normal +Y, CCW when viewed from +Y
        triangles.append([v(L0, +half_w), v(R0, +half_w), v(R1, +half_w)])
        triangles.append([v(L0, +half_w), v(R1, +half_w), v(L1, +half_w)])
        # Bottom face — outward normal -Y, reversed winding
        triangles.append([v(L0, -half_w), v(R1, -half_w), v(R0, -half_w)])
        triangles.append([v(L0, -half_w), v(L1, -half_w), v(R1, -half_w)])

    # Side walls along the LEFT polyline (outer edge of the strap on +normal side)
    for i in range(n - 1):
        A, B = left[i], left[i + 1]
        # quad: A_top, B_top, B_bot, A_bot ; outward normal points +n direction
        triangles.append([v(A, +half_w), v(B, -half_w), v(B, +half_w)])
        triangles.append([v(A, +half_w), v(A, -half_w), v(B, -half_w)])

    # Side walls along the RIGHT polyline (reverse winding)
    for i in range(n - 1):
        A, B = right[i], right[i + 1]
        triangles.append([v(A, +half_w), v(B, +half_w), v(B, -half_w)])
        triangles.append([v(A, +half_w), v(B, -half_w), v(A, -half_w)])

    # End caps (start: between left[0] and right[0]; end: between left[-1] and right[-1])
    L0, R0 = left[0], right[0]
    LN, RN = left[-1], right[-1]
    # start cap (pointing opposite to first tangent)
    triangles.append([v(L0, -half_w), v(R0, -half_w), v(R0, +half_w)])
    triangles.append([v(L0, -half_w), v(R0, +half_w), v(L0, +half_w)])
    # end cap
    triangles.append([v(LN, +half_w), v(RN, +half_w), v(RN, -half_w)])
    triangles.append([v(LN, +half_w), v(RN, -half_w), v(LN, -half_w)])

    return triangles


def write_stl(triangles, path):
    data = np.zeros(len(triangles), dtype=stl_mesh.Mesh.dtype)
    for i, tri in enumerate(triangles):
        for j in range(3):
            data["vectors"][i][j] = tri[j]
    m = stl_mesh.Mesh(data)
    m.save(str(path))


def main():
    cl = build_centerline()
    tris = build_mesh(cl)
    write_stl(tris, OUT_FILE)
    bb_min = np.min([t for tri in tris for t in tri], axis=0)
    bb_max = np.max([t for tri in tris for t in tri], axis=0)
    size = bb_max - bb_min
    print(f"Wrote {OUT_FILE}")
    print(f"Triangles: {len(tris)}")
    print(f"Bounding box (mm): X {size[0]:.1f}  Y {size[1]:.1f}  Z {size[2]:.1f}")


if __name__ == "__main__":
    main()
