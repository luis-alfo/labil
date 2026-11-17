#!/usr/bin/env python3
"""Barra modular de baño — "Trazo".

One flat PLA stroke that hangs from the wall-mounted faucet: it runs
horizontally above the caño (Ø29) and the manilla (Ø42), drops a snap loop
over each, and extends one hand-span to each side, ending in a slight
upward curve. Interchangeable hooks ("jinetes") ride on its top edge.

Why it is shaped like this (what the previous A/B/C proposals got wrong):

* Load path. The loops open DOWNWARDS, so hanging weight presses the solid
  top of each loop onto its cylinder. The snap arms only have to resist the
  uplift that an unbalanced load creates at the far cylinder.
* Print orientation. Every part is a 2D profile extruded 8 mm, printed flat
  with no supports. Layers lie in the plane of both the snap flex and the
  arm bending, which is the strong direction for PLA.
* Bed size. The stroke is split in the middle, between the two cylinders,
  with a dovetail. Each half fits diagonally on a 235 mm bed.
* Moving parts. The whole part lives in the 8 mm next to the wall, behind
  the handle's moving cap and behind the lever.

Frame (mm): x right as seen from the front, y out of the wall, z up,
origin midway between the two cylinder axes. See ../_bathroom_context.py.

Run:  python3 generate_stl.py
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _bathroom_context import (MAT_PLA, MAT_PLA_2, export_glb,  # noqa: E402
                               make_context_meshes, paint)

# ============================================================================
# Parameters (mm)
# ============================================================================
# --- measured by the user ---
FAUCET_OD      = 29.0    # caño
HANDLE_OD      = 42.0    # manilla (must be the FIXED sleeve next to the wall)
GAP_EDGE       = 49.0    # edge to edge between both cylinders
CTC            = FAUCET_OD / 2 + GAP_EDGE + HANDLE_OD / 2      # 84.5

# --- assumed from the photos: confirm with the test pieces ---
WALL_GAP       = 3.5     # chrome flange thickness; the part rests against it
DEPTH          = 8.0     # extrusion depth; cylinders expose 15-20 mm

# --- snap loops (mouth down) ---
FIT            = 0.3     # diametral clearance for PLA
CANO_T         = 3.4     # radial wall of the caño loop
CANO_WRAP      = 230.0   # degrees of wrap; mouth = 360 - wrap, centred at 6h
MANI_T         = 3.6
MANI_WRAP      = 232.0
NECK_W         = 11.0    # caño loop hangs from the line by a neck this wide

# --- the line ---
LINE_Z0        = 22.0    # bottom edge of the line above the cylinder axes
LINE_H         = 14.0    # height of the line between and beside the loops
LINE_H_TIP     = 6.0     # height at the tips (tapers along each arm)
ARM_LEN        = 200.0   # "un palmo" beyond each cylinder axis
ROOT_X         = CTC / 2 + 32.0   # where the taper starts
TIP_LEN        = 34.0    # horizontal length of the upturned end
TIP_RISE       = 9.0     # how much the end rises: the "sutil curva"
FILLET         = 1.5

# --- dovetail joint in the middle ---
BELLY_HALF_W   = 22.0    # the line swells downwards here to house the joint
BELLY_DROP     = 12.0    # depth of that swell at the centre
TAIL_LEN       = 8.0
TAIL_NECK      = 7.0     # dovetail height at the joint face
TAIL_HEAD      = 12.0    # dovetail height at its end
JOINT_CLEAR    = 0.10    # per side; tighten to 0.05 if the joint has play

# --- jinetes (interchangeable hooks that ride on the line's top edge) ---
RIDER_FIT      = 0.2     # total play across the 8 mm line (snug slide)
RIDER_BACK_T   = 2.0     # leg between line and wall (WALL_GAP must exceed it)
RIDER_BACK_LEG = 7.0     # short: the line is only LINE_H_TIP tall at the tips
RIDER_FRONT_T  = 3.2
RIDER_BRIDGE_T = 3.2
RIDER_LEG      = 9.0
HOOK_W         = 14.0    # gancho: width along the line
HOOK_DROP      = 14.0
HOOK_R         = 9.0
SHELF_W        = 56.0    # repisa: width along the line
SHELF_DEPTH    = 40.0
SHELF_LIP      = 9.0
PLATE_W        = 30.0    # horquilla / aro: width along the line
PLATE_T        = 3.6
FORK_REACH     = 30.0
FORK_SLOT      = 8.0     # neck of a toothbrush / brush head
RING_ID        = 62.0    # hairdryer barrel: MEASURE YOURS
RING_WALL      = 5.0

ARC_SEG        = 96
Z_TOP          = LINE_Z0 + LINE_H
X_TIP          = CTC / 2 + ARM_LEN

HERE     = Path(__file__).resolve().parent
WEB_DIR  = HERE.parents[1] / "docs" / "models"


# ============================================================================
# 2D profile of the stroke (x, z)
# ============================================================================
def loop_polygon(cx: float, od: float, t: float, wrap: float) -> Polygon:
    """C-shaped loop around a cylinder at (cx, 0); mouth centred at 6 o'clock."""
    r_in = (od + FIT) / 2
    r_out = r_in + t
    half_mouth = (360 - wrap) / 2
    a0, a1 = -90 + half_mouth, 270 - half_mouth
    ang = np.radians(np.linspace(a0, a1, ARC_SEG))
    outer = [(cx + r_out * math.cos(a), r_out * math.sin(a)) for a in ang]
    inner = [(cx + r_in * math.cos(a), r_in * math.sin(a)) for a in ang[::-1]]
    loop = Polygon(outer + inner)
    r_mid = r_in + t / 2
    tips = [Point(cx + r_mid * math.cos(math.radians(a)),
                  r_mid * math.sin(math.radians(a))).buffer(t / 2)
            for a in (a0, a1)]          # rounded tips double as lead-in
    return unary_union([loop] + tips)


