#!/usr/bin/env python3
"""MVP variant 4: clothespin-tips fork-pinch.

Inverted from the first attempt after user feedback: narrow at the
bottom, wider at the top, so the prongs behave like spring-loaded
clothespin tips. Cap at the top is the rigid "hinge"; the prongs
hang down converging until they almost touch at the open mouth.

The pinching action lives in the wall flex: when the sponge pushes
through the narrow tips, the prongs spread; once past, the sponge
sits in the wider zone above and the tips spring back, locking it in.

  - Throat (top, where the cap closes the structure): 14 mm — sponge
    barely compressed here, free to dry.
  - Tips (bottom, open mouth): 6 mm — sponge has to wedge through;
    once in, the spring-loaded tips don't let it back out without
    deliberate pulling.
  - Each wall is split into 4 vertical prongs with Y-direction air
    gaps so water drains and air reaches the sponge.
  - Short arm (28 mm) so only the top edge of the sponge is held; the
    rest hangs free in the air.

UX:
  - Insert: push sponge up against the tips, feel them spread, then
    "click" past as the wider zone above receives the bulk of the
    sponge.
  - Remove: pull down — same click-back-through-tips action.
  - No mechanical opening; the prongs flex as a clothespin would.

Print orientation: walls vertical (Z), gap in X, narrow tips on the
bed. The 14 mm cap span at the top bridges fine in PLA without
supports.
"""

from pathlib import Path

import generate_stl as g

GAP_TOP_MM     = 14.0   # wider top (cap end, hinge)
GAP_BOTTOM_MM  = 6.0    # narrow tips (the actual pinch)
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
    print(f"Variant: clothespin fork-pinch · tips {GAP_BOTTOM_MM} mm → "
          f"throat {GAP_TOP_MM} mm · arm {ARM_LEN_MM} mm · "
          f"{NUM_PRONGS} prongs/side")
    print("Test:")
    print(f"  [ ] Sponge clicks past the bottom tips with deliberate pressure")
    print(f"  [ ] Tips spring back — sponge stays without slipping")
    print(f"  [ ] Bottom of sponge hangs free → drips dry")
    print(f"  [ ] Pull-down release also clicks past the tips, no jamming")
    print(f"  [ ] Tip prongs flex without cracking at their base")


if __name__ == "__main__":
    main()
