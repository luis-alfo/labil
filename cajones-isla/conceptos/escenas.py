"""Escenas 3D para la web: cada pieza colocada en la columna de huecos de la isla.

Para cada escena escribe un GLB en docs/models/ con la estantería (estanteria.py) y
la pieza en su hueco. Las sombras van calculadas dentro del modelo: en cada vértice
se lanzan rayos y se mira cuánto tapa lo que hay alrededor (oclusión ambiental). Así
el interior de los huecos sale oscuro y la pieza deja sombra donde toca el mueble,
cosa que el visor de la web no sabe hacer solo.

La pieza va en verde fósforo (el color de «lo elegido» en la web), no en el color
real del filamento: si fuera blanca no se distinguiría del mueble.

Uso: python3 escenas.py            → escribe todos los GLB y cajones-isla/escenas.json
     (necesita embreex: pip install embreex)
"""
import json
import os
import struct
import sys

import numpy as np
import trimesh
from manifold3d import Manifold

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, ".."))

import cajon_click  # noqa: E402
import estanteria as E  # noqa: E402
import galga as G  # noqa: E402
import marco_prueba  # noqa: E402
import tapa as tapa_costillas  # noqa: E402
import tapa_lenguetas as TL  # noqa: E402
from cajon import llave  # noqa: E402

SALIDA = os.path.join(RAIZ, "docs", "models")
PIEZA = (0.30, 0.86, 0.34)          # verde fósforo, algo suavizado para que se vea el relieve
MALLA_PIEZA = 26.0                  # tamaño de malla de partida de la pieza (mm)

# oclusión ambiental
RAYOS = 48
ALCANCE = 300.0                     # mm: lo que está más lejos no da sombra
FUERZA = 0.96
CONTRASTE = 1.9                     # exponente: el visor no tapa su propia luz, así que la sombra va marcada
# la malla se afina sola donde la sombra cambia deprisa (bordes de sombra, contactos)
PASADAS = 5
SALTO = 0.11                        # diferencia de sombra entre vértices de una cara que obliga a partirla
MALLA_MIN = 6.0                     # mm: no se parte por debajo de esto


# --- mallas -----------------------------------------------------------------
def a_malla(m):
    me = m.to_mesh()
    return np.asarray(me.vert_properties[:, :3], float), np.asarray(me.tri_verts, np.int64)


def partir(v, f, cuales):
    """Parte por la mitad la arista más larga de las caras marcadas."""
    t = v[f[cuales]]
    k = np.linalg.norm(t[:, [1, 2, 0]] - t, axis=2).argmax(axis=1)
    fp = f[cuales]
    i = np.arange(len(fp))
    a, b, c = fp[i, k], fp[i, (k + 1) % 3], fp[i, (k + 2) % 3]
    m = len(v) + i
    v = np.vstack([v, (v[a] + v[b]) / 2])
    return v, np.vstack([f[~cuales], np.column_stack([a, m, c]), np.column_stack([m, b, c])])


def mas_larga(v, f):
    t = v[f]
    return np.linalg.norm(t[:, [1, 2, 0]] - t, axis=2).max(axis=1)


def bisecar(v, f, lmax):
    """Parte las caras hasta que ninguna arista mida más de lmax."""
    for _ in range(40):
        cuales = mas_larga(v, f) > lmax
        if not cuales.any():
            break
        v, f = partir(v, f, cuales)
    return v, f


def soldar(v, f):
    """Un vértice por posición y orientación de cara: las caras planas comparten vértices,
    las aristas vivas no. Devuelve vértices, caras, normal, un punto algo metido en la cara
    y el índice de la cara de entrada de cada cara de salida."""
    t = v[f]
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    area = np.linalg.norm(n, axis=1)
    ok = area > 1e-9
    origen = np.flatnonzero(ok)
    f, t, n = f[ok], t[ok], n[ok] / area[ok, None]
    clave = np.hstack([np.round(t.reshape(-1, 3) * 500).astype(np.int64),
                       np.round(np.repeat(n, 3, axis=0) * 5).astype(np.int64)])
    _, primero, inverso = np.unique(clave, axis=0, return_index=True, return_inverse=True)
    inverso = inverso.reshape(-1)
    v2 = t.reshape(-1, 3)[primero]
    n2 = np.repeat(n, 3, axis=0)[primero]
    f2 = inverso.reshape(-1, 3)
    # punto de salida de los rayos: el vértice, 0,35 mm hacia el centro de sus caras
    centros = np.zeros_like(v2)
    cuenta = np.zeros(len(v2))
    c = t.mean(axis=1)
    for j in range(3):
        np.add.at(centros, f2[:, j], c)
        np.add.at(cuenta, f2[:, j], 1)
    hacia = centros / cuenta[:, None] - v2
    largo = np.linalg.norm(hacia, axis=1, keepdims=True)
    dentro = v2 + hacia / np.maximum(largo, 1e-9) * np.minimum(largo, 0.35)
    return v2, f2, n2, dentro, origen


