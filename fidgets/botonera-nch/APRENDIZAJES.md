# Aprendizajes — botonera NocodeHackers

## Prueba v4 (2026-10-28): la tecla se rompe al primer clic
Causas probables (pendiente de confirmar dónde partió):
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
