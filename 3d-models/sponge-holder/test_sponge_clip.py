#!/usr/bin/env python3
"""MVP test piece: only the sponge pinch clip (C-shape, gap 14 mm).

Print this on its own to validate:
- Whether a typical kitchen sponge fits and stays put
- Whether the 14 mm inner gap gives enough pinch on a ~25 mm sponge
- Whether 220° wrap in PLA flexes enough to admit the sponge

Orientation matches the main assembly: clip axis along the world Y
(horizontal). The piece lies on its curved back; print with a brim,
and let the slicer place tree supports for the downward-facing mouth.

Usage:  python3 test_sponge_clip.py
"""

from pathlib import Path

import generate_stl as g

OUT = Path(__file__).with_name("test_sponge_clip.stl")


def main():
    clip = g.make_sponge_clip()
    # The sponge clip in the main file is positioned to merge with the drop.
    # For an isolated test piece, recentre and rest on the bed.
    bmin, bmax = clip.bounds
    clip.apply_translation([
        -(bmin[0] + bmax[0]) / 2,
        -(bmin[1] + bmax[1]) / 2,
        -bmin[2],
    ])
    clip.export(OUT)

    bmin, bmax = clip.bounds
    size = bmax - bmin
    print(f"Wrote {OUT}")
    print(f"Triangles: {len(clip.faces)}")
    print(f"Bounding box (mm): X {size[0]:.1f}  Y {size[1]:.1f}  Z {size[2]:.1f}")
    print(f"Volume:    {clip.volume / 1000:.1f} cm³")
    print()
    print("Test checklist:")
    print("  [ ] Sponge slides in from below with moderate pressure")
    print("  [ ] Sponge stays in place against gravity (and a light tug)")
    print("  [ ] Clip mouth does not crack open during insertion")
    print()
    print("If the fit is wrong, edit generate_stl.py:")
    print("  sponge falls out      → decrease SPONGE_GAP (try 12 mm)")
    print("                         or increase SPONGE_CLIP_LEN_Y (try 60 mm)")
    print("  too hard to insert    → increase SPONGE_GAP (try 16 mm)")
    print("                         or decrease SPONGE_CLIP_WRAP_DEG (try 200°)")
    print("  clip cracks           → decrease SPONGE_CLIP_WRAP_DEG (more flex)")


if __name__ == "__main__":
    main()