def arm_polygon(sign: int) -> Polygon:
    """Tapered arm with a level top edge and an upturned tip."""
    x_s = X_TIP - TIP_LEN                     # where the upturn starts
    samples = []                               # (x, z, radius)
    for x in np.linspace(ROOT_X - 2, x_s, 60):
        k = max(0.0, (x - ROOT_X) / (x_s - ROOT_X))
        h = LINE_H + (LINE_H_TIP - LINE_H) * k
        samples.append((x, Z_TOP - h / 2, h / 2))
    phi = 2 * math.atan2(TIP_RISE, TIP_LEN)
    radius = TIP_LEN / math.sin(phi)
    z_s = Z_TOP - LINE_H_TIP / 2
    for a in np.linspace(0, phi, 24)[1:]:
        samples.append((x_s + radius * math.sin(a),
                        z_s + radius * (1 - math.cos(a)),
                        LINE_H_TIP / 2))
    discs = [Point(sign * x, z).buffer(r, 24) for x, z, r in samples]
    return unary_union([unary_union([a, b]).convex_hull
                        for a, b in zip(discs[:-1], discs[1:])])


def belly_bottom(x: float) -> float:
    """Lower edge of the line between the loops: a smooth swell that gives
    the dovetail enough material without looking like an added block."""
    if abs(x) >= BELLY_HALF_W:
        return LINE_Z0
    return LINE_Z0 - BELLY_DROP * math.cos(math.pi * x / (2 * BELLY_HALF_W)) ** 2


