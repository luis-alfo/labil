# Soporte de estropajo V4: revisión completa y decisiones

## Requisitos acordados con Luis (29 oct–1 nov 2026)
- Estética: el brazo va a ras de la encimera y no debe quedar nada levantado ni torcido a la vista.
- Fregadero redondo (Ø ~400). Nada puede chocar con su borde: la V1 se rompió así.
- Una bandeja, no una pinza, unos 7 cm por debajo de la encimera, para dejar el estropajo apoyado.
- Que se pueda levantar para fregar y se quede arriba sola.
- Bandeja de rejilla y soporte calado: ahorrar material sin perder resistencia.
- PLA (Luis no tiene PETG). Nada de montajes que obliguen a doblar el PLA.
- Bambu Lab A1: una sola placa, sin soportes y con un 3MF listo para abrir.
- Que se pueda ver en el móvil (visor en GitHub Pages).

## Revisión de la V3.1 con números
Cargas usadas en todos los cálculos:
- L1: estropajo mojado, 1 N en el centro de la bandeja.
- L2: 20 N en el borde de la bandeja (alguien aprieta o apoya algo).

| Punto débil | Con L1 | Con L2 |
|---|---|---|
| Tracción en el brazo | 6 N | 208 N |
| Punta del brazo (ranura abierta) | 3 MPa | 99 MPa: rompe |
| Brazos del bastidor, entre capas | 0,5 MPa | 18 MPa: al límite |
| Pestaña de la bayoneta | 0,3 MPa | 14 MPa: al límite |

- Causa de fondo: todo el par de la bandeja se resistía con un tope en el canto de la encimera, con solo ~8 mm de palanca. Eso multiplicaba las fuerzas por 10.
- Con esa tracción, la pinza en C también puede soltarse del grifo.
- Montar la pinza en C pedía abrirla 8,4 mm. Eso deforma el PLA alrededor del 0,9 %, el doble de lo aconsejable.
- El tope en el canto dependía de medir la distancia al canto con ±0,5 mm. Cada 0,5 mm de error inclinaba la bandeja 3,6°.
- Lección: antes de mirar formas, hay que ver por dónde viaja la carga y con qué palanca se resiste. Y siempre simular el montaje completo.

## Decisiones de la V4
1. El par se resiste abajo, contra la pared del fregadero.
   - El colgador (B) cuelga de la punta del brazo como un péndulo y apoya un tope contra la pared, unos 7,7 cm más abajo.
   - La palanca pasa de 8 a 77 mm, y todas las fuerzas bajan unas 10 veces: con L2 la tracción es 21 N en vez de 208.
   - Como el péndulo busca su sitio solo, un error de medida solo lo inclina un poco: 2 mm de error son 1,5°.
2. El colgador es un perfil plano de 10 mm y se imprime tumbado.
   - Todo trabaja en el plano de las capas, sin voladizos y sin soportes.
   - Es un triángulo: pata, mentón y tirante.
3. La abrazadera es una U abierta por detrás, cerrada con una llave que se mete desde arriba.
   - El PLA no tiene que doblarse para montarla.
   - No se suelta aunque tiren de ella.
4. La bisagra es central, con un gancho abierto por arriba en el colgador y una varilla entre las dos orejas de la bandeja.
   - Abajo, un talón de la bandeja apoya contra el mentón (~10 mm de palanca). Además, el gancho la deja atrapada: no se puede levantar.
   - Solo entra y sale con la bandeja vertical.
   - Levantada, gira hasta ~97° y se apoya en la pata.
5. La bandeja es de rejilla en diagonal, con marco de 8 mm y un nervio central donde apoya al levantarse.

## Resultados verificados (simulación con las mallas reales)
- Las cuatro piezas son sólidos cerrados. Ninguna tiene voladizos de más de 45°, salvo el puente de 11 mm bajo la varilla.
- Montaje:
  - A desliza hacia la pared sin tocar el grifo.
  - K baja desde arriba.
  - B entra inclinado ~12° con el diente en la ranura y gira hasta la vertical sin tocar el brazo, la encimera ni la pared.
  - C entra vertical desde arriba y no se puede sacar ni abajo ni a 30°.
- Recorrido de la bandeja: libre de 0° a ~97°. Levantada queda 5 mm por debajo de la encimera y ocupa 36 mm desde el canto. Bajada llega a 84 mm.
- Con L2 todo trabaja en el plano de capa y nada pasa de 11 MPa, con un admisible de ~20:
  - labio del gancho: 10,7 MPa;
  - llave: 5,9 MPa;
  - varilla: 5,6 MPa.
- Material (perfil parecido al de A1 + PLA Basic):

| Pieza | Filamento | Tiempo |
|---|---|---|
| A brazo | 16,8 g | 23 min |
| K llave | 1,7 g | 3 min |
| B colgador | 8,6 g | 16 min |
| C bandeja | 17,8 g | 46 min |
| **Total** | **~45 g** | **~1 h 28 min** |

  La V3 eran ~50 g y ~2 h.

## Montaje
1. A: con la U abierta hacia la pared, desliza el brazo hacia el grifo hasta que abrace la columna.
2. K: mete la llave desde arriba por detrás de la columna, en las ranuras de la U.
3. B: inclina el colgador con la parte de abajo hacia ti (~12°), mete el diente en la ranura de la punta del brazo y deja que gire hasta quedar vertical. El tope de abajo apoya en la pared del fregadero.
4. C: con la bandeja vertical, baja la varilla por el gancho y bájala hasta horizontal.

