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
# Measured by Luis on the printed test pieces (20 Nov 2026): the caño clip
# stops ~6 mm from the plate and the manilla clip ~2 mm. The line lives in the
# caño's plane; a pad behind the manilla loop fills the 4 mm difference so
# both loops bottom out when the part is pushed home.
CANO_GAP       = 6.0     # caño flange: where the back of the line rests
MANI_GAP       = 2.0     # manilla flange
WALL_GAP       = CANO_GAP
MANI_PAD       = CANO_GAP - MANI_GAP   # filler behind the manilla loop
PAD_HALF_DEG   = 45.0    # the pad covers the top of the loop, ±45° from 12h;
                         # the snap arms below stay 8 mm deep, as tested
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
LINE_H         = 16.0    # height of the line between and beside the loops
LINE_H_TIP     = 6.0     # height at the tips (tapers along each arm)
ARM_LEN        = 250.0   # beyond each cylinder axis (Luis, 20 Nov: seven objects, none over the plate)
ROOT_X         = CTC / 2 + 32.0   # where the taper starts
TIP_LEN        = 24.0    # horizontal length of the upturned end
TIP_RISE       = 7.0     # how much the end rises: the "sutil curva"
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
PLATE_T        = 3.6     # plate of the fork / ring riders

# --- LG Casa radii brought to the physical world (same reading as the
# LARC HQ drawers): px are not mm; what is copied is the proportion. ---
R_CANTO        = 2.0     # canto: the small edge of a piece
R_ESQUINA      = 4.0     # esquina: where a piece turns (4-8 mm)
R_ENCUENTRO    = 6.0     # esquina, inside: where two walls meet
BEND_K         = 4.0     # a sheet that bends does it at 4x its thickness
TRAY_T         = 8.0     # depth of the fins of the open trays (the solid wall was 3.2)
RUNG           = 3.0     # rungs between fins

# --- what hangs where. Weights given by Luis (20 Nov 2026). Sizes of the
# objects are ESTIMATED from his photo: measure before printing a rider. ---
#   id, name, grams, x of the rider centre (mm from the middle), rider maker
OBJETOS = [
    ("cepillo",     "cepillo de dientes",  20, -256.0),
    ("pasta",       "pasta de dientes",   100, -226.0),
    ("desodorante", "desodorante",         65, -182.5),
    ("colonia",     "colonia",            370, -118.0),
    ("secador",     "secador",            250, +122.0),
    ("pelo",        "cepillo del pelo",   120, +185.0),
    ("oralb",       "oral-b",             125, +241.0),
]
COLONIA_W, COLONIA_D, COLONIA_H = 68.0, 30.0, 72.0   # bottle body (estimated)
DEO_D          = 42.0    # roll-on at its widest (estimated)
DEO_DROP       = 88.0    # its platform hangs this far below the top of the line
ORALB_D        = 28.0    # electric toothbrush handle (estimated)
TUBE_NECK      = 15.0    # slot for the toothpaste neck; the shoulder rests on it
BRUSH_NECK     = 8.0     # slot for a manual toothbrush neck
HAIRBRUSH_NECK = 21.0    # slot for the hairbrush handle, under its head
SECADOR_D_MORRO  = 48.0  # hairdryer barrel at the nozzle end (ESTIMATED)
SECADOR_D_CUERPO = 66.0  # hairdryer barrel at its widest (ESTIMATED)

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


def mani_pad_polygon() -> Polygon:
    """Top sector of the manilla loop: the footprint of the 4 mm filler."""
    r_in = (HANDLE_OD + FIT) / 2
    r_out = r_in + MANI_T
    ang = np.radians(np.linspace(90 - PAD_HALF_DEG, 90 + PAD_HALF_DEG, 40))
    xm = CTC / 2
    outer = [(xm + r_out * math.cos(a), r_out * math.sin(a)) for a in ang]
    inner = [(xm + r_in * math.cos(a), r_in * math.sin(a)) for a in ang[::-1]]
    return Polygon(outer + inner).buffer(-0.5).buffer(0.5)


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


def stroke_mesh(poly: Polygon, pad: Polygon | None = None) -> "trimesh.Trimesh":
    """Extrude a piece of the stroke. Local z = 0 is its back face (towards
    the wall); a pad, if any, sticks out behind it, from -MANI_PAD to 0."""
    body = extrude(poly, DEPTH)
    if pad is None:
        return body
    filler = extrude(pad.intersection(poly), MANI_PAD + 0.6)
    filler.apply_translation([0, 0, -MANI_PAD])
    mesh = trimesh.boolean.union([body, filler], engine="manifold")
    assert mesh.is_volume
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


