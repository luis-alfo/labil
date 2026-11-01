#!/usr/bin/env python3
"""MVP variant 3: parallel-wall pinch (clothespin-style).

Two flat 50 mm-long parallel walls 8 mm apart, joined by a top cap. The
sponge slides up between the walls and is gripped by friction along the
full wall area instead of by two narrow contact lines (which is what a
cylindrical C-clip gives you).

Pros vs. cylindrical:
  - Pressure distributed over a large flat contact area
  - No rotation of the sponge inside the clip
  - Gap easy to dial independently of wrap angle

Cons:
  - Slightly more material
  - Less flex than a partial ring; relies more on sponge compression

Print orientation: walls vertical (Z), gap in X, length along Y. Print
upright with the open mouth on the bed and the cap on top — bridging
across the cap is short enough (10 mm × wall thickness) to print
without supports in PLA.
"""

from pathlib import Path

import generate_stl as g

GAP_MM      = 8.0    # inner gap (sponge thickness, compressed)
ARM_LEN_MM  = 50.0   # how far the parallel walls extend (Z axis)
LENGTH_MM   = 50.0   # along sponge edge (Y axis)

OUT = Path(__file__).with_name("test_sponge_v_parallel.stl")
WEB = Path(__file__).resolve().parents[2] / "docs" / "models" / "test_sponge_v_parallel.glb"


def main():
    pinch = g.build_parallel_pinch(
        gap=GAP_MM,
        arm_l=ARM_LEN_MM,
        length_y=LENGTH_MM,
    )
    # rest the bottom on Z=0 (open mouth on the bed)
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
    print(f"Variant: parallel-wall pinch, gap {GAP_MM} mm, "
          f"arm {ARM_LEN_MM} mm, length {LENGTH_MM} mm")
    print("Test:")
    print(f"  [ ] Sponge slides in cleanly (no jamming on the cap)")
    print(f"  [ ] Sponge stays under gravity + repeated light tugs")
    print(f"  [ ] Walls don't deform permanently with the sponge in")


if __name__ == "__main__":
    main()
