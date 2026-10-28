"""Prueba de un solo botón de la v3 (30 × 30 mm) para validar resorte y clic.

Usa exactamente la misma geometría que generar_v3.py, con una sola celda.
Uso: python3 prueba_v3.py  -> prueba_boton_v3.stl / .3mf
"""
import generar_v3 as v3

v3.BOTONES = [(v3.circulo, (0.0, 0.0))]
v3.LADO = v3.CELDA + v3.PARED

if __name__ == "__main__":
    m = v3.construir()
    t = v3.a_trimesh(m)
    assert m.status().name == "NoError" and t.is_watertight
    t.export("prueba_boton_v3.stl")
    t.export("prueba_boton_v3.3mf")
    vol = t.volume / 1000
    print(f"bbox mm: {t.extents.round(1)}  PLA macizo: {vol * 1.24:.1f} g")