def _round_corner(poly, corner, r, sy, sz):
    """Round one convex corner of an axis-aligned profile. (sy, sz) point
    from the inside of the piece to that corner."""
    y, z = corner
    cy, cz = y - sy * r, z - sz * r
    square = sbox(min(y, cy), min(z, cz), max(y, cy), max(z, cz))
    return poly.difference(square.difference(Point(cy, cz).buffer(r, 32)))


def rider_saddle(leg: float = RIDER_LEG, bridge_t: float = RIDER_BRIDGE_T,
                 front_t: float = RIDER_FRONT_T):
    """U that drops over the line. Rider frame: y = 0 at the line's back
    face, z = 0 at the line's top edge. Returns (profile, y of front face).
    Corners follow LG Casa: the front one turns with R_ESQUINA, the thin
    back one with R_CANTO, and both legs end in a round tip."""
    c = RIDER_FIT / 2
    y_back0, y_back1 = -c - RIDER_BACK_T, -c
    y_front0, y_front1 = DEPTH + c, DEPTH + c + front_t
    u = unary_union([
        sbox(y_back0, -RIDER_BACK_LEG, y_back1, bridge_t),
        sbox(y_back0, 0, y_front1, bridge_t),
        sbox(y_front0, -leg, y_front1, bridge_t),
    ])
    u = u.buffer(-0.95).buffer(0.95)
    u = _round_corner(u, (y_front1, bridge_t), R_ESQUINA, +1, +1)
    u = _round_corner(u, (y_back0, bridge_t), R_CANTO, -1, +1)
    return u, y_front0, y_front1


def make_gancho(width=18.0, drop=16.0, radius=10.0):
    """Deep J hook: the hairdryer hangs from the loop on its handle.
    Printed on its side. Returns the mesh in the rider frame."""
    u, y0, y1 = rider_saddle()
    yc = (y0 + y1) / 2
    z0 = -RIDER_LEG + 1
    pts = [(yc, z0), (yc, z0 - drop)]
    cy, cz = yc + radius, z0 - drop
    for a in np.linspace(180, 395, 40)[1:]:
        pts.append((cy + radius * math.cos(math.radians(a)),
                    cz + radius * math.sin(math.radians(a))))
    hook = LineString(pts).buffer(RIDER_FRONT_T / 2 + 0.4)
    side = extrude(unary_union([u, hook]), width)
    return side.copy().apply_transform(side_rider_to_local(width)), on_bed(side)


def _capsule(p0, p1, w):
    return LineString([p0, p1]).buffer(w / 2, 24)


