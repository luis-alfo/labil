# Trazo — barra modular de baño

Una línea plana de PLA que cuelga del grifo empotrado: pasa por encima del
caño (Ø 29) y la manilla (Ø 42), se engancha a cada uno con un lazo abierto
hacia abajo y se alarga un palmo a cada lado. Los ganchos ("jinetes") cabalgan
sobre su canto superior y se cambian de sitio a mano.

Sustituye a las propuestas A/B/C (`../bathroom-bar-{a,b,c}/`).

## Piezas

| Archivo | Qué es | Cómo se imprime |
| --- | --- | --- |
| `trazo_izquierda.stl`, `trazo_derecha.stl` | Las dos mitades de la línea, unidas en el centro por cola de milano | Planas, como se exportan. 253 × 57 × 8 mm: en diagonal en la A1 |
| `jinete_gancho.stl` | Gancho en J | De canto, como se exporta |
| `jinete_repisa.stl` | Repisa con borde (pasta de dientes de pie) | De canto, como se exporta |
| `jinete_horquilla.stl` | Horquilla de 8 mm (cepillo colgado por el cuello) | Placa abajo, como se exporta |
| `jinete_aro.stl` | Aro Ø 62 (secador) | Placa abajo, como se exporta |
| `test_clip_manilla.stl`, `test_clip_cano.stl`, `test_union.stl` | Pruebas de 10-20 min | Planas |

Ninguna necesita soportes. PLA, 0,20 mm, 5 perímetros, 30 % giroide, brim 6 mm
en las mitades.

## Orden

1. Imprime las tres pruebas y repasa la lista que imprime cada script.
2. Ajusta parámetros en `generate_stl.py` si hace falta y regenera.
3. Imprime las dos mitades, únelas sobre una mesa y encaja el conjunto
   empujando hacia abajo sobre los dos cilindros a la vez.

## Lo que está supuesto, no medido

- `HANDLE_OD = 42` tiene que ser el casquillo **fijo** junto a la pared, no
  el mando que bascula.
- `WALL_GAP = 3.5`: grosor del embellecedor cromado contra el que apoya la
  pieza.
- `DEPTH = 8`: fondo de la pieza; debe caber entre el embellecedor y el mando.
- `RING_ID = 62`: diámetro del aro para el secador.
- `ARM_LEN = 200`: el palmo a cada lado.

## Carga

Estimaciones del script (PLA, E ≈ 3000 MPa): 500 g colgados en la punta dan
unos 4 mm de flecha y tiran del lazo contrario con unos 12 N; cada lazo
aguanta unos 25 N antes de soltarse. Lo pesado, cerca del grifo.
