"""Proyectos de Bambu Studio para la A1 de la v3 «primera capa»: un llavero y la placa de 16.

Filamentos: 1 negro (cuerpo), 2 blanco (ST), 3 naranja (26). Para todo blanco, se pone una
bobina blanca en el 3. Ajustes (ver ../APRENDIZAJES.md):
- relleno 70 % rectilíneo y un modificador al 100 % en cuello y tapón;
- brim de 4 mm solo por fuera, hecho en negro (orden de la primera capa 1 → 2 → 3);
- pata de elefante a 0 (las letras de detrás van a ras en la primera capa);
- placa PEI texturizada.

Uso: python3 make_a1.py   (lee los STL que escribe rehacer.py)
"""
import io
import sys
from pathlib import Path

import matplotlib
import numpy as np
import trimesh

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from make_3mf import build_3mf, project_settings  # noqa: E402

ESTADO = "primera-capa"
D = Path(__file__).parent.parent / ESTADO
COLORES = ["#161616", "#FFFFFF", "#FF6A13"]
PARTES = [("cuerpo negro", "negro", 1), ("ST blanco", "blanco", 2), ("26 naranja", "naranja", 3)]
# purga (mm³) de un filamento (fila) al siguiente (columna): de oscuro a claro hace falta más
FLUSH = [[0, 560, 480],
         [180, 0, 220],
         [200, 420, 0]]


def ajustes(torre=None):
    over = {
        "sparse_infill_density": "70%",
        "sparse_infill_pattern": "zig-zag",
        "brim_type": "outer_only",
        "brim_width": "4",
        "elefant_foot_compensation": "0",
        "curr_bed_type": "Textured PEI Plate",
        "enable_prime_tower": "1",
        "flush_volumes_matrix": [str(v) for fila in FLUSH for v in fila],
        "flush_volumes_vector": ["140"] * (2 * len(COLORES)),
        "flush_multiplier": "1",
    }
    if torre:
        over["wipe_tower_x"], over["wipe_tower_y"] = [str(torre[0])], [str(torre[1])]
    return project_settings("Bambu Lab A1 0.4 nozzle", "0.20mm Standard @BBL A1",
                            "Bambu PLA Basic @BBL A1", COLORES, over)


def miniatura(mallas, centros):
    fig = plt.figure(figsize=(5.12, 5.12), dpi=100, facecolor="#e9ebe9")
    ax = fig.add_axes([0, 0, 1, 1])
    lo = np.min([m.bounds[0] for m, _ in mallas], axis=0)
    hi = np.max([m.bounds[1] for m, _ in mallas], axis=0)
    c = (lo + hi) / 2
    for cx, cy in centros:
        tris, fcs, zs = [], [], []
        for m, col in mallas:
            keep = m.face_normals[:, 2] > 0.2
            t = m.triangles[keep]
            tris += list(t[:, :, :2] - c[:2] + [cx, cy])
            fcs += [col] * len(t)
            zs += list(t[:, :, 2].mean(1))
        o = np.argsort(zs)
        ax.add_collection(PolyCollection([tris[i] for i in o], facecolors=[fcs[i] for i in o], edgecolors="none"))
    if len(centros) > 1:
        ax.set_xlim(0, 256), ax.set_ylim(0, 256)
    else:
        ax.set_xlim(centros[0][0] - 45, centros[0][0] + 45), ax.set_ylim(centros[0][1] - 45, centros[0][1] + 45)
    ax.set_aspect("equal"), ax.set_axis_off()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    return buf.getvalue()


def modificador(cuerpo):
    """Caja que cubre cuello y tapón: desde donde la botella se estrecha hasta arriba."""
    lo, hi = cuerpo.bounds
    ys = np.linspace(lo[1] + 1, hi[1] - 1, 300)
    anchos = []
    for y in ys:
        s = cuerpo.section(plane_origin=[0, y, 1.0], plane_normal=[0, 1, 0])
        anchos.append(np.ptp(s.vertices[:, 0]) if s is not None else 0)
    anchos = np.array(anchos)
    hombro = ys[np.where(anchos > 0.8 * anchos.max())[0].max()]
    caja = trimesh.creation.box(extents=[hi[0] - lo[0] + 2, hi[1] - hombro + 1, hi[2] - lo[2] + 2])
    caja.apply_translation([(lo[0] + hi[0]) / 2, (hombro + hi[1] + 1) / 2, (lo[2] + hi[2]) / 2])
    return caja, hombro


def main():
    mallas = {c: trimesh.load(D / f"st26-{ESTADO}_{c}.stl") for _, c, _ in PARTES}
    caja, hombro = modificador(mallas["negro"])
    partes = [(n, mallas[c], e) for n, c, e in PARTES]
    partes.append(("cuello y tapón 100 %", caja, None, {"sparse_infill_density": "100%"}))
    vista = [(mallas[c], COLORES[e - 1] if c != "negro" else "#2a2a2a") for _, c, e in PARTES]
    meta = {"first_layer_print_sequence": "1 2 3"}

    uno = (128.0, 128.0)
    build_3mf(D / f"st26-{ESTADO}_A1.3mf", "ST26 botella v3", partes, ajustes(), uno,
              miniatura(vista, [uno]), plate_meta=meta)

    # placa de 16: 2 filas × 8, con 28,5 mm entre columnas (20,2 mm de botella + brim + aire)
    centros = [(128 + (i - 3.5) * 28.5, y) for y in (52.0, 140.0) for i in range(8)]
    build_3mf(D / f"st26-{ESTADO}_A1_placa16.3mf", "ST26 botella v3 x16", partes, ajustes(torre=(170, 200)),
              centros, miniatura(vista, centros), plate_meta=meta)
    print(f"modificador desde y = {hombro:.1f} mm (botella de {mallas['negro'].bounds[1][1]:.1f} mm)")


if __name__ == "__main__":
    main()
