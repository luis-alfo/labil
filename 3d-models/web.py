#!/usr/bin/env python3
"""Genera los datos de la web (docs/) a partir de 3d-models/objetos.json.

- docs/data/objetos.json: objetos y estados con rutas web, gramos y euros por pieza.
- docs/models/archivo/*.glb: visor 3D de los estados que no tienen GLB propio.
- docs/files/<objeto>/<estado>/: copia de descargas e imágenes que viven fuera de docs/.

Se ejecuta en CI después de los generate_stl.py (ver .github/workflows/pages.yml),
así el coste de los diseños que se regeneran siempre está al día.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix

sys.path.insert(0, str(Path(__file__).parent))
import costes  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"
FUENTE = Path(__file__).with_name("objetos.json")
SALIDA = DOCS / "data" / "objetos.json"
ARCHIVO_GLB = DOCS / "models" / "archivo"

COLOR_PIEZA = (0.79, 0.88, 0.79, 1.0)   # ink-muted #c9e1c9 (LG Señal)
SEPARACION = 12.0                         # mm entre piezas en el visor


def web(ruta: Path) -> str:
    return ruta.relative_to(DOCS).as_posix()


def publicar(origen: str, obj: str, estado: str) -> str:
    """Ruta web de un archivo; lo copia a docs/files/... si vive fuera de docs/."""
    f = RAIZ / origen
    if not f.exists():
        raise SystemExit(f"falta {origen}")
    if f.is_relative_to(DOCS):
        return web(f)
    destino = DOCS / "files" / obj / estado / f.name
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists() or destino.read_bytes() != f.read_bytes():
        shutil.copyfile(f, destino)
    return web(destino)


def glb(fuentes: list[str], nombre: str) -> str:
    mallas = []
    x = 0.0
    for ruta in fuentes:
        m = trimesh.load(RAIZ / ruta, force="mesh")
        m.apply_translation(-np.array([m.bounds[0][0], (m.bounds[0][1] + m.bounds[1][1]) / 2,
                                       m.bounds[0][2]]))
        m.apply_translation([x, 0, 0])
        x += m.extents[0] + SEPARACION
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=COLOR_PIEZA, metallicFactor=0.0, roughnessFactor=0.7))
        mallas.append(m)
    escena = trimesh.Scene()
    for i, m in enumerate(mallas):
        escena.add_geometry(m, geom_name=f"{nombre}_{i}")
    centro = escena.bounds.mean(axis=0)
    escena.apply_translation([-centro[0], -centro[1], 0])
    escena.apply_transform(rotation_matrix(-np.pi / 2, [1, 0, 0]))  # glTF: Y arriba
    escena.apply_scale(0.001)                                       # metros (AR a tamaño real)
    ARCHIVO_GLB.mkdir(parents=True, exist_ok=True)
    salida = ARCHIVO_GLB / f"{nombre}.glb"
    escena.export(salida)
    return web(salida)


def fecha_cambio(rutas: list[str]) -> str | None:
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *rutas], cwd=RAIZ,
                             capture_output=True, text=True, check=True).stdout.strip()
        return out or None
    except Exception:
        return None


def main() -> None:
    fuente = json.loads(FUENTE.read_text())
    gramos_cache: dict[str, float] = {}
    salida = {"generado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
              "euros_kg": costes.EUROS_KG,
              "perfil": (f"A1 · capa {costes.CAPA} mm · relleno {costes.RELLENO:.0%} · "
                         f"PLA {costes.DENSIDAD} g/cm³"),
              "objetos": []}
    for obj in fuente["objetos"]:
        o = {k: v for k, v in obj.items() if k != "estados"}
        if obj.get("aprendizajes"):
            o["aprendizajes"] = publicar(obj["aprendizajes"], obj["id"], "notas")
        o["estados"] = []
        for est in obj["estados"]:
            e = {k: v for k, v in est.items()
                 if k not in ("modelos", "imagenes", "piezas", "descargas")}
            e["modelos"] = []
            for i, mod in enumerate(est.get("modelos", [])):
                src = (web(RAIZ / mod["glb"]) if "glb" in mod
                       else glb(mod["de"], f"{obj['id']}-{est['id']}-{i}"))
                e["modelos"].append({"nombre": mod["nombre"], "src": src})
            e["imagenes"] = [{"src": publicar(im["de"], obj["id"], est["id"]), "pie": im["pie"]}
                             for im in est.get("imagenes", [])]
            e["descargas"] = [publicar(d, obj["id"], est["id"]) for d in est.get("descargas", [])]
            piezas = []
            for p in est.get("piezas", []):
                if p["de"] not in gramos_cache:
                    gramos_cache[p["de"]] = costes.gramos(costes.cargar(RAIZ / p["de"]))
                n = p.get("cantidad", 1)
                g = gramos_cache[p["de"]] * n
                piezas.append({"nombre": p["nombre"], "cantidad": n, "gramos": round(g, 1),
                               "euros": round(g * costes.EUROS_KG / 1000, 2),
                               "fuente": Path(p["de"]).suffix.lstrip(".")})
            e["piezas"] = piezas
            if piezas:
                g = sum(p["gramos"] for p in piezas)
                e["coste"] = {"gramos": round(g, 1), "euros": round(g * costes.EUROS_KG / 1000, 2),
                              "origen": "estimado"}
            elif "real" in est:
                g = est["real"]["gramos"]
                e["coste"] = {"gramos": g, "euros": round(g * costes.EUROS_KG / 1000, 2),
                              "origen": "laminador"}
            fuentes = [p["de"] for p in est.get("piezas", [])] + est.get("descargas", [])
            e["cambiado"] = fecha_cambio(fuentes) if fuentes else None
            o["estados"].append(e)
            print(f"{obj['id']:>14} · {est['id']:<18} "
                  + (f"{e['coste']['gramos']:6.1f} g {e['coste']['euros']:5.2f} €" if "coste" in e else "—"))
        salida["objetos"].append(o)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
