# Aprendizajes — botonera NocodeHackers

## Prueba v4 (2026-10-28): la tecla se rompe al primer clic
**Confirmado: se rompieron los brazos en espiral.** Causas probables:
- Brazos del resorte de 1,2 × 1,2 mm impresos **como puente** (en el aire): capas mal
  pegadas → frágiles.
- Brazos cortos (3 × 95°, radio ~6 mm): mucha deformación para 1–1,5 mm de recorrido.
- Tecla alta sobre un vástago fino: palanca grande si se pulsa en el borde.
- PLA es rígido y frágil en flexión repetida.

## Reglas para siguientes versiones
- Un resorte impreso **no se imprime en puente**: va apoyado en la cama o en material sólido.
- El resorte debe doblarse **a lo largo de las líneas de capa**, nunca separándolas.
- Brazos largos y anchos (serpentín) en vez de cortos y finos.
- Resorte en **PETG** (más flexible y duradero); carcasa y tecla en PLA para un clic más sonoro.
- Se admite **montar piezas impresas** (encaje a presión): da libertad para orientar cada
  pieza de forma óptima. Nada de piezas no impresas.
- Siempre validar con **una pieza de prueba** antes de la botonera completa.

## Referencias
- Botón con flexura de 4 brazos impresa plana: https://makerworld.com/en/models/3325343
- Print-in-place fidget button: https://makerworld.com/en/models/498205
- Clicker satisfactorio: https://printables.com/model/370915-satisfying-clicking-fidget-button
- Orientación de capa y fatiga en PLA: https://pmc.ncbi.nlm.nih.gov/articles/PMC6926899/

## Decisión (2026-10-28)
Luis elige la opción de **piezas impresas que encajan** (v5). Primero se valida resorte + guía
de la tecla con un botón; el clic se añade después, cambiando una sola cosa cada vez.

## Por qué la v5 debería aguantar (cálculo aproximado)
Brazo modelado como viga guiada en ambos extremos: deformación máxima ε ≈ 3·t·δ / L²
(t = grosor que se dobla, δ = recorrido, L = largo del brazo).
| | t | δ | L | ε |
|---|---|---|---|---|
| v4 (rota) | 1,2 mm | 1,5 mm | ~10 mm | **~5 %** |
| v5 | 1,2 mm | 1,5 mm | ~33 mm | **~0,5 %** |
El PLA impreso rompe en torno al 2–4 %; para miles de pulsaciones conviene < 1 %.
Fuerza estimada v5: ~1 N (~100 g), del orden de una tecla de teclado (0,5–0,7 N).
Es una aproximación: la espiral también se retuerce, lo que la hace algo más blanda.

## Evaluación de resistencia (v5)
### Cálculo (`analisis_resorte.py`, vigas con flexión + torsión)
| Material | Fuerza botón | Deformación máx | Admisible orientativo* | Margen |
|---|---|---|---|---|
| PLA | 1,6 N (~160 g) | 0,67 % | 1 % | ×1,5 |
| PETG | 1,0 N (~100 g) | 0,67 % | 2 % | ×3 |
*No hay un valor publicado de deformación admisible en fatiga para flexuras impresas;
son supuestos prudentes. Hay que validarlos con ensayo.
Con brazos de 1,0 mm en PLA: ~0,9 N y 0,56 %.

### Ensayos caseros propuestos
1. **Fuerza–recorrido** con báscula de cocina: anotar gramos a 0,5 / 1 / 1,5 mm. Compara con el cálculo.
2. **Rotura estática**: pulsar más allá del recorrido (hasta que toque fondo) y comprobar que no cede.
3. **Fatiga**: 1.000 pulsaciones (a mano o con un servo) y repetir el ensayo 1. Si la fuerza
   cae > 10 % o aparecen marcas blancas en los brazos → el material se está cansando.
4. Repetir con 3 unidades (dispersión de impresión) y en PLA y PETG.

## Decisión material (2026-10-28)
Luis imprime **solo en PLA**. Se alargan las espirales a 300° (brazo 1,2 mm):
fuerza ~1,1 N, deformación 0,47 % → margen ×2,1 sobre el 1 % supuesto para PLA.

## Prueba v5 impresa (2026-10-28): ✅ funciona
Luis: funciona bien. Pide **más recorrido** y **más pequeño** (2×2 de 30 mm queda grande).
Compromiso tamaño / recorrido / tensión (PLA, calculado):
| Botón | Recorrido | Deformación | Fuerza |
|---|---|---|---|
| v5: 30 mm | 1,5 mm | 0,47 % (probado ✅) | 1,1 N |
| v6: 24 mm, 2 brazos de 510°, ancho 1,0 | 2,0 mm | 0,50 % | 0,5 N |
| 24 mm con 2,5 mm de recorrido | 2,5 mm | 0,63 % | 0,6 N (más riesgo) |
Regla: a igual tensión, menos tamaño ⇒ menos recorrido; se compensa con más vueltas y brazos más finos.

## Revisión de la tapa trasera (2026-10-29) — diseño actual NO válido
Luis pregunta si se probó el encaje. **No**: solo se comprobó que las piezas no se solapan.
Fallos del diseño actual (cordón perimetral de 0,3 mm):
- Ninguna pieza puede doblarse: pared de 2 mm y placa de 1,6 mm rígidas → o no entra o rompe.
- Holgura de 0,15 mm: por debajo de lo recomendado en FDM (0,2–0,4 mm).
Cómo se hace bien (snap-fit):
- El enganche lo da un **brazo en voladizo** que se dobla; deformación ε ≈ 1,5·h·y / L²
  (h grosor raíz, y interferencia, L largo). Brazo de 5–15 mm, **redondeo en la raíz**.
- El brazo se imprime **en el plano XY**, nunca vertical (en Z las capas se separan; admisible ÷2).
- PLA es frágil en flexión repetida: mantener ε bajo y pocas aperturas.
- **Antes de la pieza final, imprimir una probeta de tolerancias** (0,2 / 0,3 / 0,4 mm).
Fuentes: Fictiv (snap fits), Core77, guías Qidi/Sovol de holguras.
