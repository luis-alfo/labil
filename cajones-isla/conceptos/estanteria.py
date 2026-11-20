"""La columna de huecos de la isla, modelada para ver cada pieza en su sitio.

No es una pieza para imprimir: es el contexto. Sale de dos fotos de Luis
(2026-10-13 y 2026-11-20) y de tres medidas suyas: hueco de 130 × 135 mm y 350 mm
de fondo. Todo lo demás (grosor de los tableros, zócalo, encimera, cajones de al
lado) está estimado de las fotos y solo sirve para situar la pieza.

Ejes de la escena (mm): x = a lo ancho, visto de frente (0 = centro del hueco);
y = hacia el fondo del mueble (0 = cara delantera); z = hacia arriba (0 = suelo).
"""
from manifold3d import Manifold, OpType

# === Medido por Luis ===
ANCHO_HUECO = 130.0
ALTO_HUECO = 135.0
FONDO_HUECO = 350.0

# === Estimado de las fotos ===
N_HUECOS = 5            # se cuentan 5 en la foto del 13 de octubre
TABLERO = 18.0          # grosor de costados y estantes
TRASERA = 8.0
ZOCALO = 100.0          # alto del zócalo
ZOCALO_RETIRO = 45.0
ENCIMERA = 20.0
VUELO = 20.0            # lo que sobresale la encimera
COSTADO_ISLA = 20.0     # el panel lacado del extremo de la isla, a la derecha
CAJONES_ANCHO = 190.0   # un trozo del módulo de cajones de la izquierda
GOLA = 22.0             # ranura entre frentes de cajón

# colores (sRGB 0-1)
BLANCO = (0.84, 0.83, 0.80)
FRENTE = (0.80, 0.79, 0.75)
PIEDRA = (0.78, 0.74, 0.68)
GRIS = (0.44, 0.47, 0.50)
SUELO = (0.36, 0.35, 0.34)
OSCURO = (0.20, 0.20, 0.20)


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def suelo_hueco(k):
    """Altura (z) del suelo del hueco k; k = 0 es el de abajo."""
    return ZOCALO + TABLERO + k * (ALTO_HUECO + TABLERO)


def alto_mueble():
    return ZOCALO + (N_HUECOS + 1) * TABLERO + N_HUECOS * ALTO_HUECO


def estanteria():
    """Lista de (Manifold, color, tamaño de malla en mm) con las partes del mueble."""
    w, h, d = ANCHO_HUECO, ALTO_HUECO, FONDO_HUECO
    xi, xd = -w / 2 - TABLERO, w / 2 + TABLERO
    top = alto_mueble()
    fondo = d + TRASERA

    columna = box(xi, xd, 0, fondo, ZOCALO, top)
    for k in range(N_HUECOS):
        z = suelo_hueco(k)
        columna -= box(-w / 2, w / 2, -1, d, z, z + h)

    costado = box(xd, xd + COSTADO_ISLA, 0, fondo, 0, top)

    # módulo de cajones de la izquierda: cuerpo y tres frentes separados por la gola
    xc = xi - CAJONES_ANCHO
    cuerpo = box(xc, xi, TABLERO, fondo, ZOCALO, top)
    alto_frente = (top - ZOCALO - 2 * GOLA) / 3
    frentes = Manifold.batch_boolean(
        [box(xc, xi - 2, 0, TABLERO, ZOCALO + i * (alto_frente + GOLA), ZOCALO + i * (alto_frente + GOLA) + alto_frente)
         for i in range(3)], OpType.Add)
    golas = Manifold.batch_boolean(
        [box(xc, xi - 2, 6, TABLERO, ZOCALO + (i + 1) * alto_frente + i * GOLA, ZOCALO + (i + 1) * (alto_frente + GOLA))
         for i in range(2)], OpType.Add)

    zocalo = box(xc, xd, ZOCALO_RETIRO, fondo, 0, ZOCALO)
    encimera = box(xc, xd + COSTADO_ISLA + VUELO, -VUELO, fondo, top, top + ENCIMERA)
    suelo = box(xc - 40, xd + COSTADO_ISLA + 130, -300, fondo + 20, -8, 0)

    return [
        (columna, BLANCO, 70.0),
        (costado, FRENTE, 70.0),
        (cuerpo, BLANCO, 90.0),
        (frentes, FRENTE, 70.0),
        (golas, OSCURO, 90.0),
        (zocalo, GRIS, 70.0),
        (encimera, PIEDRA, 70.0),
        (suelo, SUELO, 90.0),
    ]