## Medidas que hay que confirmar antes de imprimir
- Ø de la columna, Ø y altura del embellecedor, y distancia del eje del grifo al canto. Igual que antes.
- `sink_wall_x`: a ~8 cm de profundidad, cuánto entra o sale la pared del fregadero respecto al canto de la encimera. Es la medida nueva y la que más importa.
- Que detrás del grifo quede sitio para meter la llave: unos 15 mm.

## Crítica de la V4 frente a los principios de Luis (16 nov 2026)
Luis pidió repensar el modelo y criticarlo según sus principios: resistencia, ahorro de material, montaje y estética, además de que sirva para dejar el estropajo. Comprobado sobre las mallas de la V4; nada está impreso todavía.

### Función
- El estropajo no cabe tumbado. El interior del marco mide 95 × 58 mm y la bisagra central ocupa una franja de 23 mm de ancho hasta 11 mm dentro de la bandeja: en el centro quedan 47 mm de fondo.
- Nunca se preguntó el tamaño del estropajo. La bandeja se fue encogiendo (V2: 100 × 75 interior) para librar el fregadero redondo sin volver a comprobarlo.

### Resistencia
- El cálculo solo cubre la carga hacia delante. Ahí la V4 va sobrada (11 MPa con 20 N).
- De lado es inestable: el colgador apoya en 10 mm de ancho. Con un estropajo de 100 g descentrado 20 mm se ladea ~9° (8 mm de caída en la esquina), hasta que el diente hace tope en la ranura.
- Nada está bloqueado:
  - bastan ~0,1 N para separar el colgador de la pared, porque es un péndulo;
  - el movimiento de montaje (inclinar 12° y levantar 4 mm) es el mismo que lo desengancha;
  - la abrazadera no aprieta, así que el conjunto gira alrededor del grifo: 5° son 10 mm de desplazamiento lateral de la bandeja.
- Todo el reparto de fuerzas depende de dónde está la pared del fregadero a 8 cm de profundidad, que no está medida.
- Los números son fórmulas de mano con palancas supuestas y un admisible supuesto. No son ensayos.

### Material
- De los 18,4 cm³ del brazo, 13,1 son la abrazadera, y 9,3 son un anillo de 7 mm de grosor por encima del embellecedor que no hace falta.
- La rejilla tiene 3 mm de grosor: 9,6 de los 16,4 cm³ de la bandeja.
- El mayor gasto no está en las piezas: son cuatro versiones diseñadas sobre medidas supuestas. Una pieza de prueba de 3 g habría ahorrado más que cualquier calado.

### Montaje
- Cumple lo de no doblar el PLA.
- La llave es una pieza suelta de 2 g que se cae al fregadero, y necesita ~15 mm libres detrás del grifo, sin comprobar.
- La varilla de la bisagra se imprime como puente redondo de 11 mm: la cara de abajo saldrá deformada y la holgura con el gancho es de 0,25 mm.

### Estética
- El brazo a ras se cumple, pero mide 5 mm de alto y 22 de ancho.
- La abrazadera es un bloque en U de 18 mm de alto con dos colas cuadradas detrás del grifo.
- En la punta del brazo, el sitio más visible, hay una ranura con el remate del colgador embutido y juntas de 0,3 mm.
- El colgador parece una escuadra, y la bisagra es un bulto de 17 mm en medio de la bandeja.
- Con el estropajo descentrado la bandeja queda ladeada, que es el defecto estético que más se nota.

### Proceso (causa de fondo)
- La guía del repo (CLAUDE.md) pide preguntar medidas y material antes de modelar, e imprimir piezas de prueba de cada encaje. No se hizo ninguna de las dos cosas.
- Cada versión arregló el fallo de la anterior añadiendo piezas: de una pieza (V1) a cuatro (V4).
- "Verificado" significó que las mallas ideales no se solapan en posiciones sueltas, sin tolerancias de impresión.

### Qué cambiar en la siguiente versión
1. Medir antes de dibujar: grifo, canto, pared del fregadero y estropajo. Después, imprimir una prueba de la abrazadera y otra del colgador.
2. Bandeja a la medida del estropajo, con la bisagra en los laterales o por debajo del fondo.
3. Colgador con apoyo ancho arriba y dos topes separados en la pared, y enganche con bloqueo.
4. Abrazadera baja, solo alrededor del embellecedor, con una llave en cuña que apriete. Brazo de 3 mm.
5. Rejilla de 2 mm.

## Datos de Luis para la V5 (16 nov 2026)
- Decisión: el soporte sí puede apoyarse en la pared interior del fregadero.
- El estropajo es de tipo salvauñas: espuma amarilla con ranuras de agarre a los lados y fibra verde en una cara. Faltan sus medidas.
- Luis preguntó cómo se seca mejor. Recomendación (pendiente de que la confirme): de canto, apoyado en el lado largo, con la fibra en vertical y sobre dos o tres nervios finos en vez de un fondo plano.
  - Así las dos caras grandes quedan al aire y el agua baja por gravedad y gotea.
  - Tumbado sobre la fibra, la cara de abajo queda siempre mojada.
- Consecuencia para el diseño: la bandeja pasa a ser una cuna estrecha (el grosor del estropajo más holgura) y entra menos en el fregadero.
- Siguen pendientes las medidas 1 a 8 del grifo, el canto, la pared del fregadero y el estropajo.