def stroke_profile() -> Polygon:
    """The whole line, both loops included, before it is split in two."""
    xc, xm = -CTC / 2, +CTC / 2
    band = sbox(-ROOT_X, LINE_Z0, ROOT_X, Z_TOP)
    xs = np.linspace(-BELLY_HALF_W, BELLY_HALF_W, 81)
    belly = Polygon([(x, belly_bottom(x)) for x in xs]
                    + [(BELLY_HALF_W, Z_TOP), (-BELLY_HALF_W, Z_TOP)])
    cano_r_mid = (FAUCET_OD + FIT) / 2 + CANO_T / 2
    neck = sbox(xc - NECK_W / 2, cano_r_mid, xc + NECK_W / 2, LINE_Z0 + 1)
    parts = [band, belly, neck,
             arm_polygon(-1), arm_polygon(+1),
             loop_polygon(xc, FAUCET_OD, CANO_T, CANO_WRAP),
             loop_polygon(xm, HANDLE_OD, MANI_T, MANI_WRAP)]
    profile = unary_union(parts)
    profile = profile.buffer(FILLET).buffer(-FILLET)   # fillet inside corners
    assert profile.geom_type == "Polygon", profile.geom_type
    return profile


def dovetail() -> Polygon:
    zc = (belly_bottom(TAIL_LEN) + Z_TOP) / 2
    tail = Polygon([(-1.0, zc - TAIL_NECK / 2), (TAIL_LEN, zc - TAIL_HEAD / 2),
                    (TAIL_LEN, zc + TAIL_HEAD / 2), (-1.0, zc + TAIL_NECK / 2)])
    return tail.buffer(-0.7).buffer(0.7)               # soften the corners


def split_profile(profile: Polygon):
    """Left half carries the dovetail, right half the socket."""
    big = 1000
    tail = dovetail()
    left = profile.intersection(sbox(-big, -big, 0, big)).union(tail)
    right = profile.intersection(sbox(JOINT_CLEAR, -big, big, big))
    right = right.difference(tail.buffer(JOINT_CLEAR))
    # No sharp corners in the joint: fillet the tail root on the left half,
    # and round the socket (mouth and bottom) to match on the right half.
    left = left.buffer(0.6).buffer(-0.6)
    right = right.buffer(-0.6).buffer(0.6).buffer(0.5).buffer(-0.5)
    assert left.geom_type == right.geom_type == "Polygon"
    return left, right


# ============================================================================
# 3D parts. "Print" orientation = as it sits on the bed (z up, flat).
# ============================================================================
def extrude(poly: Polygon, height: float) -> "trimesh.Trimesh":
    # Chained buffers leave near-duplicate vertices that break triangulation.
    poly = poly.simplify(0.01, preserve_topology=True).buffer(0)
    mesh = trimesh.creation.extrude_polygon(poly, height=height)
    if not mesh.is_volume:
        mesh.merge_vertices()
        mesh.update_faces(mesh.nondegenerate_faces())
        trimesh.repair.fix_normals(mesh)
    assert mesh.is_volume, "extrusion is not a closed volume"
    return mesh


# Flat profile (x, z) extruded along +depth  →  installed on the wall.
STROKE_TO_WALL = np.array([[1, 0, 0, 0],
                           [0, 0, 1, WALL_GAP],
                           [0, 1, 0, 0],
                           [0, 0, 0, 1]], dtype=float)


def side_rider_to_local(width: float):
    """Profile (y, z) extruded along x  →  rider frame (x centred on rider)."""
    return np.array([[0, 0, 1, -width / 2],
                     [1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 0, 1]], dtype=float)


def rider_saddle(leg: float = RIDER_LEG, bridge_t: float = RIDER_BRIDGE_T):
    """U that drops over the line. Rider frame: y = 0 at the line's back
    face, z = 0 at the line's top edge. Returns (profile, y of front face)."""
    c = RIDER_FIT / 2
    y_back0, y_back1 = -c - RIDER_BACK_T, -c
    y_front0, y_front1 = DEPTH + c, DEPTH + c + RIDER_FRONT_T
    u = unary_union([
        sbox(y_back0, -RIDER_BACK_LEG, y_back1, bridge_t),
        sbox(y_back0, 0, y_front1, bridge_t),
        sbox(y_front0, -leg, y_front1, bridge_t),
    ])
    return u.buffer(-0.8).buffer(0.8), y_front0, y_front1


