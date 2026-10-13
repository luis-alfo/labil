import os
import math, sys, numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from manifold3d import CrossSection, Manifold, JoinType, OpType
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import render

PLA = 1.24
W, H, L = 129.0, 134.0, 348.0          # exterior cajón (hueco 130x135x350)
TF, RIB = 2.0, 6.0                       # frente y nervios traseros
RIM_T, RIM_H = 1.2, 20.0                 # reborde lateral
G, NX, NY = 42.0, 3, 8                   # rejilla Gridfinity
BP_H = 4.65                              # alto del perfil de la base
Y0 = TF + RIB                            # inicio de la base
Y_SPLIT = Y0 + 4 * G                     # unión entre tramos

def rrect(w, h, r, seg=24):
    r = min(r, w / 2 - 0.01, h / 2 - 0.01)
    return CrossSection.square((w - 2 * r, h - 2 * r), center=True).offset(r, JoinType.Round, circular_segments=seg)

def box(x, y, z, sx, sy, sz):
    return Manifold.cube((sx, sy, sz)).translate((x, y, z))

def celda():
    # perfil de la base Gridfinity: 0,7 a 45°, 1,8 recto, 2,15 a 45° (abierta por abajo)
    a = rrect(36.3, 36.3, 0.8).extrude(0.7 + 0.01, scale_top=(37.7 / 36.3, 37.7 / 36.3))
    b = rrect(37.7, 37.7, 1.5).extrude(1.8 + 0.02).translate((0, 0, 0.7 - 0.01))
    c = rrect(37.7, 37.7, 1.5).extrude(2.15 + 0.01, scale_top=(41.6 / 37.7, 41.6 / 37.7)).translate((0, 0, 2.5))
    return (a + b + c).translate((0, 0, -0.005))

def base(y_ini, n_filas):
    slab = box(-NX * G / 2, y_ini, 0, NX * G, n_filas * G, BP_H)
    cuts = []
    c = celda()
    for ix in range(NX):
        for iy in range(n_filas):
            cuts.append(c.translate((-G + ix * G, y_ini + G / 2 + iy * G, -0.001)))
    return slab - Manifold.batch_boolean(cuts, OpType.Add)

def cuerpo():
    m = base(Y0, NY)
    xi = NX * G / 2                                         # 63.0
    for s in (-1, 1):                                       # rebordes laterales
        x = xi if s > 0 else -W / 2
        m += box(x, TF, 0, W / 2 - xi, L - TF, RIM_H)
    m += box(-W / 2, Y0 + NY * G, 0, W, L - (Y0 + NY * G), RIM_H)   # trasera / tope
    return m

def frente(tipo):
    f = box(-W / 2, 0, 0, W, TF, H)
    rib_top = H - 20
    if tipo == "muesca":
        f -= Manifold.cylinder(TF + 2, 16, circular_segments=48).rotate((-90, 0, 0)).translate((0, -1, H))
    elif tipo == "gola":
        z0, fondo = 108.0, 18.0
        f = box(-W / 2, 0, 0, W, TF, z0)                                     # frente bajo
        f += box(-W / 2, fondo, z0 - 2, W, TF, H - z0 + 2)                   # panel retranqueado
        for x in (-W / 2, W / 2 - 1.6):
            f += box(x, 0, z0 - 2, 1.6, fondo + TF, H - z0 + 2)              # mejillas
        rib_top = z0
    elif tipo == "agujero":
        hole = rrect(56, 24, 12).extrude(TF + 2).rotate((90, 0, 0)).translate((0, TF + 1, 92))
        f -= hole
        rib_top = 76
    elif tipo == "ranura":
        hole = rrect(104, 16, 8).extrude(TF + 2).rotate((90, 0, 0)).translate((0, TF + 1, 114))
        f -= hole
        rib_top = 102
    elif tipo == "calado":
        r, web = 6.5, 2.4
        dx, dz = r * math.sqrt(3) + web, 1.5 * r + web * math.sqrt(3) / 2
        hexs, z, row = [], 22.0, 0
        while z < H - 18:
            x = -W / 2 + 14 + (dx / 2 if row % 2 else 0)
            while x < W / 2 - 14:
                hexs.append(CrossSection.circle(r, 6).rotate(30).translate((x, z)))
                x += dx
            z += dz; row += 1
        f -= CrossSection.batch_boolean(hexs, OpType.Add).extrude(TF + 2).rotate((90, 0, 0)).translate((0, TF + 1, 0))
        rib_top = 0
    if rib_top > 0:
        for x in (-38, 38):
            f += box(x - 0.8, TF, 0, 1.6, RIB, rib_top)
    return f