def make_bandeja(width=COLONIA_W + 4, depth=COLONIA_D + 3, lip=12.0, drop=None,
                 ribs=4, rib_w=3.6):
    """Open tray: the object stands in front of the line (or, with `drop`,
    hangs that far below its top edge). Printed on its side.

    Same principle as the sponge cradle of El Secadero: ribs and an open
    floor instead of a solid sheet. The wall and the floor are `ribs` fins
    TRAY_T deep that run from the saddle to the lip; between them it is
    open, with a rung every 30-45 mm and a diagonal web at the bend (they
    are what each fin rests on while it prints). Material moves away from
    the neutral axis: the fins keep the section modulus of the 3.2 mm
    solid sheet they replace (asserted below) and are stiffer.
    The lip is a 3.2 mm sheet that bends up at 4x its thickness and ends
    in a round tip, like the ends of the line itself."""
    t, T = RIDER_FRONT_T, TRAY_T
    assert ribs * rib_w * T ** 2 >= width * t ** 2, "fins weaker than the solid sheet"
    z_ft = -(drop or RIDER_LEG + 3) + 3.2          # floor top: where it stood before
    z_fb = z_ft - T
    u, y0, yw = rider_saddle(front_t=T)             # yw = front edge of the fins
    y_fe = yw + depth + 3.0
    body = unary_union([sbox(y0, z_fb, yw, 1.0), sbox(y0, z_fb, y_fe, z_ft)])
    body = body.buffer(R_ENCUENTRO).buffer(-R_ENCUENTRO)        # inside corner
    body = _round_corner(body, (y0, z_fb), BEND_K * t, -1, -1)
    body = _round_corner(body, (y_fe, z_fb), T - t, +1, -1)
    r = BEND_K * t                                              # lip bend
    cz = z_ft - t / 2 + r
    phi = math.acos(max(-1.0, 1 - (lip - t) / r))
    pts = [(y_fe - 3.0, z_ft - t / 2)] + [
        (y_fe + r * math.sin(a), cz - r * math.cos(a))
        for a in np.linspace(0, phi, 24)]
    tray = unary_union([body, LineString(pts).buffer(t / 2, 16)])
    tray = tray.buffer(2.0).buffer(-2.0)
    side = extrude(unary_union([u, tray]), width)
    solid = side.copy().apply_transform(side_rider_to_local(width))

    bay = (width - ribs * rib_w) / (ribs - 1)
    xs = [-width / 2 + rib_w + bay / 2 + k * (rib_w + bay) for k in range(ribs - 1)]
    through_y = np.array([[1, 0, 0, 0], [0, 0, 1, y0 - 1.0],
                          [0, 1, 0, 0], [0, 0, 0, 1.0]])
    z_a = -0.5                              # the windows start under the bridge
    wall = True
    y_b = y_fe + 3.0                        # the windows bite into the foot of the lip
    cuts, keeps = [], []
    for x in xs:
        if wall:
            rows = max(1, math.ceil((z_a - z_ft) / (bay + 30.0)))
            length = (z_a - z_ft - (rows - 1) * RUNG) / rows
            for k in range(rows):
                z1 = z_a - k * (length + RUNG)
                last = k == rows - 1
                z2 = z_fb - 1.0 if last else z1 - length
                win = _capsule((x, z1 - bay / 2), (x, z2 + (0 if last else bay / 2)), bay)
                if last:
                    win = win.intersection(sbox(x - bay, z2, x + bay, z1))
                m = extrude(win, T + 2.0)
                m.apply_transform(through_y)
                cuts.append(m)
            web = trimesh.creation.box(extents=[bay + 1.0, RUNG, 6 * T])
            web.apply_transform(trimesh.transformations.rotation_matrix(
                -math.pi / 4, [1, 0, 0]))
            web.apply_translation([x, yw - T / 2, z_ft - T / 2])
            keeps.append(trimesh.boolean.intersection([solid, web], engine="manifold"))
        y_a = y0 - 1.0 if wall else yw + R_ENCUENTRO + 0.5
        win = _capsule((x, y_a + (0 if wall else bay / 2)), (x, y_b - bay / 2), bay)
        if wall:
            win = win.intersection(sbox(x - bay, y_a, x + bay, y_b))
        m = extrude(win, T + 2.0)
        m.apply_translation([0, 0, z_fb - 1.0])
        cuts.append(m)
    local = trimesh.boolean.difference([solid] + cuts, engine="manifold")
    if keeps:
        local = trimesh.boolean.union([local] + keeps, engine="manifold")
    assert local.is_volume and len(local.split()) == 1
    bed = local.copy().apply_transform(np.linalg.inv(side_rider_to_local(width)))
    return local, on_bed(bed)


def _plate_rider(plate_xy: Polygon, width: float, extra=(), cut=()):
    """Rider whose tool is a flat plate level with the bridge. Built in the
    rider frame; printed upside down so the plate is the first layer.
    The legs follow the rounded outline of the plate."""
    c = RIDER_FIT / 2
    plate = extrude(plate_xy, PLATE_T)                    # z 0..PLATE_T
    legs = []
    for y0, y1, length in (
            (-c - RIDER_BACK_T, -c, RIDER_BACK_LEG),
            (DEPTH + c, DEPTH + c + RIDER_FRONT_T, RIDER_LEG)):
        leg = trimesh.creation.box(extents=[width, y1 - y0, length + 0.5])
        leg.apply_translation([0, (y0 + y1) / 2, -length / 2 + 0.25])
        legs.append(leg)
    outline = extrude(Polygon(plate_xy.exterior), 40.0)
    outline.apply_translation([0, 0, -30.0])
    legs = [trimesh.boolean.intersection([leg, outline], engine="manifold")
            for leg in legs]
    rider = trimesh.boolean.union([plate] + legs + list(extra), engine="manifold")
    if cut:
        rider = trimesh.boolean.difference([rider] + list(cut), engine="manifold")
    assert rider.is_volume
    return rider, on_bed(rider, flip=True)


def make_horquilla(slot=BRUSH_NECK, reach=22.0, width=22.0):
    """Fork open to the front: the object slides in and hangs by its neck."""
    c = RIDER_FIT / 2
    y_back = -c - RIDER_BACK_T
    y_leg = DEPTH + c + RIDER_FRONT_T
    y_end = y_leg + reach
    body = sbox(-width / 2, y_back, width / 2, y_end)
    channel = LineString([(0, y_leg + 3 + slot / 2), (0, y_end + 5)]).buffer(slot / 2)
    r = (width - slot) / 4 - 0.05                 # prongs end in a full round tip
    plate = body.difference(channel).buffer(-r).buffer(r)
    return _plate_rider(plate, width)


