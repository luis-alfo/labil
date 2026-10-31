# Soporte de estropajo del grifo: aprendizajes

## V1: qué falló (según Luis, 29 oct 2026)
- La pinza chocaba con el borde del fregadero y acabó rompiéndose.
- El brazo quedaba unos mm por encima de la encimera porque el aro apoyaba sobre el embellecedor cromado. Quedaba feo.
- Meter el estropajo en la pinza desde abajo era incómodo.

## V2: qué pide Luis
- Que el brazo vaya a ras de la encimera.
- Que en vez de la pinza haya una bandeja que cuelgue 5–8 cm por debajo, dentro del fregadero, para dejar el estropajo apoyado.

## V2: decisiones de diseño
- Son dos piezas y ninguna necesita soportes al imprimir.
  - A: aro en C escalonado (abraza el embellecedor por abajo y la columna por arriba) y brazo plano de 5 mm.
  - B: bandeja y pata. Encaja desde arriba en una ranura con avellanado de 45° y queda enrasada con el brazo. Si se levanta la bandeja, sale, así que se puede quitar para lavarla.
- La pata no toca el fregadero: queda a 6 mm del canto arriba y a 10 mm abajo. Un tope apoya en el canto de la encimera y evita que la bandeja gire.
- Las cotas del grifo son estimaciones sacadas de las fotos. Todavía no está probado en el grifo real.

## V3: lo que pide Luis (29 oct 2026)
- Que la bandeja se pueda levantar con una bisagra para que no estorbe al fregar.
- Que la bandeja sea una rejilla y el soporte no tenga que ser macizo. Hay que ahorrar material sin perder resistencia.
- El fregadero es redondo, así que la pared se acerca por los lados.

## V3: decisiones de diseño
- Son tres piezas y ninguna necesita soportes:
  - A: la misma pinza y brazo de la V2.
  - B: bastidor calado en forma de "A", que se imprime de pie.
  - C: bandeja de rejilla en diagonal, que se imprime plana.
- La bisagra es de bayoneta: ver la sección de PLA más abajo. La primera versión llevaba ojos cerrados y había que abrir los brazos de la "A" para encajar los pivotes, y se descartó.
- Bandeja levantada: gira libre hasta unos 97°, pasa de la vertical y se queda apoyada contra los brazos. Así ocupa 30 mm desde el canto en vez de 86, y su borde superior queda 7 mm por debajo de la encimera.
- Fregadero redondo:
  - Dentro del ancho de la bandeja, los brazos tienen que ir por detrás de ella cuando está levantada.
  - Por los lados la pared del fregadero se acerca. Por eso el eje de la bisagra está a 24 mm del canto y la bandeja mide 100 mm de ancho.
  - Con Ø 400 quedan 2,7 mm de holgura entre los ojos y la pared.
- Material: el bastidor y la bandeja suman unos 30 cm³, frente a los 46 cm³ de la bandeja maciza de la V2 (−34 %).
- Todavía no está probado en el grifo real. Hay que medir el Ø del fregadero y cuánto se mete la pared hacia dentro a 7 cm de profundidad.

## Luis imprime en PLA: cómo encaja cada pieza (29 oct 2026)
- El PLA aguanta poco cuando se dobla en la dirección que separa las capas. Antes de dar por buena una unión, hay que mirar hacia dónde se dobla respecto a las capas.
- Pinza en C: se dobla en el plano de las capas (la pieza se imprime plana) y deforma entre el 0,3 y el 0,5 %. Con PLA va bien.
- Espiga en el brazo: entra desde arriba sin doblar nada y queda enrasada.
- Bisagra: abrir la "A" para meter pivotes en ojos cerrados doblaría los brazos (impresos de pie) contra las capas. Con PLA eso es arriesgado.
- Solución, la bayoneta:
  - El ojo tiene una ranura abierta por arriba y el pivote entra desde arriba.
  - Cada pivote lleva una pestaña detrás del eje. Esa pestaña recorre un alojamiento del ojo cuyos extremos son el tope de abajo (0°) y el de arriba (95°).
  - Con la bandeja abajo, la pestaña empuja hacia arriba contra el tope y los pivotes quedan apretados hacia abajo, así que no pueden salirse.
  - La bandeja solo entra y sale con ella levantada del todo (85–95°), tirando hacia arriba. En el resto del recorrido queda atrapada.
- El PLA se ablanda hacia 55–60 °C: no conviene echarle agua muy caliente ni meterlo en el lavavajillas.

## Impresión en la Bambu Lab A1 de Luis y coste (29 oct 2026)
- Las tres piezas caben en una sola placa de 256 × 256 mm.
- El bastidor va en el centro, con la "A" alineada con el eje Y, que es por donde se mueve la cama. En una impresora de cama móvil, las piezas altas tienen que ir así.
- El bastidor lleva orejetas de 0,4 mm modeladas en la propia pieza, para no depender de que haya que activar el brim.
- Estimación con un perfil parecido al de A1 0.20mm Standard + PLA Basic: 48 g en total.
  - Por pieza: A 15 g, B 15 g, C 18 g.
  - Tiempo de la placa: unas 2 h 03 min, más unos 5–7 min de calibración inicial.
- Coste aproximado:
  - Filamento a unos 20 €/kg: alrededor de 1 €.
  - Luz: unos 0,2 kWh, es decir, 3–5 céntimos.
  - Total: 1,0–1,5 €, contando el desgaste de la máquina.
- Desde esta sesión no se puede descargar Bambu Studio porque GitHub está bloqueado. Por eso el 3MF solo lleva la geometría, y los ajustes de cada pieza hay que ponerlos a mano.
