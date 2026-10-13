"""Cajón modular Gridfinity para el hueco de la isla (130 × 135 × 350 mm).

Piezas:  frente (intercambiable)  +  tramo 1  +  tramo 2
Uniones: "cola de milano a caída". Bajo la base corren dos patines; en cada
         junta, la pieza de delante saca una lengüeta en cola de milano y la de
         detrás tiene el hueco abierto por abajo: se monta bajando la pieza de
         detrás sobre la lengüeta. Tirar del cajón no la puede soltar.
"""
import math
import numpy as np
from manifold3d import CrossSection, Manifold, JoinType, OpType

PLA = 1.24                                # g/cm³

# --- hueco y cajón ---------------------------------------------------------
W, H, L = 129.0, 134.0, 348.0             # exterior del cajón
TF = 2.0                                  # grosor del frente
RIB = 6.0                                 # fondo de los nervios del frente
G, NX, NY = 42.0, 3, 8                    # rejilla Gridfinity
BP_H = 4.65                               # alto del perfil de la base
RIM_T, RIM_H = 1.2, 20.0                  # reborde lateral (por encima de la base)
Y0 = TF + RIB                             # donde empieza la base
Y_SPLIT = Y0 + 4 * G                      # junta tramo 1 / tramo 2

# --- uniones ---------------------------------------------------------------
Z_R = 3.0                                 # alto de los patines (la base va encima)
RAIL_W = 6.0                              # ancho del patín (bajo el nervio de la base)
RAIL_X = (-G / 2, G / 2)                  # bajo los nervios longitudinales de la base
DT_NECK, DT_HEAD, DT_LEN = 7.0, 11.0, 8.0 # cola de milano: cuello, cabeza, largo
DT_PAD = 17.0                             # ensanche del patín alrededor de la unión
HOLGURA_DT = 0.2                          # juego por lado en la cola de milano
FL_D = 10.0                               # fondo de la pestaña inferior del frente


def rrect(w, h, r, seg=24):
    r = max(0.0, min(r, w / 2 - 0.01, h / 2 - 0.01))
    if r == 0:
        return CrossSection.square((w, h), center=True)
    return CrossSection.square((w - 2 * r, h - 2 * r), center=True).offset(r, JoinType.Round, circular_segments=seg)


def box(x, y, z, sx, sy, sz):
    return Manifold.cube((sx, sy, sz)).translate((x, y, z))


def vertical(cs, grosor, chaflan=0.0, y=0.0):
    """Extruye un perfil (x, z) hacia +Y desde y. El chaflán va en la cara y (la vista)."""
    m = cs.extrude(grosor - chaflan)
    if chaflan > 0:
        b = cs.bounds()                                       # (xmin, ymin, xmax, ymax)
        w, h = b[2] - b[0], b[3] - b[1]
        k = ((w - 2 * chaflan) / w, (h - 2 * chaflan) / h)
        cx, cz = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        tapa = cs.translate((-cx, -cz)).extrude(chaflan, scale_top=k).translate((cx, cz, grosor - chaflan))
        m += tapa
    return m.rotate((90, 0, 0)).translate((0, y + grosor, 0))


def corte(cs, prof, chaflan=0.0):
    """Taladro pasante en el frente con boca achaflanada en la cara vista."""
    m = cs.extrude(prof + 2).translate((0, 0, -1))
    if chaflan > 0:
        b = cs.bounds()
        w, h = b[2] - b[0], b[3] - b[1]
        cx, cz = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        boca = cs.translate((-cx, -cz)).offset(chaflan, JoinType.Round, circular_segments=24)
        bw, bh = w + 2 * chaflan, h + 2 * chaflan
        m += boca.extrude(chaflan + 0.01, scale_top=(w / bw, h / bh)).translate((cx, cz, prof - chaflan))
        m += boca.extrude(1).translate((cx, cz, prof))
    return m.rotate((90, 0, 0)).translate((0, prof, 0))


def cola_milano(holgura=0.0, largo=DT_LEN, alto=Z_R):
    n, h = DT_NECK / 2 + holgura, DT_HEAD / 2 + holgura
    pts = [(-n, -0.01 - holgura), (n, -0.01 - holgura), (h, largo + holgura), (-h, largo + holgura)]
    return CrossSection([pts]).extrude(alto)