def _ring_plate(inner_d: float, wall: float, width: float):
    c = RIDER_FIT / 2
    y_back = -c - RIDER_BACK_T
    y_leg = DEPTH + c + RIDER_FRONT_T
    r_out = inner_d / 2 + wall
    yc = y_leg + 2 + r_out
    body = unary_union([sbox(-width / 2, y_back, width / 2, yc),
                        Point(0, yc).buffer(r_out, 64)])
    body = body.buffer(5).buffer(-5).buffer(-1.5).buffer(1.5)
    return body.difference(Point(0, yc).buffer(inner_d / 2, 64)), yc


def make_aro(inner_d=DEO_D - 1.0, wall=4.0, width=30.0):
    """Ring: the roll-on drops in cap down and rests on its widest part."""
    plate, _ = _ring_plate(inner_d, wall, width)
    return _plate_rider(plate, width)


def _frustum(r_top, r_bot, z_top, z_bot):
    return trimesh.creation.revolve(
        [(0, z_bot), (r_bot, z_bot), (r_top, z_top), (0, z_top)], sections=96)


def make_embudo(d_top=SECADOR_D_CUERPO - 2.0, d_bot=SECADOR_D_MORRO + 2.0,
                height=26.0, wall=3.2, width=44.0):
    """Funnel ring for the hairdryer, level with the line: the barrel goes
    in nozzle down and wedges where its taper meets the cone, so the motor
    and the switch stay above the faucet, away from splashes. The handle
    (it folds) stays out, towards you: it is what you grab.
    Printed plate down: the cone grows upwards leaning 15 deg, no supports."""
    plate, yc = _ring_plate(d_top, wall, width)
    plate = unary_union([plate, Point(0, yc).buffer(d_top / 2 + 0.01)])
    outer = _frustum(d_top / 2 + wall, d_bot / 2 + wall, 0.5, -height)
    inner = _frustum(d_top / 2, d_bot / 2, 0.0, -height)
    hole = trimesh.util.concatenate([
        _frustum(d_top / 2, d_bot / 2 - (d_top - d_bot) / 2 / height, 0.0, -height - 1),
        _cyl(d_top, PLATE_T + 1, 0, 0, -0.01)])
    for m in (outer, hole):
        m.apply_translation([0, yc, 0])
    hole = trimesh.boolean.union(hole.split(), engine="manifold")
    return _plate_rider(plate, width, [outer], [hole])


def make_vasito(inner_d=ORALB_D + 3.0, wall=4.0, width=30.0, depth=42.0):
    """Open cup for the electric toothbrush: a ring on top, four posts and
    a cross for a floor, so it drains. Printed ring-down: the posts grow
    upwards and the cross is two 30 mm bridges on top."""
    plate, yc = _ring_plate(inner_d, wall, width)
    r = inner_d / 2 + wall / 2
    extra = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        post = trimesh.creation.box(extents=[4.0, 4.0, depth + 0.5])
        post.apply_translation([r * math.cos(a), yc + r * math.sin(a),
                                -depth / 2 + 0.25])
        extra.append(post)
    for k in range(2):
        bar = trimesh.creation.box(extents=[2 * r + 4.0, 5.0, 2.4])
        bar.apply_transform(trimesh.transformations.rotation_matrix(
            math.radians(45 + 90 * k), [0, 0, 1]))
        bar.apply_translation([0, yc, -depth + 1.2])
        extra.append(bar)
    return _plate_rider(plate, width, extra)


def make_horquilla_baja(slot=BRUSH_NECK, reach=22.0, width=22.0, drop=34.0):
    """Fork hanging `drop` below the top of the line, so what it holds stays
    under the line. Printed on its side; the slot needs a small support."""
    u, y0, y1 = rider_saddle(leg=drop)
    plate = sbox(y0, -drop, y1 + reach, -drop + PLATE_T)
    plate = unary_union([sbox(y0, -drop, y1, 0), plate]).buffer(1.5).buffer(-1.5)
    side = extrude(unary_union([u, plate]), width)
    local = side.copy().apply_transform(side_rider_to_local(width))
    cut_len = reach + 6
    channel = trimesh.creation.box(extents=[slot, cut_len, PLATE_T + 6])
    channel.apply_translation([0, y1 + 3 + cut_len / 2, -drop + PLATE_T / 2])
    local = trimesh.boolean.difference([local, channel], engine="manifold")
    assert local.is_volume
    bed = local.copy().apply_transform(np.linalg.inv(side_rider_to_local(width)))
    return local, on_bed(bed)