def cubo(nx, ny, u, x, y):
    w, d, h = nx * G - 0.5, ny * G - 0.5, 7 * u
    pie = rrect(w - 5.7, d - 5.7, 0.8).extrude(4.4, scale_top=((w - 0.6) / (w - 5.7), (d - 0.6) / (d - 5.7)))
    caja = rrect(w, d, 3.75).extrude(h - 4.4).translate((0, 0, 4.4))
    hueco = rrect(w - 2.4, d - 2.4, 2.6).extrude(h).translate((0, 0, 6))
    return (pie + caja - hueco).translate((x, y, 0.3))

def tm(m):
    me = m.to_mesh()
    return trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)

def g(m):
    return m.volume() / 1000 * PLA

if __name__ == "__main__":
    CREMA = np.array([0.95, 0.91, 0.82])
    COLS = [np.array(c) for c in ([0.62, 0.72, 0.62], [0.84, 0.56, 0.44], [0.58, 0.66, 0.78], [0.86, 0.78, 0.50])]
    body = cuerpo()
    fr = frente("gola")
    # cubos de ejemplo
    gx = lambda ix, n: -G * 1.5 + G * n / 2 + ix * G
    gy = lambda iy, n: Y0 + G * n / 2 + iy * G
    cubos = [cubo(1, 1, 6, gx(0, 1), gy(0, 1)), cubo(2, 1, 9, gx(1, 2), gy(0, 1)),
             cubo(3, 2, 4, gx(0, 3), gy(1, 2)), cubo(1, 2, 12, gx(0, 1), gy(3, 2)),
             cubo(2, 2, 6, gx(1, 2), gy(3, 2)), cubo(3, 1, 3, gx(0, 3), gy(5, 1))]

    t1 = body ^ box(-W, -1, -1, 2 * W, Y_SPLIT + 1, 200)
    t2 = body ^ box(-W, Y_SPLIT, -1, 2 * W, L, 200)
    print(f"tramo1 sin frente {g(t1):.0f} g, tramo2 {g(t2):.0f} g, frente gola {g(fr):.0f} g, total {g(body+fr):.0f} g")
    print("Tramo 1 largo:", Y_SPLIT, "Tramo 2:", L - Y_SPLIT)

    fig = plt.figure(figsize=(16, 7.2))
    ax = fig.add_subplot(1, 2, 1)
    parts = [(tm(body + fr), CREMA)] + [(tm(c), COLS[i % 4]) for i, c in enumerate(cubos)]
    ax.imshow(render(parts, az=-35, el=33, size=(760, 640))); ax.set_axis_off()
    ax.set_title(f"Montado, con cubos Gridfinity de ejemplo\ncajón ≈ {g(body + fr):.0f} g de PLA (sin cubos)", fontsize=12)

    ax = fig.add_subplot(1, 2, 2)
    sep = 70
    parts = [(tm(t1 + fr), CREMA), (tm(t2.translate((0, sep, 0))), np.array([0.90, 0.86, 0.76]))]
    for i, c in enumerate(cubos[:3]):
        parts.append((tm(c.translate((0, 0, 150))), COLS[i % 4]))
    ax.imshow(render(parts, az=-35, el=33, size=(760, 640))); ax.set_axis_off()
    ax.set_title(f"Despiece: tramo 1 con frente ({Y_SPLIT:.0f} mm) + tramo 2 ({L - Y_SPLIT:.0f} mm)\n"
                 f"cada tramo cabe en la Bambu A1 (256 mm); base de celdas abiertas", fontsize=12)
    fig.suptitle("Cajón Gridfinity para hueco de 130 × 135 × 350 mm — 3 × 8 unidades, frente tipo gola", fontsize=14, y=0.98)
    plt.tight_layout(rect=(0, 0, 1, 0.93))
    plt.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "concepto_gridfinity.png"), dpi=100)