def make_gancho():
    """J hook for anything with a loop or strap. Printed on its side."""
    u, y0, y1 = rider_saddle()
    yc = (y0 + y1) / 2
    z0 = -RIDER_LEG + 1
    pts = [(yc, z0), (yc, z0 - HOOK_DROP)]
    cy, cz = yc + HOOK_R, z0 - HOOK_DROP
    for a in np.linspace(180, 385, 40)[1:]:
        pts.append((cy + HOOK_R * math.cos(math.radians(a)),
                    cz + HOOK_R * math.sin(math.radians(a))))
    hook = LineString(pts).buffer(RIDER_FRONT_T / 2 + 0.2)
    return extrude(unary_union([u, hook]), HOOK_W), HOOK_W


def make_repisa():
    """Small shelf with a lip: toothpaste standing on its cap, razor, etc."""
    leg = RIDER_LEG + 3
    u, y0, y1 = rider_saddle(leg=leg)
    y_end = y1 + SHELF_DEPTH
    tray = unary_union([
        sbox(y0, -leg, y1, -1),
        sbox(y0, -leg, y_end, -leg + 3.2),
        sbox(y_end - 3.0, -leg, y_end, -leg + SHELF_LIP),
    ])
    tray = tray.buffer(1.5).buffer(-1.5).buffer(-0.8).buffer(0.8)
    return extrude(unary_union([u, tray]), SHELF_W), SHELF_W


def _plate_rider(plate_xy: Polygon):
    """Rider whose tool is a flat plate level with the bridge. Built in the
    rider frame; printed upside down so the plate is the first layer."""
    c = RIDER_FIT / 2
    plate = extrude(plate_xy, PLATE_T)                    # z 0..PLATE_T
    legs = []
    for y0, y1, length in (
            (-c - RIDER_BACK_T, -c, RIDER_BACK_LEG),
            (DEPTH + c, DEPTH + c + RIDER_FRONT_T, RIDER_LEG)):
        leg = trimesh.creation.box(extents=[PLATE_W, y1 - y0, length + 0.5])
        leg.apply_translation([0, (y0 + y1) / 2, -length / 2 + 0.25])
        legs.append(leg)
    rider = trimesh.boolean.union([plate] + legs, engine="manifold")
    assert rider.is_volume
    return rider


def make_horquilla():
    """Fork: a toothbrush (manual or electric head) hangs by its neck."""
    c = RIDER_FIT / 2
    y_back = -c - RIDER_BACK_T
    y_leg = DEPTH + c + RIDER_FRONT_T
    y_end = y_leg + FORK_REACH
    body = sbox(-PLATE_W / 2, y_back, PLATE_W / 2, y_end)
    slot = LineString([(0, y_leg + 8), (0, y_end + 5)]).buffer(FORK_SLOT / 2)
    plate = body.difference(slot).buffer(-2.5).buffer(2.5)   # round prongs
    return _plate_rider(plate)


def make_aro():
    """Ring: hairdryer nozzle-down, or a cup. Set RING_ID to your object."""
    c = RIDER_FIT / 2
    y_back = -c - RIDER_BACK_T
    y_leg = DEPTH + c + RIDER_FRONT_T
    r_out = RING_ID / 2 + RING_WALL
    yc = y_leg + 2 + r_out
    body = unary_union([sbox(-PLATE_W / 2, y_back, PLATE_W / 2, yc),
                        Point(0, yc).buffer(r_out, 64)])
    body = body.buffer(6).buffer(-6)                   # fair neck into ring
    body = body.buffer(-1.5).buffer(1.5)
    plate = body.difference(Point(0, yc).buffer(RING_ID / 2, 64))
    return _plate_rider(plate)


