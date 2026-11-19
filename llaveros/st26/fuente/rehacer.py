"""Rehace los STL de todos los estados del llavero ST26 a partir de las siluetas guardadas.

Las siluetas (`siluetas_artefacto.json`, en mm, trazados SVG con y hacia abajo) salieron del
trazado del logo y de los generadores originales. Aquí se extruyen con los grosores, biseles e
incrustaciones de cada estado (ver ../APRENDIZAJES.md).

Por cada estado escribe en llaveros/st26/<estado>/:
  st26-<estado>.stl            pieza completa (para la web y el coste)
  st26-<estado>_negro.stl      cuerpo, filamento 1
  st26-<estado>_blanco.stl     ST, filamento 2        (si tiene letras de color)
  st26-<estado>_naranja.stl    26, filamento 3

Uso: python3 rehacer.py
"""
import json
import re
from pathlib import Path

import numpy as np
import shapely
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

AQUI = Path(__file__).parent
ST26 = AQUI.parent
SIL = json.loads((AQUI / "siluetas_artefacto.json").read_text())
CAPA = 0.2   # mm, altura de capa: los biseles se escalonan por capas, como los imprime la A1

# estado -> silueta y parámetros (mm). base = cuerpo negro; relieve = letras por delante;
# detras = None | "espejo" (se lee bien por detrás) | "traspaso" (misma forma: se ve en espejo,
# como si las letras atravesaran); bisel = (cara de arriba, cara de la cama) en el agujero;
# boca = bisel de arriba en el borde del tapón.
ESTADOS = {
    "v1-silueta":       dict(sil="v1",    base=3.0, relieve=1.2),
    "reforzada":        dict(sil="v2",    base=3.0, relieve=1.2),
    "lateral":          dict(sil="lat",   base=3.0, relieve=1.2),
    "trazo-minimo":     dict(sil="v5",    base=3.0, relieve=1.2),
    "botella-primeras": dict(sil="bot1",  base=3.6, relieve=0.8),
    "botella-75cl":     dict(sil="botB",  base=3.6, relieve=0.8),
    "doble-cara":       dict(sil="doble", base=4.4, relieve=0.8, detras="espejo"),
    "tapon-macizo":     dict(sil="final", base=4.4, relieve=0.8, detras="espejo"),
    "bisel":            dict(sil="final", base=4.4, relieve=0.8, detras="espejo", bisel=(1.0, 1.0), boca=(1.0, 1.0)),
    "botella-ojal":     dict(sil="prop",  base=4.4, relieve=0.8, detras="espejo", bisel=(1.0, 1.0), boca=(1.0, 1.0)),
    "primera-capa":     dict(sil="prop",  base=4.4, relieve=0.8, detras="traspaso", bisel=(1.0, 0.0), boca=(1.0, 0.0)),
}
INCRUSTA = 0.8   # mm de letras incrustadas a ras por detrás (4 capas)


