# CLAUDE.md

Project guide auto-loaded by Claude Code on every session in this repo.

## Project

This repo has two distinct concerns:

1. **Labil** (`/src`, `package.json`, etc.) — Next.js app for AI-powered
   diagram generation. See `README.md` for that side.
2. **3D-printable parts** (`/3d-models`, `/docs`, `/.github/workflows/pages.yml`,
   `.claude/skills/3d-printable-from-photo/`) — parametric models, MVP
   test pieces, and a mobile-friendly viewer. The rest of this file is
   the playbook for that workflow.

If the user's request is unrelated to 3D-printable design (e.g. they ask
about the Next.js app), you can ignore the rest of this file.

---

# Designing 3D-printable parts from a photo

End-to-end playbook for the loop **photo → parametric model → MVP test
pieces → mobile preview → printed part**, learned from the
sponge-holder design (`/3d-models/sponge-holder/`). Apply to any new
printable: clips, brackets, hooks, holders, jigs.

## Phase 1 — Discovery (do not skip)

Before generating any geometry, ask the user. **Hand-drawn dimensions
on a photo are almost always ambiguous**; assumptions cost a print.

Always ask these five:

1. **Critical interface dimensions** — the diameter / width of every
   surface the part will touch. A photo arrow saying "45" could be a
   diameter, an arc length, a chord, or a hand-drawn approximation.
2. **Which sketched number maps to which dimension** — confirm each
   annotation by name ("`50` is the cradle bottom, right?").
3. **Material** (PLA / PETG / TPU). Drives wall thickness, fit
   tolerance, and clip wrap angle:
   - PLA: ±0.4 mm fit, 220–240° wrap (rigid → less flex).
   - PETG: ±0.3 mm fit, 220–260° wrap.
   - TPU: ±0 mm fit, 360° rings OK (flexes freely).
4. **Function vs. existing object** — is the user copying a part they
   already own, or designing a replacement / improvement? Affects how
   precisely to mimic the reference.
5. **Where the part hides / sticks out** — front, back, side. Drives
   the orientation of secondary features ("brazo por detrás" =
   the arm exits the side opposite the clip mouth).

Other questions when relevant: held object size (sponge, brush…), how
the user installs the part (snap from radial direction vs. slide axially),
whether AR-on-phone preview is wanted.

When the user pushes back ("just make it"), still call out what you
assumed in 2-3 lines so they can correct on first feedback.

## Phase 2 — Parametric model

Always parametric. Hard-coded dimensions waste the user's iteration time.

### Toolchain

Two parallel files, same parameters, kept in sync:

| File | Purpose |
| --- | --- |
| `generate_stl.py` | Source of truth. Uses `trimesh` + `shapely` + `manifold3d`. Outputs both STL (printing) and GLB (web preview). |
| `*.scad` | Human-readable mirror in OpenSCAD for users who prefer that ecosystem. Optional but cheap to maintain. |

Required Python deps (install from CI or local):

```
pip install trimesh shapely manifold3d numpy-stl
```

### File skeleton

```python
# === Parameters (mm) at the top, comment every one ===
WALL_T          = 4.0
CLIP_INNER_D    = 45.4   # 45 mm shaft + 0.4 mm fit tolerance for PLA
CLIP_WRAP_DEG   = 240.0  # PLA-friendly snap (less wrap = more flex)
# ...

OUT_FILE = Path(__file__).with_name("part.stl")
WEB_DIR  = Path(__file__).resolve().parents[2] / "docs" / "models"
WEB_FILE = WEB_DIR / "part.glb"

def make_clip(): ...          # one function per primitive feature
def make_arm_drop(): ...      # uses shapely buffer for swept profiles
def make_sponge_clip(): ...

def main():
    parts = [make_clip(), make_arm_drop(), make_sponge_clip()]
    holder = trimesh.boolean.union(parts, engine="manifold")
    holder.export(OUT_FILE)
    holder.export(WEB_FILE)
    update_web_version()      # bumps cache-buster for mobile viewer
```

### Recipes that came up here

| Need | Recipe |
| --- | --- |
| Partial-cylinder snap clip (axis Z, mouth on +X) | `partial_annulus(r_in, r_out, half_open, 360 - half_open)` → `extrude_polygon` |
| C-clip with a different axis (e.g. axis Y, mouth -Z) | Build with axis Z + mouth +Y, then `rotation_matrix(-π/2, [1,0,0])` |
| Smooth 90° fillet between two perpendicular straps | Define centerline polyline (two segments + quarter-arc) in XZ; `LineString(pts).buffer(WALL_T/2, cap_style=2, join_style=2)`; `extrude_polygon`; rotate so extrusion is along Y |
| Booleans must be manifold | `trimesh.boolean.union(parts, engine="manifold")`; check `holder.is_volume` after |
| Tiny welding overlap so booleans don't crack | `CLIP_OVERLAP = 0.6` mm — every junction overlaps neighbours by this |