def to_wall(rider_local: "trimesh.Trimesh", x: float) -> "trimesh.Trimesh":
    m = rider_local.copy()
    m.apply_translation([x, WALL_GAP, Z_TOP])
    return m


def on_bed(mesh: "trimesh.Trimesh", flip: bool = False) -> "trimesh.Trimesh":
    m = mesh.copy()
    if flip:
        m.apply_transform(trimesh.transformations.rotation_matrix(
            math.pi, [1, 0, 0]))
    m.apply_translation(-np.array([m.bounds[0][0], m.bounds[0][1],
                                   m.bounds[0][2]]))
    return m


# ============================================================================
# Engineering estimates (order of magnitude, PLA E ≈ 3000 MPa)
# ============================================================================
E_PLA = 3000.0


def loop_estimate(od: float, t: float, wrap: float, junction_z: float):
    """Peak strain while snapping on, and force to pull the loop back off."""
    r_in = (od + FIT) / 2
    r_mid = r_in + t / 2
    half_mouth = math.radians((360 - wrap) / 2)
    deflect = od / 2 - r_in * math.sin(half_mouth)        # per arm
    top = math.asin(min(1.0, junction_z / (r_in + t)))    # arm root angle
    arm = r_mid * (top + (math.pi / 2 - half_mouth))      # free arc length
    strain = 1.5 * deflect * t / arm ** 2
    inertia = DEPTH * t ** 3 / 12
    radial = 3 * E_PLA * inertia * deflect / arm ** 3
    lead = math.pi / 2 - half_mouth
    pull_off = 2 * radial * (math.tan(lead) + 0.3)
    return deflect, arm, strain, pull_off


def report(left: Polygon, right: Polygon, printed: dict):
    print("\n— Snap loops (mouth down) —")
    for name, od, t, wrap, jz in (
            ("caño", FAUCET_OD, CANO_T, CANO_WRAP,
             math.sqrt(max(0.0, ((FAUCET_OD + FIT) / 2 + CANO_T) ** 2
                           - (NECK_W / 2 + FILLET) ** 2))),
            ("manilla", HANDLE_OD, MANI_T, MANI_WRAP, LINE_Z0 - FILLET)):
        d, arm, strain, pull = loop_estimate(od, t, wrap, jz)
        print(f"  {name:8s} opens {d:.1f} mm/arm · free arm {arm:.0f} mm · "
              f"peak strain {strain * 100:.2f} % (keep < 1.2) · "
              f"pull-off ≈ {pull:.0f} N")
    inertia = DEPTH * LINE_H ** 3 / 12
    for grams, at in ((300, 150), (500, 200)):
        force = grams / 1000 * 9.81
        sag = 1.6 * force * at ** 3 / (3 * E_PLA * inertia)   # 1.6: taper
        uplift = force * at / CTC
        print(f"  {grams} g at {at} mm from a loop: tip sag ≈ {sag:.1f} mm · "
              f"uplift on the far loop ≈ {uplift:.0f} N")
    print("\n— Print —")
    for name, poly in (("trazo_izquierda", left), ("trazo_derecha", right)):
        x0, z0, x1, z1 = poly.bounds
        length, height = x1 - x0, z1 - z0
        print(f"  {name}: {length:.0f} × {height:.0f} × {DEPTH:.0f} mm · "
              f"fits a {math.ceil((length + height) / math.sqrt(2) + 4)} mm "
              f"square bed diagonally")
    total = 0.0
    for name, mesh in printed.items():
        size = mesh.bounds[1] - mesh.bounds[0]
        total += mesh.volume
        print(f"  {name:18s} {size[0]:6.1f} × {size[1]:5.1f} × {size[2]:5.1f}"
              f" mm · {mesh.volume / 1000:5.1f} cm³ · manifold={mesh.is_volume}")
    print(f"  total ≈ {total / 1000:.0f} cm³ ≈ {total / 1000 * 1.24:.0f} g PLA")