def make_pinza(width=40.0, drop=34.0, slit=1.2):
    """Hanging clip for the toothpaste: the flat end of the tube slides in
    sideways between the leg and a springy jaw. Printed on its side."""
    u, y0, y1 = rider_saddle(leg=drop)
    jaw = unary_union([
        sbox(y1 + slit, -drop, y1 + slit + 2.2, -14),
        sbox(y1 - 0.5, -16, y1 + slit + 2.2, -13),
    ])
    side = extrude(unary_union([u, jaw.buffer(-0.4).buffer(0.4)]), width)
    return side.copy().apply_transform(side_rider_to_local(width)), on_bed(side)


RIDERS = {
    "cepillo":     lambda: make_horquilla(BRUSH_NECK, 22.0, 22.0),
    "pasta":       lambda: make_horquilla(TUBE_NECK, 26.0, 30.0),
    # Luis, 20 Nov: the roll-on on a platform, hanging, not upside down in a ring
    "desodorante": lambda: make_bandeja(DEO_D + 4, DEO_D + 2, 14.0, drop=DEO_DROP,
                                        ribs=3, rib_w=2.9),
    "colonia":     lambda: make_bandeja(),
    "secador":     lambda: make_embudo(),
    "pelo":        lambda: make_horquilla(HAIRBRUSH_NECK, 32.0, 44.0),
    "oralb":       lambda: make_vasito(),
}

# The same objects hanging below the line instead of standing on it
# ("la línea es el techo"). The hairdryer and the roll-on have one form.
RIDERS_BAJO = {
    "cepillo":     lambda: make_horquilla_baja(BRUSH_NECK, 22.0, 22.0, 34.0),
    "pasta":       lambda: make_pinza(),
    "colonia":     lambda: make_bandeja(drop=COLONIA_H + 27.0),
    "pelo":        lambda: make_gancho(5.5, 8.0, 7.0),
    "oralb":       lambda: make_horquilla_baja(10.0, 24.0, 26.0, 32.0),
}


MAT = {
    "blanco": ([236, 236, 232, 255], 0.0, 0.45), "azul": ([36, 92, 190, 255], 0.0, 0.4),
    "rojo": ([205, 40, 44, 255], 0.0, 0.45), "negro": ([28, 28, 30, 255], 0.2, 0.5),
    "gris": ([74, 76, 80, 255], 0.5, 0.4), "ambar": ([198, 146, 58, 255], 0.2, 0.15),
    "plata": ([205, 205, 212, 255], 1.0, 0.2), "celeste": ([70, 170, 215, 255], 0.0, 0.5),
}


def _box(dx, dy, dz, x, y, z0):
    m = trimesh.creation.box(extents=[dx, dy, dz])
    m.apply_translation([x, y, z0 + dz / 2])
    return m


def _cyl(d, h, x, y, z0, axis="z"):
    m = trimesh.creation.cylinder(radius=d / 2, height=h, sections=40)
    if axis == "y":
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
        m.apply_translation([x, y + h / 2, z0])
    else:
        m.apply_translation([x, y, z0 + h / 2])
    return m


def _blob(dx, dy, dz, x, y, z0):
    m = trimesh.creation.icosphere(subdivisions=3, radius=0.5)
    m.apply_scale([dx, dy, dz])
    m.apply_translation([x, y, z0 + dz / 2])
    return m


