---
name: 3d-printable-from-photo
description: Use when the user shares a photo (often with hand-drawn measurements) and wants a 3D-printable part — designs a parametric model, generates STL+GLB, prints test MVPs first, and sets up a mobile-friendly web preview that auto-updates on each iteration. Triggers on "modelo 3D", "imprimir en 3D", "STL", "OpenSCAD", "pieza paramétrica", or any photo-with-dimensions request for a printable object.
---

# 3D-printable design playbook

The full content of this skill lives in **`/CLAUDE.md`** at the repo
root, so it is auto-loaded by Claude Code Cloud sessions even when
project-level skills aren't discovered.

If you are reading this via the skill mechanism, open `/CLAUDE.md` and
follow the "Designing 3D-printable parts from a photo" section. It
documents the full loop: discovery questions → parametric model with
trimesh + shapely + manifold3d → MVP test pieces → PLA print
orientation → shared mobile-viewer pipeline (single `/docs/index.html`
with sticky tabs, scroll-snap, GLB cache-busting, GitHub Pages via
Actions).

The canonical reference implementation is `/3d-models/sponge-holder/`.
