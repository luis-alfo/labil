"""Perfiles oficiales de Bambu Studio (impresora, proceso, filamento) ya resueltos.

Descarga los JSON de resources/profiles/BBL del repositorio de BambuStudio en la etiqueta TAG,
sigue `inherits` hasta la raíz y mezcla las plantillas de `include` (sin ellas el proyecto queda
sin G-code de inicio y de fin). Guarda una caché en bbl_cache/ junto a este archivo.
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

TAG = "v02.08.04.61"
BASE = f"https://raw.githubusercontent.com/bambulab/BambuStudio/{TAG}/resources/profiles/BBL"
CACHE = Path(__file__).with_name("bbl_cache")
_index = None


def _get(sub_path):
    f = CACHE / sub_path
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        url = BASE + "/" + urllib.parse.quote(sub_path)
        with urllib.request.urlopen(url, timeout=60) as r:
            f.write_bytes(r.read())
    return json.loads(f.read_text())


def _path(kind, name):
    global _index
    if _index is None:
        f = CACHE / "BBL.json"
        if not f.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(BASE + ".json", timeout=60) as r:
                f.write_bytes(r.read())
        _index = json.loads(f.read_text())
    for e in _index[f"{kind}_list"]:
        if e["name"] == name:
            return e["sub_path"]
    raise KeyError(f"{kind}: {name}")


def resolved(kind, name):
    """kind: 'machine', 'process' o 'filament'. Devuelve el perfil completo como dict."""
    d = _get(_path(kind, name))
    out = resolved(kind, d["inherits"]) if d.get("inherits") else {}
    for inc in d.get("include", []):
        out.update({k: v for k, v in resolved(kind, inc).items() if k not in ("name", "instantiation")})
    out.update(d)
    out.pop("include", None)
    return out


if __name__ == "__main__":
    m = resolved("machine", "Bambu Lab A1 0.4 nozzle")
    print(len(m), "claves de impresora; G-code de inicio:", len(m.get("machine_start_gcode", "")), "caracteres")