def make_objetos():
    """Rough stand-ins for Luis's things, in the rider frame, to show the bar
    in use. Sizes are estimates from his photo; they are never printed."""
    c = RIDER_FIT / 2
    y_leg = DEPTH + c + RIDER_FRONT_T
    T = PLATE_T
    y_fork = lambda slot: y_leg + 3 + slot / 2 + 3
    y_ring = lambda d, wall: y_leg + 2 + d / 2 + wall
    yd, yo = y_ring(DEO_D - 1, 4.0), y_ring(ORALB_D + 3, 4.0)
    yb, yp, yh = y_fork(BRUSH_NECK), y_fork(TUBE_NECK), y_fork(HAIRBRUSH_NECK)
    y_tray = DEPTH + c + TRAY_T                 # front of the ribs of a tray
    yc = y_tray + 1.5 + COLONIA_D / 2
    ydb = y_tray + 1.5 + (DEO_D + 2) / 2
    zd = -DEO_DROP + 3.2
    ye = y_leg + 2 + (SECADOR_D_CUERPO - 2.0) / 2 + 3.2      # funnel axis
    barrel = _frustum(SECADOR_D_CUERPO / 2, SECADOR_D_MORRO / 2, 12.0, -22.0)
    barrel.apply_translation([0, ye, 0])
    arriba = {
        "cepillo": [(_box(9, 6, 150, 0, yb, -150 + T), "celeste"),
                    (_box(11, 8, 12, 0, yb, T), "blanco"),
                    (_box(12, 14, 26, 0, yb + 3, T + 12), "blanco")],
        "pasta": [(_cyl(13, 16, 0, yp, -16 + T), "blanco"),
                  (_cyl(30, 60, 0, yp, T), "rojo"),
                  (_box(34, 8, 50, 0, yp, T + 58), "blanco")],
        "desodorante": [(_cyl(DEO_D - 3, 38, 0, ydb, zd), "azul"),
                        (_cyl(DEO_D, 44, 0, ydb, zd + 38), "blanco")],
        "colonia": [(_box(COLONIA_W, COLONIA_D, COLONIA_H, 0, yc, -RIDER_LEG - 3 + 3.2), "ambar"),
                    (_cyl(22, 22, 0, yc, -RIDER_LEG - 3 + 3.2 + COLONIA_H), "plata")],
        "secador": [(_cyl(SECADOR_D_MORRO, 22, 0, ye, -44), "negro"),
                    (barrel, "gris"),
                    (_cyl(SECADOR_D_CUERPO, 56, 0, ye, 12), "gris"),
                    (_cyl(SECADOR_D_CUERPO - 8, 5, 0, ye, 68), "negro"),
                    (_box(28, 100, 30, 0, ye + SECADOR_D_CUERPO / 2 + 46, 30), "negro")],
        "pelo": [(_cyl(18, 118, 0, yh, -118 + T), "negro"),
                 (_blob(64, 20, 96, 0, yh, T + 4), "negro")],
        "oralb": [(_cyl(ORALB_D, 122, 0, yo, -42 + 2.4), "blanco"),
                  (_cyl(ORALB_D + 0.6, 10, 0, yo, 40), "azul"),
                  (_cyl(9, 58, 0, yo, 80), "blanco"),
                  (_box(11, 12, 14, 0, yo + 3, 136), "blanco")],
    }
    # hanging: nothing rises above the top of the line (z = 0)
    zc = -(COLONIA_H + 27.0) + 3.2
    zb, zo = -34.0 + T, -32.0 + T
    yob = y_leg + 3 + 5 + 3
    yj = y_leg - RIDER_FRONT_T / 2 + 7
    abajo = {
        "cepillo": [(_box(9, 6, 150, 0, yb, zb - T - 150), "celeste"),
                    (_box(11, 8, 4, 0, yb, zb - T), "blanco"),
                    (_box(12, 14, 26, 0, yb + 3, zb), "blanco")],
        "pasta": [(_box(38, 1.0, 16, 0, y_leg + 0.6, -32), "blanco"),
                  (_box(36, 8, 22, 0, y_leg + 2, -56), "blanco"),
                  (_cyl(30, 84, 0, y_leg + 6, -140), "rojo"),
                  (_cyl(13, 14, 0, y_leg + 6, -154), "blanco")],
        "colonia": [(_box(COLONIA_W, COLONIA_D, COLONIA_H, 0, yc, zc), "ambar"),
                    (_cyl(22, 22, 0, yc, zc + COLONIA_H), "plata")],
        "pelo": [(_cyl(18, 118, 0, yj, -134), "negro"),
                 (_blob(64, 20, 96, 0, yj, -228), "negro")],
        "oralb": [(_box(11, 12, 14, 0, yob + 3, zo + 4), "blanco"),
                  (_cyl(9, 60, 0, yob, zo - T - 56), "blanco"),
                  (_cyl(ORALB_D + 0.6, 10, 0, yob, zo - T - 66), "azul"),
                  (_cyl(ORALB_D, 122, 0, yob, zo - T - 188), "blanco")],
    }
    return arriba, abajo


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


def loop_pull_off():
    """Estimated force (N) that pulls each loop up and off its cylinder."""
    cano_jz = math.sqrt(max(0.0, ((FAUCET_OD + FIT) / 2 + CANO_T) ** 2
                            - (NECK_W / 2 + FILLET) ** 2))
    return (loop_estimate(FAUCET_OD, CANO_T, CANO_WRAP, cano_jz)[3],
            loop_estimate(HANDLE_OD, MANI_T, MANI_WRAP, LINE_Z0 - FILLET)[3])


TAPER = 1.6            # a tapered arm sags about 1.6x a uniform one
SIGMA_OK = 15.0        # MPa that PLA holds for years without creeping away
G = 9.81 / 1000        # N per gram


