#!/usr/bin/env python3
"""MVP variant 4: converging fork-pinch.

Iteration on the parallel-wall pinch after testing the cylindrical C
versions. Three changes:

  - Walls converge (gap 16 mm at the mouth → 8 mm at the throat) so the
    sponge wedges in tighter the further it goes; gravity + water make
    it self-tighten.
  - Each wall is split into 4 prongs separated by Y-direction gaps so
    water drains and air reaches the sponge — fixes the "drying" issue
    of a fully-enclosed pinch.
  - Short arm (28 mm) so only the top of the sponge is gripped; the
    bottom hangs free in the air.

UX:
  - Mouth is the widest gap → sponge slots in with light pressure.
  - As it goes up, walls squeeze harder → no slipping.
  - To remove: pull straight down through the wide mouth.

Print orientation: walls vertical (Z), gap in X, mouth on the bed.
The cap on top bridges 8 mm — short enough for PLA without supports.
"""

from pathlib import Path

import generate_stl as g

GAP_TOP_MM     = 8.0    # narrow throat (final grip)
GAP_BOTTOM_MM  = 16.0   # wide mouth (easy entry)
ARM_LEN_MM     = 28.0   # how deep the clip grips (sponge sticks out below)
TOTAL_Y_MM     = 55.0   # along sponge top edge
NUM_PRONGS     = 4
PRONG_Y_RATIO  = 0.55   # 55% material, 45% air gaps in Y

OUT = Path(__file__).with_name("test_sponge_v_fork.stl")
WEB = Path(__file__).resolve().parents[2] / "docs" / "models" / "test_sponge_v_fork.glb"


def main():
    pinch = g.build_fork_pinch(
        gap_top=GAP_TOP_MM,
        gap_bottom=GAP_BOTTOM_MM,
        arm_l=ARM_LEN_MM,
        total_y=TOTAL_Y_MM,
        num_prongs=NUM_PRONGS,
        prong_y_ratio=PRONG_Y_RATIO,
    )
    bmin, bmax = pinch.bounds
    pinch.apply_translation([
        -(bmin[0] + bmax[0]) / 2,
        -(bmin[1] + bmax[1]) / 2,
        -bmin[2],
    ])
    pinch.export(OUT)
    WEB.parent.mkdir(parents=True, exist_ok=True)
    pinch.export(WEB)
    g.update_web_version()

    bmin, bmax = pinch.bounds
    size = bmax - bmin
    print(f"Wrote {OUT}")
    print(f"Triangles: {len(pinch.faces)}")
    print(f"Bounding box (mm): X {size[0]:.1f}  Y {size[1]:.1f}  Z {size[2]:.1f}")
    print(f"Volume: {pinch.volume / 1000:.1f} cm³  (manifold={pinch.is_volume})")
    print()
    print(f"Variant: fork-pinch · gap {GAP_BOTTOM_MM}→{GAP_TOP_MM} mm · "
          f"arm {ARM_LEN_MM} mm · {NUM_PRONGS} prongs/side")
    print("Test:")
    print(f"  [ ] Sponge slots in with light pressure at the wide mouth")
    print(f"  [ ] Wedges tight by the time the top is at the throat")
    print(f"  [ ] Bottom of sponge hangs free → drips dry")
    print(f"  [ ] Pull-down release feels intuitive")
    print(f"  [ ] Walls flex visibly during insertion but no cracks")


if __name__ == "__main__":
    main()
