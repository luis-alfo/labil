"""Prueba de un solo botón de la v4 (mecanismo oculto), 30 × 30 mm.

Uso: python3 prueba_v4.py  -> prueba_boton_v4.stl / .3mf
"""
import generar_v4 as v4
import generar_v3 as v3

v3.BOTONES = [(v3.circulo, (0.0, 0.0))]
v3.LADO = v3.CELDA + v3.PARED

if __name__ == "__main__":
    m = v4.construir()
    t = v3.a_trimesh(m)
    assert m.status().name == "NoError" and t.is_watertight
    t.export("prueba_boton_v4.stl")
    t.export("prueba_boton_v4.3mf")
    print(f"bbox mm: {t.extents.round(1)}  PLA macizo: {t.volume / 1000 * 1.24:.1f} g")
