#!/usr/bin/env python3
"""Luz del visor 3D de la web: escribe docs/luz-visor.hdr.

El entorno «neutral» de <model-viewer> ilumina igual desde todos lados y las piezas
claras se ven planas, sin relieve. Este entorno es un estudio sencillo:

  - una luz principal grande arriba, delante y a la izquierda,
  - una luz de relleno más floja a la derecha,
  - un contraluz estrecho detrás, para que se recorten los cantos,
  - techo gris y suelo oscuro.

Así cada cara recibe una luz distinta según hacia dónde mira y se lee el volumen.
Es una imagen equirrectangular HDR (formato Radiance, sin comprimir) de 256 × 128.

Uso: python3 3d-models/luz_visor.py
"""
from pathlib import Path

import numpy as np

W, H = 256, 128
SALIDA = Path(__file__).resolve().parents[1] / "docs" / "luz-visor.hdr"

# (dirección hacia la luz en el marco del visor: x derecha, y arriba, z hacia quien mira,
#  anchura angular en grados, intensidad)
LUCES = [
    ((-0.55, 0.65, 0.55), 34.0, 9.0),    # principal
    ((0.85, 0.25, 0.45), 40.0, 2.2),     # relleno
    ((0.25, 0.45, -0.85), 22.0, 3.0),    # contraluz
]
TECHO, HORIZONTE, SUELO = 0.55, 0.28, 0.10


def entorno() -> np.ndarray:
    # three.js: u = atan2(z, x) / 2π + 0,5 ; v = asin(y) / π + 0,5 (fila 0 = arriba)
    u = (np.arange(W) + 0.5) / W
    v = 1.0 - (np.arange(H) + 0.5) / H
    lon = (u - 0.5) * 2 * np.pi
    lat = (v - 0.5) * np.pi
    lon, lat = np.meshgrid(lon, lat)
    d = np.stack([np.cos(lat) * np.cos(lon), np.sin(lat), np.cos(lat) * np.sin(lon)], axis=-1)
    y = d[..., 1]
    base = np.where(y >= 0, HORIZONTE + (TECHO - HORIZONTE) * y, HORIZONTE + (SUELO - HORIZONTE) * np.minimum(-y * 3, 1))
    img = np.repeat(base[..., None], 3, axis=-1)
    for direccion, ancho, intensidad in LUCES:
        l = np.array(direccion, float)
        l /= np.linalg.norm(l)
        ang = np.degrees(np.arccos(np.clip(d @ l, -1, 1)))
        img += intensidad * np.exp(-0.5 * (ang / (ancho / 2)) ** 2)[..., None]
    return img.astype(np.float32)


def escribir_hdr(img: np.ndarray, ruta: Path) -> None:
    m = img.max(axis=-1)
    e = np.where(m > 1e-32, np.ceil(np.log2(np.maximum(m, 1e-32))), 0)
    escala = np.where(m > 1e-32, 256.0 / (2.0 ** e), 0)
    rgbe = np.zeros(img.shape[:2] + (4,), np.uint8)
    rgbe[..., :3] = np.clip(img * escala[..., None], 0, 255).astype(np.uint8)
    rgbe[..., 3] = np.where(m > 1e-32, e + 128, 0).astype(np.uint8)
    cabecera = f"#?RADIANCE\nFORMAT=32-bit_rle_rgbe\n\n-Y {img.shape[0]} +X {img.shape[1]}\n".encode()
    ruta.write_bytes(cabecera + rgbe.tobytes())


if __name__ == "__main__":
    escribir_hdr(entorno(), SALIDA)
    print(f"{SALIDA.relative_to(SALIDA.parents[1])}: {SALIDA.stat().st_size // 1024} KB")
