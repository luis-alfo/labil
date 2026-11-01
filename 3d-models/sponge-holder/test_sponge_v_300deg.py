#!/usr/bin/env python3
"""MVP variant 1: C-clip with 300° wrap (mouth = 60°).

Same geometry pattern as the original sponge clip, just more closed.
The mouth narrows from 140° to 60° so the sponge has to squeeze
through but the grip improves once it's inside.

Print orientation: same as the original sponge clip (axis Y horizontal,
mouth -Z) so the flex behaviour at the mouth is comparable.
"""

from pathlib import Path

import generate_stl as g

GAP_MM     = 10.0   # inner gap (sponge thickness, compressed)
WRAP_DEG   = 300.0
LENGTH_MM  = 50.0

OUT = Path(__file__).with_name("test_sponge_v_300deg.stl")
WEB = Path(__file__).resolve().parents[2] / "docs" / "models" / "test_sponge_v_300deg.glb"


def main():
    clip = g.build_c_clip(gap=GAP_MM, wrap_deg=WRAP_DEG, length_y=LENGTH_MM)
    bmin, bmax = clip.bounds
    clip.apply_translation([
        -(bmin[0] + bmax[0]) / 2,
        -(bmin[1] + bmax[1]) / 2,
        -bmin[2],
    ])
    clip.export(OUT)
    WEB.parent.mkdir(parents=True, exist_ok=True)
    clip.export(WEB)
    g.update_web_version()

    bmin, bmax = clip.bounds
    size = bmax - bmin
    print(f"Wrote {OUT}")
    print(f"Bounding box (mm): X {size[0]:.1f}  Y {size[1]:.1f}  Z {size[2]:.1f}")
    print(f"Volume: {clip.volume / 1000:.1f} cm³")
    print()
    print(f"Variant: 300° wrap, gap {GAP_MM} mm, length {LENGTH_MM} mm")
    print("Test:")
    print(f"  [ ] Sponge inserts with deliberate but not painful pressure")
    print(f"  [ ] Sponge stays under gravity + light tug")
    print(f"  [ ] Mouth tips don't crack on insertion")


if __name__ == "__main__":
    main()