def direcciones(n):
    """RAYOS direcciones por vértice, repartidas con peso de coseno alrededor de su normal."""
    i = np.arange(RAYOS) + 0.5
    r = np.sqrt(i / RAYOS)
    ang = i * 2.399963229728653                                   # ángulo áureo
    lx, ly, lz = r * np.cos(ang), r * np.sin(ang), np.sqrt(1 - r * r)
    ref = np.where(np.abs(n[:, [2]]) < 0.9, [[0.0, 0.0, 1.0]], [[1.0, 0.0, 0.0]])
    tx = np.cross(ref, n)
    tx /= np.linalg.norm(tx, axis=1, keepdims=True)
    ty = np.cross(n, tx)
    return (tx[:, None, :] * lx[None, :, None] + ty[:, None, :] * ly[None, :, None]
            + n[:, None, :] * lz[None, :, None])


def oclusion(puntos, normales, escena):
    d = direcciones(normales).reshape(-1, 3)
    o = np.repeat(puntos + normales * 0.25, RAYOS, axis=0)
    donde, rayo, _ = escena.ray.intersects_location(o, d, multiple_hits=False)
    dist = np.linalg.norm(donde - o[rayo], axis=1)
    peso = np.clip(1 - dist / ALCANCE, 0, 1)
    tapa = np.zeros(len(o))
    tapa[rayo] = peso
    return 1 - tapa.reshape(-1, RAYOS).mean(axis=1)


def lineal(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


# --- GLB --------------------------------------------------------------------
def escribir_glb(ruta, v_mm, f, color_lineal):
    """GLB mínimo: posiciones, color por vértice e índices. Sin normales: el visor
    sombrea cada cara plana. Marco glTF: X derecha, Y arriba, Z hacia quien mira; metros."""
    pos = np.column_stack([v_mm[:, 0], v_mm[:, 2], -v_mm[:, 1]]).astype(np.float32) / 1000
    col = np.column_stack([np.clip(color_lineal, 0, 1), np.ones(len(v_mm))])
    col = np.round(col * 65535).astype(np.uint16)
    corto = len(v_mm) < 65536
    idx = f.astype(np.uint16 if corto else np.uint32).reshape(-1)

    trozos, vistas, desplaz = [], [], 0
    for datos, destino in ((idx, 34963), (pos, 34962), (col, 34962)):
        b = datos.tobytes()
        b += b"\x00" * (-len(b) % 4)
        vistas.append({"buffer": 0, "byteOffset": desplaz, "byteLength": len(datos.tobytes()), "target": destino})
        trozos.append(b)
        desplaz += len(b)
    binario = b"".join(trozos)
    gltf = {
        "asset": {"version": "2.0", "generator": "cajones-isla/conceptos/escenas.py"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0, "name": os.path.basename(ruta)[:-4]}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 1, "COLOR_0": 2}, "indices": 0, "material": 0}]}],
        "materials": [{"pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.0,
                                                "roughnessFactor": 0.82}}],
        "buffers": [{"byteLength": len(binario)}], "bufferViews": vistas,
        "accessors": [
            {"bufferView": 0, "componentType": 5123 if corto else 5125, "count": int(idx.size), "type": "SCALAR"},
            {"bufferView": 1, "componentType": 5126, "count": len(pos), "type": "VEC3",
             "min": pos.min(axis=0).tolist(), "max": pos.max(axis=0).tolist()},
            {"bufferView": 2, "componentType": 5123, "normalized": True, "count": len(col), "type": "VEC4"},
        ],
    }
    j = json.dumps(gltf, separators=(",", ":")).encode()
    j += b" " * (-len(j) % 4)
    total = 12 + 8 + len(j) + 8 + len(binario)
    with open(ruta, "wb") as fh:
        fh.write(struct.pack("<4sII", b"glTF", 2, total))
        fh.write(struct.pack("<I4s", len(j), b"JSON") + j)
        fh.write(struct.pack("<I4s", len(binario), b"BIN\x00") + binario)


