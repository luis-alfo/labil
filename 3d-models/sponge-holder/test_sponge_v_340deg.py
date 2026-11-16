#!/usr/bin/env python3
"""MVP variant 2: C-clip with 340° wrap (mouth = 20°, near-closed ring).

Aggressive grip: the mouth is barely wider than the inner gap, so the
sponge has to be pushed firmly through. May crack at the mouth tips
in PLA — drop wrap if so.

Print orientation: same as the original sponge clip (axis Y horizontal,
mouth -Z).
"""

from pathlib import Path

import generate_stl as g

GAP_MM     = 10.0
WRAP_DEG   = 340.0
LENGTH_MM  = 50.0

OUT = Path(__file__).with_name("test_sponge_v_340deg.stl")
WEB = Path(__file__).resolve().parents[2] / "docs" / "models" / "test_sponge_v_340deg.glb"


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
    print(f"Variant: 340° wrap, gap {GAP_MM} mm, length {LENGTH_MM} mm")
    print("Test:")
    print(f"  [ ] Sponge inserts (will require firm push)")
    print(f"  [ ] Sponge stays even under a hard tug")
    print(f"  [ ] Mouth tips survive insertion without cracking")


if __name__ == "__main__":
    main()
