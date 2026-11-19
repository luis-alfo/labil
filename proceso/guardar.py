#!/usr/bin/env python3
"""Guarda una imagen del proceso de diseño de Luis en el repo.

    python3 proceso/guardar.py <imagen> <objeto> <descripcion> [AAAA-MM-DD]

- La reduce a 1600 px en el lado largo y la guarda en JPEG (calidad 82), girada
  según su EXIF y sin metadatos (ni GPS ni datos del móvil).
- Destino: proceso/<objeto>/<fecha>-<descripcion>.jpg
- Imprime la línea para pegar en la lista `proceso` del estado en 3d-models/objetos.json.
"""
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

LADO = 1600


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def main() -> None:
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    origen, objeto, descripcion = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    fecha = sys.argv[4] if len(sys.argv) > 4 else date.today().isoformat()
    destino = Path(__file__).parent / objeto / f"{fecha}-{slug(descripcion)}.jpg"
    destino.parent.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(origen)).convert("RGB")
    im.thumbnail((LADO, LADO))
    im.save(destino, "JPEG", quality=82, optimize=True)
    ruta = destino.resolve().relative_to(Path(__file__).resolve().parents[1]).as_posix()
    print(f"{ruta} ({destino.stat().st_size // 1024} KB)")
    print(json.dumps({"de": ruta, "pie": descripcion, "fecha": fecha}, ensure_ascii=False))


if __name__ == "__main__":
    main()
