"""Botón NocodeHackers v6: v5 compacta (24 mm) con más recorrido (2 mm).

Mismas 3 piezas que la v5. Para caber en menos espacio sin más tensión,
el resorte usa 2 brazos más finos que dan casi 1,5 vueltas.
Uso: python3 generar_v6.py -> boton_v6_*.stl y boton_v6_piezas.3mf
"""
import generar_v5 as v5

v5.LADO = 24.0
v5.TAM = 15.0
v5.RECORRIDO = 2.0
v5.N_BRAZOS = 2
v5.ANCHO_BRAZO = 1.0
v5.GROSOR_BRAZO = 1.2
v5.GIRO_BRAZO = 510
v5.R_BUJE = 3.5
# derivados
v5.HUECO = v5.LADO - 2 * v5.PARED
v5.R_LIBRE = v5.HUECO / 2 - 1.6
v5.Z_BUJE = v5.ALTO_MARCO
v5.Z_VALONA = v5.Z_BUJE + v5.RECORRIDO + 0.7
v5.Z_TAPA_INF = v5.Z_VALONA + v5.VALONA
v5.Z_TAPA_SUP = v5.Z_TAPA_INF + v5.TAPA

if __name__ == "__main__":
    import trimesh
    import analisis_resorte as a
    piezas = {"resorte": v5.resorte(), "carcasa": v5.boca_abajo(v5.carcasa()),
              "tecla": v5.boca_abajo(v5.tecla())}
    escena = trimesh.Scene()
    for i, (nombre, m) in enumerate(piezas.items()):
        t = v5.a_trimesh(m)
        assert m.status().name == "NoError" and t.is_watertight, nombre
        t.export(f"boton_v6_{nombre}.stl")
        t.apply_translation([(i - 1) * 32, 0, 0])
        escena.add_geometry(t, geom_name=nombre)
        print(f"{nombre}: {t.extents.round(1)} mm, {t.volume / 1000 * 1.24:.1f} g")
    escena.export("boton_v6_piezas.3mf")
    c, k = v5.carcasa(), v5.tecla()
    r = v5.resorte().rotate([180, 0, 0]).translate([0, 0, v5.ALTO_MARCO])
    print("choques:", round((c ^ k).volume(), 3), round((c ^ r).volume(), 3), round((k ^ r).volume(), 3),
          "| resorte en 1 pieza:", len(v5.resorte().decompose()) == 1)
    F, s = a.analizar(3500)
    print(f"PLA: fuerza {F:.2f} N, deformación {s / 3500 * 100:.2f} %")