### Verification before declaring done

Always print these three after `main()`:

```python
bb_min, bb_max = holder.bounds
print(f"Bounding box (mm): {bb_max - bb_min}")
print(f"Volume:    {holder.volume / 1000:.1f} cm³")
print(f"Manifold:  {holder.is_volume}")          # MUST be True
```

If `is_volume` is False, the slicer will silently produce garbage.
Investigate before exporting.

## Phase 3 — MVP test pieces

**Print every interface in isolation before the full part.** Two
benefits: shorter prints (~15 min vs ~1 h) and decoupled feedback
(grip vs. structure).

For a part with N interfaces, generate N test scripts that import
shared functions:

```python
# test_faucet_clip.py
import generate_stl as g

def main():
    clip = g.make_faucet_clip()
    bmin, _ = clip.bounds
    clip.apply_translation([0, 0, -bmin[2]])    # rest on bed
    clip.export(Path(__file__).with_name("test_faucet_clip.stl"))
    clip.export(WEB_DIR / "test_faucet_clip.glb")
    g.update_web_version()
```

**Critical: the test piece must be printed in the same orientation as
in the assembled part.** Otherwise the layer direction changes and the
flex behaviour observed in the test won't match the final piece.

Print each test piece with its own GLB and a clear checklist of
acceptance criteria the user can tick:

```
[ ] Snaps onto the 45 mm shaft with a clear click
[ ] Stays in place under a gentle pull
[ ] No cracks at the mouth tips after opening
```

## Phase 4 — Print orientation (PLA in particular)

PLA is rigid. Layer adhesion is the weak axis. The single most
important choice for clips is:

> **Lay layer lines in the plane of the flex stress.**

For a partial-ring clip flexed radially:
- **Axis-vertical (ring lies horizontal)**: layers are circumferential
  → fibers carry the bending stress → **strong**.
- **Axis-horizontal (ring lies vertical)**: layers cut across the ring
  → bending crosses layer adhesion → **weak**.

When the part has two clips with perpendicular axes (sponge holder),
prioritise the load-bearing one (the clip that supports the part's
weight).

Other PLA settings to recommend by default:

- 5 perimeters, 30–40 % gyroid infill.
- 0.20 mm layer height, 210 °C nozzle, 60 °C bed.
- Brim 6–10 mm if the bed contact is a curved surface (line contact).
- Tree supports, "touching build plate only".
- Slow first layer (20 mm/s), normal speed elsewhere (50–60 mm/s).

## Phase 5 — Mobile preview pipeline

Goal: user sees the latest model on their phone after every push,
with AR if they want, **without manually running anything**.

The repo has **a single shared viewer** that lists every printable
design in the project. New designs always get **added to that viewer
as a new section + tab**, never their own page.

Stack:

```
3d-models/
├── sponge-holder/          # one folder per design
│   ├── generate_stl.py
│   └── test_*.py
└── <new-design>/           # new designs go here
    └── generate_stl.py

docs/
├── index.html              # <model-viewer> + sticky tabs + scroll-snap
└── models/
    ├── sponge_holder.glb   # one .glb per visible model in the viewer
    ├── <new-design>.glb    # generators write to /docs/models/...
    └── version.txt         # shared cache-buster timestamp

.github/workflows/pages.yml # regenerates ALL GLBs in CI, deploys /docs
```

Key points:

- Use **GLB** (not STL) for the viewer. trimesh can `.export(*.glb)`
  natively. Smaller, faster, and `<model-viewer>` only accepts GLB/glTF.
- **Cache-busting**: write a unix timestamp to `models/version.txt` on
  every regeneration; in `index.html`, fetch it (with `?_=Date.now()`
  to bypass cache *for the version file itself*) and append `?v=<ts>`
  to every `<model-viewer src>`. Mobile Safari caches GLBs aggressively
  otherwise. The version file is shared across all designs.
- **GitHub Actions** workflow on `push` to `3d-models/**` or
  `docs/**`: install Python deps, glob `3d-models/*/` and run every
  `generate_stl.py` + `test_*.py` it finds, then
  `actions/upload-pages-artifact` + `actions/deploy-pages`. User must
  set `Settings → Pages → Source = "GitHub Actions"` (one click).
- **Don't** enable `cache: pip` in `setup-python` unless there is a
  `requirements.txt` / `pyproject.toml` — it errors out otherwise.

### Adding a new design to the viewer (do this every time)