def estado(puestos) -> dict:
    """Statics of the bar with a given set of objects on it.

    The bar is a beam on two supports (the loops). A positive reaction means
    the loop presses down on its cylinder; a negative one means the load is
    trying to lift that loop, and only its snap arms hold it."""
    xc, xm = -CTC / 2, CTC / 2
    on = [(g * G, x) for oid, _, g, x in OBJETOS if oid in puestos]
    total = sum(f for f, _ in on)
    r_mani = sum(f * (x - xc) for f, x in on) / CTC
    r_cano = total - r_mani
    inertia = DEPTH * LINE_H ** 3 / 12
    out = {"peso_g": round(total / G), "cano_N": r_cano, "manilla_N": r_mani}
    for lado, sign, root in (("izq", -1, xc), ("der", +1, xm)):
        arms = [(f, sign * (x - root)) for f, x in on if sign * (x - root) > 0
                and sign * x > CTC / 2]
        moment = sum(f * a for f, a in arms)
        sag = TAPER * sum(f * a * a * (3 * ARM_LEN - a) for f, a in arms) \
            / (6 * E_PLA * inertia)
        out[f"momento_{lado}_Nmm"] = moment
        out[f"tension_{lado}_MPa"] = moment * 6 / (DEPTH * LINE_H ** 2)
        out[f"flecha_{lado}_mm"] = sag
    return out


def cargas() -> dict:
    """Every combination of objects on/off: the worst case for each limit."""
    from itertools import combinations
    ids = [o[0] for o in OBJETOS]
    pull_cano, pull_mani = loop_pull_off()
    peor = {"cano": (0.0, ()), "manilla": (0.0, ()), "tension": (0.0, ()),
            "flecha": (0.0, ())}
    for n in range(len(ids) + 1):
        for combo in combinations(ids, n):
            e = estado(combo)
            for key, value in (
                    ("cano", -e["cano_N"]), ("manilla", -e["manilla_N"]),
                    ("tension", max(e["tension_izq_MPa"], e["tension_der_MPa"])),
                    ("flecha", max(e["flecha_izq_mm"], e["flecha_der_mm"]))):
                if value > peor[key][0]:
                    peor[key] = (value, combo)
    return {
        "ctc": CTC, "arm_len": ARM_LEN, "depth": DEPTH, "line_h": LINE_H,
        "E": E_PLA, "taper": TAPER, "sigma_ok": SIGMA_OK,
        "aguanta_cano_N": round(pull_cano, 1),
        "aguanta_manilla_N": round(pull_mani, 1),
        "objetos": [{"id": i, "nombre": n, "gramos": g, "x": x,
                     "formas": ["arriba", "abajo"] if i in RIDERS_BAJO else ["puesto"]}
                    for i, n, g, x in OBJETOS],
        "todo": {k: round(v, 2) for k, v in estado(ids).items()},
        "peor": {k: {"valor": round(v, 2), "con": list(c)}
                 for k, (v, c) in peor.items()},
    }


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
    c = cargas()
    t = c["todo"]
    print("\n— Loads (weights from Luis; positions in OBJETOS) —")
    print(f"  everything on: {t['peso_g']} g · caño {t['cano_N']:+.1f} N · "
          f"manilla {t['manilla_N']:+.1f} N (+ presses down, - lifts)")
    for key, label, limit in (
            ("cano", "worst lift on the caño loop", c["aguanta_cano_N"]),
            ("manilla", "worst lift on the manilla loop", c["aguanta_manilla_N"]),
            ("tension", "worst stress at an arm root", SIGMA_OK)):
        w = c["peor"][key]
        unit = "MPa" if key == "tension" else "N"
        margin = limit / w["valor"] if w["valor"] else float("inf")
        print(f"  {label}: {w['valor']:.1f} {unit} of {limit:.0f} "
              f"(x{margin:.1f}) with {', '.join(w['con']) or 'nothing'}")
    w = c["peor"]["flecha"]
    print(f"  worst tip sag: {w['valor']:.1f} mm at first, about double with "
          f"the years (creep), with {', '.join(w['con'])}")
    print("\n— Open trays: fins TRAY_T deep instead of a solid 3.2 mm sheet —")
    t, T = RIDER_FRONT_T, TRAY_T
    for name, width, ribs, rib_w, grams, d in (
            ("colonia", COLONIA_W + 4, 4, 3.6, 370, COLONIA_D),
            ("desodorante", DEO_D + 4, 3, 2.9, 65, DEO_D + 2)):
        w0, w1 = width * t ** 2 / 6, ribs * rib_w * T ** 2 / 6
        i0, i1 = width * t ** 3 / 12, ribs * rib_w * T ** 3 / 12
        m0 = grams * G * (t + 1.5 + d / 2)          # weight x how far it stands out
        m1 = grams * G * (T + 1.5 + d / 2)
        print(f"  {name:11s} W {w0:.0f} -> {w1:.0f} mm3 · I {i0:.0f} -> {i1:.0f} mm4"
              f" (x{i1 / i0:.1f} stiffer) · stress {m0 / w0:.2f} -> {m1 / w1:.2f} MPa"
              f" of {SIGMA_OK:.0f}")
    grams, arm, width = 250, 85.0, 44.0             # hairdryer, handle towards you
    m = grams * G * arm
    print(f"\n— Funnel ring (hairdryer {grams} g, centre of mass ~{arm:.0f} mm out) —")
    print(f"  plate at the saddle: {m / (width * PLATE_T ** 2 / 6):.1f} MPa · front leg: "
          f"{m / (width * RIDER_FRONT_T ** 2 / 6):.1f} MPa of {SIGMA_OK:.0f} · it twists "
          f"the line with {m:.0f} N·mm (the cologne tray: "
          f"{370 * G * (TRAY_T + 1.5 + COLONIA_D / 2 + DEPTH / 2):.0f})")
    print("\n— Print —")
    for name, poly in (("trazo_izquierda", left), ("trazo_derecha", right)):
        x0, z0, x1, z1 = poly.bounds
        length, height = x1 - x0, z1 - z0
        from shapely import affinity
        side = min(max(r.bounds[2] - r.bounds[0], r.bounds[3] - r.bounds[1])
                   for r in (affinity.rotate(poly, a) for a in range(0, 180, 1)))
        print(f"  {name}: {length:.0f} × {height:.0f} × {DEPTH:.0f} mm · "
              f"turned on the bed it needs a {side:.0f} mm square "
              f"(A1: 256 mm)")
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
    stroke = {
        "trazo_izquierda":  stroke_mesh(left),
        "trazo_derecha":    stroke_mesh(right, mani_pad_polygon()),
    }
    printed = {
        "trazo_izquierda":  on_bed(stroke["trazo_izquierda"]),
        # front face down, so the pad is the last thing printed: no supports
        "trazo_derecha":    on_bed(stroke["trazo_derecha"], flip=True),
    }
    riders_local = {}
    for oid, maker in RIDERS.items():
        local, bed = maker()
        riders_local[oid] = local
        printed[f"jinete_{oid}"] = bed
    for oid, maker in RIDERS_BAJO.items():
        local, bed = maker()
        riders_local[f"{oid}_bajo"] = local
        printed[f"jinete_{oid}_bajo"] = bed
    return profile, left, right, printed, riders_local, stroke