def componer(partes, ruta):
    """partes = [(Manifold, color sRGB, tamaño de malla)]. Escribe el GLB con las sombras."""
    vs, fs, cs, base = [], [], [], 0
    for m, color, lmax in partes:
        v, f = bisecar(*a_malla(m), lmax)
        vs.append(v); fs.append(f + base)
        cs.append(np.tile(lineal(color), (len(v), 1)))
        base += len(v)
    v, f, c = np.vstack(vs), np.vstack(fs), np.vstack(cs)
    escena = trimesh.Trimesh(v, f, process=False)             # lo que da sombra no cambia al afinar
    for pasada in range(PASADAS + 1):
        v2, f2, n2, p2, origen = soldar(v, f)
        luz = oclusion(p2, n2, escena)
        if pasada == PASADAS:
            break
        salto = np.ptp(luz[f2], axis=1)
        cuales = np.zeros(len(f), bool)
        cuales[origen] = (salto > SALTO) & (mas_larga(v2, f2) > MALLA_MIN)
        if not cuales.any():
            break
        nv = len(v)
        v, f = partir(v, f, cuales)
        c = np.vstack([c, np.zeros((len(v) - nv, 3))])
        c[nv:] = c[f[-cuales.sum():, 2]]                       # el vértice nuevo hereda el color de su cara
    # color por vértice soldado: el del primer vértice original que cayó en él
    col2 = np.zeros((len(v2), 3))
    col2[f2.reshape(-1)] = c[f[origen].reshape(-1)]
    sombra = ((1 - FUERZA) + FUERZA * luz) ** CONTRASTE
    escribir_glb(ruta, v2, f2, col2 * sombra[:, None])
    return len(v2), len(f2)


# --- piezas en su sitio -----------------------------------------------------
def en_hueco(m, k, fuera=0.0):
    """Coloca una pieza (x centrado, y hacia el fondo, z desde el estante) en el hueco k."""
    return m.translate((0, -fuera, E.suelo_hueco(k)))


def marco():
    m, _, alto = marco_prueba.construir_marco(E.ANCHO_HUECO, E.ALTO_HUECO, 0.5, 1.6, 10.0, 6.0, 0.4)
    return m.rotate((90, 0, 0)).translate((0, 10.0, alto / 2))


def galga_ancho():
    m, anchos = G.galga()
    entra = sum(1 for w in anchos if w <= E.ANCHO_HUECO) * G.LARGO_PASO
    return m.rotate((0, 0, 180)).translate((0, entra, 0))


def galga_alto():
    m, anchos = G.galga()
    entra = sum(1 for w in anchos if w <= E.ALTO_HUECO) * G.LARGO_PASO
    m = m.rotate((0, 0, 180)).translate((0, entra, -G.GROSOR / 2))
    return m.rotate((0, 90, 0)).translate((0, 0, E.ALTO_HUECO / 2))


def cajon():
    piezas = [cajon_click.frente_click(), cajon_click.tramo_a(), cajon_click.tramo_b()]
    piezas += [llave().translate((x, y, 0)) for x in cajon_click.C.RAIL_X for y in (cajon_click.C.FL_D, cajon_click.Y_SPLIT)]
    m = Manifold()
    for p in piezas:
        m += p
    return m


def centro(m):
    b = m.bounding_box()
    return [(b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2]


def escenas():
    """(archivo, pieza colocada, distancia de cámara en m)"""
    hol = TL.HOLGURA
    return [
        ("cajones_marco_en_hueco", en_hueco(marco(), 2), 1.5),
        ("cajones_cajon_abierto", en_hueco(cajon(), 3, fuera=175.0), 1.75),
        ("cajones_tapa_costillas_bolsillo", en_hueco(tapa_costillas.tapa("bolsillo"), 1), 1.5),
        ("cajones_tapa_costillas_pasante", en_hueco(tapa_costillas.tapa("pasante"), 1), 1.5),
        ("cajones_galga_ancho", en_hueco(galga_ancho(), 2), 1.5),
        ("cajones_galga_alto", en_hueco(galga_alto(), 2), 1.5),
        ("cajones_aro_colocado", en_hueco(TL.tapa("aro", saliente=hol), 1), 1.5),
        ("cajones_aro_entrando", en_hueco(TL.tapa("aro"), 1, fuera=75.0), 1.5),
        ("cajones_tapa_lenguetas_colocada", en_hueco(TL.tapa("pasante", saliente=hol), 1), 1.5),
        ("cajones_tapa_lenguetas_entrando", en_hueco(TL.tapa("pasante"), 1, fuera=75.0), 1.5),
    ]


def main():
    os.makedirs(SALIDA, exist_ok=True)
    mueble = E.estanteria()
    camaras = {}
    solo = set(sys.argv[1:])
    for nombre, pieza, radio in escenas():
        if solo and nombre not in solo:
            continue
        ruta = os.path.join(SALIDA, nombre + ".glb")
        nv, nf = componer(mueble + [(pieza, PIEZA, MALLA_PIEZA)], ruta)
        x, y, z = centro(pieza)
        camaras[nombre] = {"glb": f"docs/models/{nombre}.glb",
                           "objetivo": f"{x / 1000:.3f}m {z / 1000:.3f}m {-y / 1000:.3f}m",
                           "orbita": f"32deg 76deg {radio}m"}
        print(f"{nombre}.glb: {nv} vértices, {nf} caras, {os.path.getsize(ruta) // 1024} KB")
    if not solo:
        with open(os.path.join(AQUI, "..", "escenas.json"), "w") as fh:
            json.dump(camaras, fh, ensure_ascii=False, indent=1)
            fh.write("\n")


if __name__ == "__main__":
    main()
