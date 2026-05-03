#!/usr/bin/env python3
"""MVP variant 4-COMPARE: two fork-pinches with different arm lengths
on the same print bed for side-by-side testing.

Print this once, try the sponge in both, then update PINCH_ARM_L in
generate_stl.py to whichever felt right.

  LEFT  — arm 20 mm (current default; ~mid)
  RIGHT — arm 14 mm (very short; minimal contact)
"""

from pathlib import Path

import trimesh

import generate_stl as g

ARM_LEFT_MM   = 20.0
ARM_RIGHT_MM  = 14.0
SEPARATION_MM = 8.0   # clearance between the two pieces along X

# Frozen at the 5-prong design used during the actual A/B test, so this
# file stays as a faithful snapshot even if generate_stl.py defaults
# change in later iterations.
NUM_PRONGS_FROZEN     = 5
PRONG_Y_RATIO_FROZEN  = 0.35

OUT     = Path(__file__).with_name("test_sponge_v_fork_compare.stl")
OUT_3MF = Path(__file__).with_name("test_sponge_v_fork_compare.3mf")
WEB     = Path(__file__).resolve().parents[2] / "docs" / "models" / "test_sponge_v_fork_compare.glb"


def _make_pinch(arm_l):
    return g.build_fork_pinch(
        gap_top=g.PINCH_GAP_TOP,
        gap_bottom=g.PINCH_GAP_BOTTOM,
        arm_l=arm_l,
        total_y=g.PINCH_LEN_Y,
        num_prongs=NUM_PRONGS_FROZEN,
        prong_y_ratio=PRONG_Y_RATIO_FROZEN,
        wall_t=g.PINCH_WALL_T,
        curved_cap=True,
    )


def main():
    left  = _make_pinch(ARM_LEFT_MM)
    right = _make_pinch(ARM_RIGHT_MM)

    # Place left piece on the -X side, right on +X side, with SEPARATION
    # of clearance between their outer walls. Both rest with tips on Z=0.
    bmin_l, bmax_l = left.bounds
    bmin_r, bmax_r = right.bounds
    width_l = bmax_l[0] - bmin_l[0]
    width_r = bmax_r[0] - bmin_r[0]

    left.apply_translation([
        -(SEPARATION_MM / 2 + width_l / 2),
        -(bmin_l[1] + bmax_l[1]) / 2,
        -bmin_l[2],
    ])
    right.apply_translation([
        +(SEPARATION_MM / 2 + width_r / 2),
        -(bmin_r[1] + bmax_r[1]) / 2,
        -bmin_r[2],
    ])

    combined = trimesh.util.concatenate([left, right])
    combined.export(OUT)
    combined.export(OUT_3MF)
    WEB.parent.mkdir(parents=True, exist_ok=True)
    combined.export(WEB)
    g.update_web_version()

    bmin, bmax = combined.bounds
    size = bmax - bmin
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_3MF}")
    print(f"Bounding box (mm): X {size[0]:.1f}  Y {size[1]:.1f}  Z {size[2]:.1f}")
    print(f"Volume: {combined.volume / 1000:.1f} cm³")
    print()
    print(f"Layout:  LEFT (arm {ARM_LEFT_MM} mm)  ↔ {SEPARATION_MM} mm gap ↔  RIGHT (arm {ARM_RIGHT_MM} mm)")
    print("Test:")
    print(f"  [ ] Sponge enters the LEFT (longer) pinch — note how it feels")
    print(f"  [ ] Sponge enters the RIGHT (shorter) pinch — note how it feels")
    print(f"  [ ] Compare grip strength once inserted")
    print(f"  [ ] Pull the sponge out from each — note removal effort")
    print(f"  [ ] Pick a winner; update PINCH_ARM_L in generate_stl.py")


if __name__ == "__main__":
    main()