# --- base Gridfinity -------------------------------------------------------
def celda():
    a = rrect(36.3, 36.3, 0.8).extrude(0.71, scale_top=(37.7 / 36.3, 37.7 / 36.3))
    b = rrect(37.7, 37.7, 1.5).extrude(1.82).translate((0, 0, 0.69))
    c = rrect(37.7, 37.7, 1.5).extrude(2.16, scale_top=(41.6 / 37.7, 41.6 / 37.7)).translate((0, 0, 2.5))
    return (a + b + c).translate((0, 0, -0.005))


def base(y_ini, filas):
    slab = box(-NX * G / 2, y_ini, 0, NX * G, filas * G, BP_H)
    c = celda()
    cuts = [c.translate((-G + ix * G, y_ini + G / 2 + iy * G, -0.001)) for ix in range(NX) for iy in range(filas)]
    return (slab - Manifold.batch_boolean(cuts, OpType.Add)).translate((0, 0, Z_R))


def bandeja(y_a, y_b, filas, y_base, trasera=False):
    """Base + rebordes entre y_a e y_b (los rebordes y la base van sobre los patines)."""
    m = base(y_base, filas)
    xi = NX * G / 2
    for x in (-W / 2, xi):
        m += box(x, y_a, Z_R, W / 2 - xi, y_b - y_a, RIM_H + BP_H)
    if trasera:
        yb = y_base + filas * G
        m += box(-W / 2, yb, Z_R, W, y_b - yb, RIM_H + BP_H)
    return m


def patines(y_a, y_b):
    return Manifold.batch_boolean([box(x - RAIL_W / 2, y_a, 0, RAIL_W, y_b - y_a, Z_R + 0.01) for x in RAIL_X], OpType.Add)


def macho(y):
    """Lengüetas que salen hacia +Y desde y (con su ensanche de raíz)."""
    m = Manifold()
    for x in RAIL_X:
        m += cola_milano().translate((x, y, 0))
        m += box(x - DT_PAD / 2, y - 12, 0, DT_PAD, 12, Z_R)
    return m


def hembra(y):
    """Ensanche con hueco abierto por abajo, a partir de y hacia +Y."""
    pad = Manifold.batch_boolean([box(x - DT_PAD / 2, y, 0, DT_PAD, DT_LEN + 5, Z_R) for x in RAIL_X], OpType.Add)
    hueco = Manifold.batch_boolean([cola_milano(HOLGURA_DT, alto=Z_R + 0.2).translate((x, y, -0.01)) for x in RAIL_X], OpType.Add)
    return pad, hueco


# --- piezas ----------------------------------------------------------------
def tramo1():
    m = bandeja(TF, Y_SPLIT, 4, Y0) + patines(FL_D, Y_SPLIT)
    m += macho(Y_SPLIT)
    pad, hueco = hembra(FL_D)                       # recibe las lengüetas del frente
    return m + pad - hueco


def tramo2():
    m = bandeja(Y_SPLIT, L, 4, Y_SPLIT, trasera=True) + patines(Y_SPLIT, L)
    pad, hueco = hembra(Y_SPLIT)
    return m + pad - hueco


ESTILOS = {
    # nombre: (radio esquinas, chaflán aristas, abertura)
    "actual":   dict(radio=0.0, chaflan=0.0, abertura=("ovalo", 56, 24, 92)),
    "sombra":   dict(radio=2.0, chaflan=1.0, abertura=("ovalo", 56, 24, 92)),
    "pildora":  dict(radio=2.0, chaflan=1.0, abertura=("ovalo", 72, 14, 104)),
    "bolsillo": dict(radio=2.0, chaflan=1.0, abertura=("bolsillo", 64, 22, 100)),
    "onda":     dict(radio=2.0, chaflan=1.0, abertura=("onda", 84, 11, 0)),
    "circulo":  dict(radio=2.0, chaflan=1.0, abertura=("ovalo", 30, 30, 100)),
    # volta catalana: arco rebajado (flecha ~1/5 de la luz) sobre una base recta
    "volta":    dict(radio=2.0, chaflan=1.0, abertura=("volta", 66, 22, 92)),
    # revoltons: tres voltes entre "vigas", como el techo visto desde abajo
    "revoltons": dict(radio=2.0, chaflan=1.0, abertura=("revoltons", 24, 18, 94)),
}


