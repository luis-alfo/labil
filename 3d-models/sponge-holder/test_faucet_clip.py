#!/usr/bin/env python3
"""MVP test piece: only the faucet clip (abrazadera) for the 45 mm shaft.

Print this on its own to validate:
- Whether the clip snaps onto the faucet shaft
- Whether the inner Ø (45.4 mm) gives a good fit (snug but not over-tight)
- Whether 240° wrap angle in PLA gives enough flex without breaking

Orientation matches the main assembly (axis Z, vertical) so the layer
direction is identical to what the full piece will have. Print flat on
the bed with a brim.

Usage:  python3 test_faucet_clip.py
"""

from pathlib import Path

import generate_stl as g

OUT = Path(__file__).with_name("test_faucet_clip.stl")


def main():
    clip = g.make_faucet_clip()
    # rest the bottom on Z=0 so the slicer doesn't have to reposition it
    bmin, _ = clip.bounds
    clip.apply_translation([0, 0, -bmin[2]])
    clip.export(OUT)

    bmin, bmax = clip.bounds
    size = bmax - bmin
    print(f"Wrote {OUT}")
    print(f"Triangles: {len(clip.faces)}")
    print(f"Bounding box (mm): X {size[0]:.1f}  Y {size[1]:.1f}  Z {size[2]:.1f}")
    print(f"Volume:    {clip.volume / 1000:.1f} cm³")
    print()
    print("Test checklist:")
    print("  [ ] Snaps onto the 45 mm faucet shaft with a clear click")
    print("  [ ] Stays in place when pulled gently")
    print("  [ ] Does not crack at the mouth tips when opened")
    print()
    print("If the fit is wrong, edit CLIP_INNER_D in generate_stl.py:")
    print("  too tight   → increase by 0.2 mm")
    print("  too loose   → decrease by 0.2 mm")
    print("  cracks open → decrease CLIP_WRAP_DEG (e.g. 220) or switch to PETG")


if __name__ == "__main__":
    main()