# ============================================================================
# Build
# ============================================================================
def build():
    profile = stroke_profile()
    left, right = split_profile(profile)
    printed = {
        "trazo_izquierda":  extrude(left, DEPTH),
        "trazo_derecha":    extrude(right, DEPTH),
    }
    gancho, gw = make_gancho()
    repisa, sw = make_repisa()
    riders_local = {
        "jinete_gancho":    gancho.copy().apply_transform(side_rider_to_local(gw)),
        "jinete_repisa":    repisa.copy().apply_transform(side_rider_to_local(sw)),
        "jinete_horquilla": make_horquilla(),
        "jinete_aro":       make_aro(),
    }
    printed["jinete_gancho"] = on_bed(gancho)
    printed["jinete_repisa"] = on_bed(repisa)
    printed["jinete_horquilla"] = on_bed(riders_local["jinete_horquilla"], flip=True)
    printed["jinete_aro"] = on_bed(riders_local["jinete_aro"], flip=True)
    return profile, left, right, printed, riders_local


def write_test_piece(name: str, polygons, checklist):
    """Export a cut-out of the stroke profile as an MVP test piece, lying on
    the bed exactly as the full part prints (same layer direction)."""
    meshes, x = [], 0.0
    for poly in polygons:
        m = extrude(poly, DEPTH)
        m.apply_translation([x - m.bounds[0][0], -m.bounds[0][1], 0])
        x = m.bounds[1][0] + 6
        meshes.append(m)
    piece = trimesh.util.concatenate(meshes)
    piece.export(HERE / f"{name}.stl")
    shown = piece.copy()
    shown.apply_transform(np.diag([1.0, -1.0, 1.0, 1.0]))   # printer → model
    export_glb([(name, paint(shown, MAT_PLA))], WEB_DIR / f"{name}.glb")
    update_web_version()
    size = piece.bounds[1] - piece.bounds[0]
    print(f"Wrote {name}.stl  {size[0]:.0f} × {size[1]:.0f} × {size[2]:.0f} mm"
          f" · {piece.volume / 1000:.1f} cm³")
    print("Print flat, as exported. Checklist:")
    for line in checklist:
        print(f"  [ ] {line}")


def update_web_version():
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    (WEB_DIR / "version.txt").write_text(str(int(time.time())))


def main():
    profile, left, right, printed, riders_local = build()

    for name, mesh in printed.items():
        mesh.export(HERE / f"{name}.stl")

    # --- installed view, with the faucet for context ---
    scene = []
    for name in ("trazo_izquierda", "trazo_derecha"):
        m = printed[name].copy()
        m.apply_transform(STROKE_TO_WALL)
        scene.append((name, paint(m, MAT_PLA)))
    layout = (("jinete_gancho", -200), ("jinete_horquilla", -150),
              ("jinete_repisa", -100), ("jinete_aro", 150),
              ("jinete_gancho", 200))
    for i, (name, x) in enumerate(layout):
        scene.append((f"{name}_{i}",
                      paint(to_wall(riders_local[name], x), MAT_PLA_2)))
    scene += make_context_meshes(FAUCET_OD, HANDLE_OD, CTC)
    export_glb(scene, WEB_DIR / "bathroom_trazo.glb")

    # --- print tray: every part as it lies on the bed ---
    tray, y = [], 0.0
    for name, mesh in printed.items():
        m = mesh.copy()
        m.apply_translation([-m.bounds[1][0] / 2, y, 0])
        y += m.bounds[1][1] - m.bounds[0][1] + 14
        # printer frame (y away from you) → model frame (y towards you)
        m.apply_transform(np.diag([1.0, -1.0, 1.0, 1.0]))
        tray.append((name, paint(m, MAT_PLA_2 if "jinete" in name else MAT_PLA)))
    export_glb(tray, WEB_DIR / "bathroom_trazo_piezas.glb")
    update_web_version()

    report(left, right, printed)
    return profile


if __name__ == "__main__":
    main()
