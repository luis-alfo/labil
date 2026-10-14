"""Cajón para el hueco de la isla con base Clickfinity real (no inventada).

La base son las placas "Gridfinity Clickfinity Baseplate" de NoWarrenty
(remix de las ClickPlates de jerrymk), licencia CC BY-NC-SA 4.0. Este script
NO incluye sus mallas: las lee del ZIP original que tiene Luis y genera
copias recortadas para uso personal en cajones-isla/clickfinity_local/
(ignorada por git).

Por qué hay que recortarlas: cada placa Clickfinity lleva un nervio completo
también en el borde exterior y orejas de cola de milano. Una placa de 3
columnas mide 131,7 mm sin orejas y 137 mm con ellas, y el hueco mide 130.
Se recorta a x ∈ [-0,2, 126,2] (medio nervio exterior fuera): siguen
intactos el chaflán interior y los brazos del clic de cada celda.

Reparto de las 8 filas (Clickfinity une placas dejando una fila libre que
cierran los conectores): placa 3x4 + fila de conectores + placa 3x3.

Piezas propias (este repo): frente, tramo A y tramo B de la bandeja, y las
llaves de mariposa.
"""
import os, sys, zipfile, io
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh, OpType

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import cajon as C
from cajon import box, frente, llave, alojamiento, patines, gramos

W, H, L, TF, Z_R = C.W, C.H, C.L, C.TF, C.Z_R
G = 42.0
FL_T = 1.2                       # suelo de la bandeja (tiras bajo las líneas de la rejilla)
TIRA = 6.0                       # ancho de cada tira
PARED = 1.0                      # laterales: interior 127 mm para la placa recortada de 126,4
PLACA_H = 4.0                    # alto de la placa Clickfinity
Z_PLACA = Z_R + FL_T             # la placa se apoya aquí
OREJA = 3.0                      # orejas W de las placas en los extremos (eje Y)
YG0 = TF + OREJA + 0.3           # primera línea de la rejilla
LINEAS_Y = [YG0 + G * k for k in range(9)]
LINEAS_X = [-63.0, -21.0, 21.0, 63.0]
Y_SPLIT = (LINEAS_Y[4] + LINEAS_Y[5]) / 2     # en mitad de la fila de conectores
RIM_H = 20.0                     # reborde por encima del suelo
RECORTE = (-0.2, 126.2)          # x conservado de las placas (coordenadas Clickfinity)
DENS_PETG = 1.27

ZIP_DEF = os.environ.get("CLICKFINITY_ZIP", "")


# --- bandeja propia ---------------------------------------------------------
def suelo(y_a, y_b):
    tiras = []
    for x in LINEAS_X:
        tiras.append(box(x - TIRA / 2, y_a, Z_R, TIRA, y_b - y_a, FL_T))
    for y in LINEAS_Y:
        lo, hi = max(y - TIRA / 2, y_a), min(y + TIRA / 2, y_b)
        if hi > lo:
            tiras.append(box(-W / 2 + PARED, lo, Z_R, W - 2 * PARED, hi - lo, FL_T))
    return Manifold.batch_boolean(tiras, OpType.Add) ^ box(-W / 2, y_a - 1, Z_R - 1, W, y_b - y_a + 2, FL_T + 2)


def rebordes(y_a, y_b):
    return (box(-W / 2, y_a, Z_R, PARED, y_b - y_a, FL_T + RIM_H)
            + box(W / 2 - PARED, y_a, Z_R, PARED, y_b - y_a, FL_T + RIM_H))


def tramo(y_a, y_b, trasera=False):
    m = suelo(y_a, y_b) + rebordes(y_a, y_b) + patines(max(y_a, C.FL_D), y_b)
    if trasera:
        yb = LINEAS_Y[-1] + OREJA + 0.3
        m += box(-W / 2, yb, Z_R, W, y_b - yb, FL_T + RIM_H)
        m += box(-W / 2 + PARED, LINEAS_Y[-1], Z_R, W - 2 * PARED, y_b - LINEAS_Y[-1], FL_T)
    for y, lado in ((max(y_a, C.FL_D), 1), (y_b, -1)):
        pad, hueco = alojamiento(y, lado)
        m = m + pad - hueco
    return m