When the user asks for a new printable, after Phase 1–4 produce a new
`3d-models/<design>/generate_stl.py`, then **edit `/docs/index.html`**
to include the new model. Concretely:

1. Have the generator write `<design>.glb` to `docs/models/`. Use the
   same `WEB_DIR = Path(__file__).resolve().parents[2] / "docs" / "models"`
   pattern as the sponge-holder.
2. **Add a tab** to the sticky `<nav class="tabs">` block:
   ```html
   <a href="#<design>" data-target="<design>"><Display name></a>
   ```
3. **Append a section** to `<main>` after the existing ones, copying
   the structure of the sponge-holder sections (eyebrow / h2 / lede /
   model-viewer / dl.meta). Use `data-src="models/<design>.glb"` —
   the cache-busting JS picks it up automatically.
4. **No JS changes needed.** `IntersectionObserver` discovers new
   sections via `document.querySelectorAll("main section")`, and the
   tab→scroll handler binds to every `.tabs a`.
5. **No workflow changes needed.** `pages.yml` already globs
   `3d-models/*/`, so new designs are picked up automatically.
6. Update the `Modelo NN` numbering on the eyebrow if you want, or
   just let the order in `<main>` define it.

Do not create a second HTML file or a second route. The single
`/docs/index.html` is the catalogue for everything 3D-printable in
this repo.

### `<model-viewer>` boilerplate

```html
<model-viewer
  data-src="models/part.glb"
  alt="..."
  auto-rotate camera-controls
  ar ar-modes="webxr scene-viewer quick-look"
  shadow-intensity="0.7" exposure="1.05">
</model-viewer>
```

`data-src` (not `src`) is filled in by the cache-busting JS at runtime.

### UI patterns that worked

- Beige / cream palette (`#F5F1E8` bg, `#C2410C` accent) and Source
  Serif 4 — feels handmade, unobtrusive, matches the "physical
  artefact" theme. Keep this consistent across new sections so the
  catalogue feels like one project.
- Sticky top bar with one pill-tab per model.
- `<main>` is the scroll container with `scroll-snap-type: y mandatory`
  and each `<section>` has `scroll-snap-align: start; scroll-snap-stop:
  always; min-height: calc(100dvh - var(--nav-h))`.
- Active tab tracked with `IntersectionObserver` rooted on `<main>`.
- Click on tab → `target.scrollIntoView({ behavior: "smooth" })`.
- Use `100dvh`, not `100vh`, on mobile (the URL bar steals height).

## Iteration loop, end to end

```
edit param in generate_stl.py
  → git commit -am "tweak: gap 12 mm" && git push
  → CI regenerates STL + GLB (1-2 min)
  → mobile URL refreshes
  → user prints test piece, gives feedback
  → adjust by 0.2 mm, repeat
```

Default answers when something doesn't fit:

| Symptom | First adjustment |
| --- | --- |
| Clip too tight | `CLIP_INNER_D += 0.2 mm` |
| Clip too loose | `CLIP_INNER_D -= 0.2 mm` |
| Clip cracks on installation | `CLIP_WRAP_DEG -= 20°` (more flex) or switch to PETG |
| Held object falls out | Decrease pinch gap, or extend grip length |
| Held object impossible to insert | Increase gap, or open the mouth wider |
| Layer lines failing on flex | Re-orient so layer plane contains the flex axis |

## Anti-patterns to avoid

- ❌ Generating STL with sharp internal corners on load-bearing
  joints. Always fillet (8 mm radius is a safe default for ~4 mm
  walls).
- ❌ Skipping `is_volume` check before export.
- ❌ Rotating the test piece to a "convenient" print orientation
  different from the assembled part — invalidates the test.
- ❌ Asserting one specific orientation is "best" for parts with
  perpendicular clip axes — there is always a trade-off, name it.
- ❌ Committing huge meshes (`ARC_SEG > 200`). 96 segments is plenty
  for visual smoothness; the printer's nozzle averages anything
  finer.
- ❌ Using STL for the web viewer. GLB is ~30 % the size and renders
  faster on phones.
- ❌ `cache: pip` in setup-python without a manifest file (silent CI
  failure).
- ❌ Creating a second HTML page or route for new designs. Always
  extend `/docs/index.html`.

## Reference implementation

`/3d-models/sponge-holder/` is the canonical example of this playbook
applied end to end:

- `generate_stl.py` — main parametric model
- `test_faucet_clip.py`, `test_sponge_clip.py` — MVP test pieces
- `sponge_holder.scad` — OpenSCAD mirror
- `/docs/index.html` — mobile preview
- `/.github/workflows/pages.yml` — auto-deploy

Read those files before starting a new design — most of the recipes
above are already inlined and battle-tested.