def arco(luz, alto, z0, flecha_rel=0.2, r=2.0):
    """Perfil de volta: arranques rectos y arco rebajado de flecha = flecha_rel · luz."""
    f = flecha_rel * luz
    arr = alto - f
    R = (luz ** 2 / 4 + f ** 2) / (2 * f)
    cz = z0 + arr + f - R
    a0 = math.asin((luz / 2) / R)
    pts = [(-luz / 2, z0), (luz / 2, z0)]
    for i in range(41):
        a = a0 - 2 * a0 * i / 40
        pts.append((R * math.sin(a), cz + R * math.cos(a)))
    cs = CrossSection([pts])
    return cs.offset(-r, JoinType.Round, circular_segments=16).offset(r, JoinType.Round, circular_segments=16)


def frente(estilo="actual", nervios_hasta=None):
    e = ESTILOS[estilo]
    tipo, aw, ah, zc = e["abertura"]
    perfil = rrect(W, H, e["radio"]).translate((0, H / 2))
    if tipo == "onda":
        perfil -= CrossSection.circle(1, 96).scale((aw / 2 + 6, ah + 5)).translate((0, H + 5))
    f = vertical(perfil, TF, e["chaflan"])
    if tipo in ("ovalo", "bolsillo"):
        f -= corte(rrect(aw, ah, ah / 2).translate((0, zc)), TF, e["chaflan"])
    elif tipo == "volta":
        f -= corte(arco(aw, ah, zc - ah / 2), TF, e["chaflan"])
    elif tipo == "revoltons":
        viga = 5.0
        for k in (-1, 0, 1):
            f -= corte(arco(aw, ah, zc - ah / 2).translate((k * (aw + viga), 0)), TF, e["chaflan"])
    if tipo == "bolsillo":                          # cajita trasera: no se ve el interior
        caja = rrect(aw + 2.4, ah + 2.4, ah / 2 + 1.2).translate((0, zc)).extrude(RIB).rotate((90, 0, 0)).translate((0, TF + RIB, 0))
        hueco = rrect(aw, ah, ah / 2).translate((0, zc)).extrude(RIB - 1.2).rotate((90, 0, 0)).translate((0, TF + RIB - 1.2, 0))
        f = f + caja - hueco
    # pestaña inferior y nervios: transmiten el tirón a las lengüetas
    f += box(-W / 2 + 1.5, 0, 0, W - 3, FL_D, Z_R)
    top = nervios_hasta or (zc - ah / 2 - 6 if tipo in ("ovalo", "volta", "revoltons") else 76)
    for x in RAIL_X:
        f += box(x - 0.8, TF, Z_R, 1.6, RIB, top - Z_R)
        f += cola_milano().translate((x, FL_D, 0))
    return f


def gramos(m):
    return m.volume() / 1000 * PLA


def prueba_union():
    """Probeta de tolerancias: 3 parejas macho/hembra con juego 0,1 / 0,2 / 0,3 mm.
    Las muescas del costado indican cuál es cuál (1, 2 o 3)."""
    piezas = Manifold()
    for i, juego in enumerate((0.1, 0.2, 0.3)):
        x0 = i * 30.0
        m = box(-DT_PAD / 2, -12, 0, DT_PAD, 12, Z_R) + cola_milano()
        h = box(-DT_PAD / 2, 0, 0, DT_PAD, DT_LEN + 5, Z_R + 1.2) - cola_milano(juego, alto=Z_R + 0.2).translate((0, 0, -0.01))
        for k in range(i + 1):                     # muescas identificativas
            n = box(-DT_PAD / 2 - 0.5, -10 + k * 3, -0.5, 1.5, 1.2, Z_R + 2)
            m -= n
            h -= n.translate((0, 12, 0))
        piezas += m.translate((x0, 0, 0)) + h.translate((x0, 14, 0))   # separadas 6 mm
    return piezas