def write_test_piece(name: str, polygons, checklist, pads=None):
    """Export a cut-out of the stroke profile as an MVP test piece, lying on
    the bed exactly as the full part prints (same layer direction)."""
    meshes, x = [], 0.0
    for poly, pad in zip(polygons, pads or [None] * len(polygons)):
        m = on_bed(stroke_mesh(poly, pad), flip=pad is not None)
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
    profile, left, right, printed, riders_local, stroke = build()

    for name, mesh in printed.items():
        mesh.export(HERE / f"{name}.stl")

    # --- installed view, with the faucet for context ---
    scene = []
    for name in ("trazo_izquierda", "trazo_derecha"):
        m = stroke[name].copy()
        m.apply_transform(STROKE_TO_WALL)
        scene.append((name, paint(m, MAT_PLA)))
    for oid, _, _, x in OBJETOS:
        scene.append((f"jinete_{oid}",
                      paint(to_wall(riders_local[oid], x), MAT_PLA_2)))
    scene += make_context_meshes(FAUCET_OD, HANDLE_OD, CTC)
    export_glb(scene, WEB_DIR / "bathroom_trazo.glb")

    # --- the same view with Luis's things on it (node names drive the
    # load animation: obj_<id>_<n>) ---
    # Each object can stand on the line ("arriba") or hang below it ("abajo"):
    # obj_/jinete_ are the first form, objb_/jineteb_ the hanging one.
    uso = list(scene)
    arriba, abajo = make_objetos()
    for oid, _, _, x in OBJETOS:
        for k, (mesh, mat) in enumerate(arriba[oid]):
            uso.append((f"obj_{oid}_{k}", paint(to_wall(mesh, x), MAT[mat])))
        if oid in abajo:
            uso.append((f"jineteb_{oid}",
                        paint(to_wall(riders_local[f"{oid}_bajo"], x), MAT_PLA_2)))
            for k, (mesh, mat) in enumerate(abajo[oid]):
                uso.append((f"objb_{oid}_{k}", paint(to_wall(mesh, x), MAT[mat])))
    export_glb(uso, WEB_DIR / "bathroom_trazo_uso.glb")
    import json
    (HERE / "cargas.json").write_text(
        json.dumps(cargas(), ensure_ascii=False, indent=1) + "\n")

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