def rings(d):
    """Trazado SVG 'M x y L x y ... Z' -> lista de anillos (x, -y)."""
    out = []
    for sub in re.findall(r"M[^M]*", d):
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", sub)]
        pts = [(nums[i], -nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
        if len(pts) >= 3:
            out.append(pts)
    return out


def region(d):
    """Relleno par-impar (como el SVG): los anillos interiores son huecos."""
    geo = Polygon()
    for r in rings(d):
        geo = geo.symmetric_difference(Polygon(r).buffer(0))
    return geo.buffer(0)


def extrude(geo, z0, z1):
    geo = geo.buffer(0)
    if geo.is_empty:
        return None
    polys = list(geo.geoms) if hasattr(geo, "geoms") else [geo]
    ms = []
    for p in polys:
        if p.area < 1e-4:
            continue
        m = trimesh.creation.extrude_polygon(p, z1 - z0)
        m.apply_translation([0, 0, z0])
        ms.append(m)
    return trimesh.util.concatenate(ms) if ms else None


def union(ms):
    ms = [m for m in ms if m is not None]
    return trimesh.boolean.union(ms, engine="manifold") if len(ms) > 1 else ms[0]


def diff(a, bs):
    bs = [b for b in bs if b is not None]
    return trimesh.boolean.difference([a] + bs, engine="manifold") if bs else a


def escalones(perfil_de, grosor, z_cara, hacia_dentro):
    """Bisel de `grosor` mm a 45°, por capas, desde la cara z_cara hacia dentro (±1)."""
    piezas = []
    n = int(round(grosor / CAPA))
    for i in range(n):
        off = grosor - i * CAPA            # en la cara, todo el bisel; luego se estrecha
        za = z_cara - hacia_dentro * i * CAPA
        zb = z_cara - hacia_dentro * (i + 1) * CAPA
        piezas.append(extrude(perfil_de(off), min(za, zb) - (0.01 if i == 0 and hacia_dentro > 0 else 0),
                              max(za, zb) + (0.01 if i == 0 and hacia_dentro > 0 else 0)))
    return piezas


def construir(nombre, p):
    s = SIL[p["sil"]]
    base = region(s["base"])
    blanco = region(s["white"]).intersection(base)
    naranja = region(s["salmon"]).intersection(base)
    letras = unary_union([blanco, naranja])
    hx, hy = s["hole"][0], -s["hole"][1]
    T = p["base"]
    cuerpo = extrude(base, 0, T)
    cortes = []
    # agujero de la anilla: el anillo interior de la base que contiene el centro del agujero
    contorno = Polygon(base.exterior) if base.geom_type == "Polygon" else Polygon(max(base.geoms, key=lambda g: g.area).exterior)
    hueco = contorno.difference(base)
    hueco = [g for g in (hueco.geoms if hasattr(hueco, "geoms") else [hueco]) if g.contains(shapely.Point(hx, hy))]
    arriba, cama = p.get("bisel", (0, 0))
    if hueco:
        h = hueco[0]
        if arriba:
            cortes += escalones(lambda o: h.buffer(o, join_style=1), arriba, T + 0.01, +1)
        if cama:
            cortes += escalones(lambda o: h.buffer(o, join_style=1), cama, -0.01, -1)
    # boca: bisel del borde exterior del tapón (zona por encima del agujero menos 4 mm)
    b_arriba, b_cama = p.get("boca", (0, 0))
    zona = box(-1e3, hy - 4.0, 1e3, 1e3)
    def anillo(o):
        return contorno.difference(contorno.buffer(-o, join_style=2)).intersection(zona)
    if b_arriba:
        cortes += escalones(anillo, b_arriba, T + 0.01, +1)
    if b_cama:
        cortes += escalones(anillo, b_cama, -0.01, -1)

    detras = p.get("detras")
    trasera = {}
    if detras:
        cx = (contorno.bounds[0] + contorno.bounds[2]) / 2
        espejo = (lambda g: shapely.affinity.scale(g, -1, 1, origin=(cx, 0))) if detras == "espejo" else (lambda g: g)
        trasera = {"blanco": espejo(blanco).intersection(base.buffer(-0.6)),
                   "naranja": espejo(naranja).intersection(base.buffer(-0.6))}
        cortes += [extrude(g, -0.01, INCRUSTA) for g in trasera.values()]
    negro = diff(cuerpo, cortes)
    partes = {"negro": negro}
    for color, g in (("blanco", blanco), ("naranja", naranja)):
        ms = [extrude(g, T - 0.01, T + p["relieve"])]
        if color in trasera:
            ms.append(extrude(trasera[color], 0, INCRUSTA))
        partes[color] = union(ms)
    # en la v1 y sus borradores la pieza se imprimió con las letras del mismo color que pidió Luis
    completo = union(list(partes.values()))
    return partes, completo


def main():
    for nombre, p in ESTADOS.items():
        partes, completo = construir(nombre, p)
        d = ST26 / nombre
        d.mkdir(exist_ok=True)
        completo.export(d / f"st26-{nombre}.stl")
        for color, m in partes.items():
            m.export(d / f"st26-{nombre}_{color}.stl")
        ext = completo.extents
        print(f"{nombre:17s} {ext[0]:5.1f} × {ext[1]:5.1f} × {ext[2]:4.1f} mm  "
              f"{completo.volume / 1000:5.2f} cm³  cerrada={completo.is_volume}  "
              + " ".join(f"{c}={m.is_volume}" for c, m in partes.items()))


if __name__ == "__main__":
    main()