def tramo_a():
    return tramo(TF, Y_SPLIT)


def tramo_b():
    return tramo(Y_SPLIT, L, trasera=True)


def frente_click(estilo="revoltons3"):
    # nervios por encima de la placa (no tocan su borde ni las orejas) y de 3 mm de fondo
    return frente(estilo, nervios_desde=Z_PLACA + PLACA_H + 0.4, nervios_fondo=OREJA)


# --- placas Clickfinity (leídas del ZIP de Luis) ----------------------------
def _manifold(data):
    m = trimesh.load(io.BytesIO(data), file_type="stl")
    return Manifold(Mesh(vert_properties=np.array(m.vertices, dtype=np.float32), tri_verts=np.array(m.faces, dtype=np.uint32)))


def leer_zip(ruta):
    with zipfile.ZipFile(ruta) as z:
        nombres = {os.path.basename(n): n for n in z.namelist()}
        return {k: _manifold(z.read(nombres[k])) for k in ("3x4.stl", "3x3.stl", "join_vertical_m.stl")}


def recorta(m):
    """Quita lo que sobresale del ancho útil (medio nervio exterior y orejas laterales)."""
    x0, x1 = RECORTE
    return m ^ box(x0, -50, -1, x1 - x0, 500, 10)


def kit_clickfinity(ruta):
    """Piezas Clickfinity recortadas y colocadas en el cajón (coordenadas del cajón)."""
    z = leer_zip(ruta)
    dx = LINEAS_X[0]                               # x Clickfinity 0 → x cajón -63
    sitio = {
        "placa_3x4": recorta(z["3x4.stl"]).translate((dx, LINEAS_Y[0], Z_PLACA)),
        "placa_3x3": recorta(z["3x3.stl"]).translate((dx, LINEAS_Y[5], Z_PLACA)),
    }
    # El conector viene tumbado a lo largo de X sobre la línea y=0; girado 90° queda sobre la
    # línea x=0 ocupando y ∈ [0,62; 41,38]: se coloca en la fila libre (entre líneas 4 y 5).
    jv = z["join_vertical_m.stl"].rotate((0, 0, 90))
    for k, xl in enumerate((0.0, 42.0, 84.0, 126.0)):
        sitio[f"conector_{k + 1}"] = recorta(jv.translate((xl, 0, 0))).translate((dx, LINEAS_Y[4], Z_PLACA))
    return sitio


def gramos_petg(m):
    return m.volume() / 1000 * DENS_PETG


def _tm(m):
    me = m.to_mesh()
    return trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts)


def exportar(ruta_zip=None):
    out_repo = os.path.join(AQUI, "..", "stl")
    os.makedirs(out_repo, exist_ok=True)
    propias = {"frente_revoltons3": frente_click(), "tramo_A": tramo_a(), "tramo_B": tramo_b(), "llave_mariposa": llave()}
    # orientación de impresión: frente boca abajo; tramos tal cual; llave tal cual
    imp = dict(propias)
    imp["frente_revoltons3"] = propias["frente_revoltons3"].rotate((90, 0, 0))
    for k, m in imp.items():
        bb = m.bounding_box()
        _tm(m.translate((-bb[0], -bb[1], -bb[2]))).export(os.path.join(out_repo, f"{k}.stl"))
    if ruta_zip:
        out_loc = os.path.join(AQUI, "..", "clickfinity_local")
        os.makedirs(out_loc, exist_ok=True)
        kit = kit_clickfinity(ruta_zip)
        nombres = {"placa_3x4": "placa_3x4_recortada", "placa_3x3": "placa_3x3_recortada",
                   "conector_1": "conector_exterior_izq_recortado", "conector_2": "conector_entero_a",
                   "conector_3": "conector_entero_b", "conector_4": "conector_exterior_der_recortado"}
        for k, m in kit.items():
            bb = m.bounding_box()
            _tm(m.translate((-bb[0], -bb[1], -bb[2]))).export(os.path.join(out_loc, nombres[k] + ".stl"))
    return propias


if __name__ == "__main__":
    exportar(sys.argv[1] if len(sys.argv) > 1 else ZIP_DEF or None)
