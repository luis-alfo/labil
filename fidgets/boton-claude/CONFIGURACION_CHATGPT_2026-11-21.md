# Configuración del botón ESP32-C3 por ChatGPT

Fecha: 21 de noviembre de 2026 (Europe/Madrid).

Este registro lo ha redactado ChatGPT/Codex para documentar su intervención en el Mac y en la placa de Luis. El diseño, el firmware y el programa del Mac ya existían en el repo y proceden del trabajo previo de Claude. No atribuyo su autoría a ChatGPT. Las adaptaciones posteriores del programa del Mac de F18 a Shift+B y del foco del cuadro de mensaje sí las he realizado yo, a petición de Luis.

## Resultado comprobado

- Firmware cargado en el ESP32-C3 y datos escritos verificados por Arduino.
- Pulsaciones físicas comprobadas en el monitor serie: aparece D al pulsar BOOT y U al soltarlo, repetidamente.
- Programa del Mac instalado y ejecutándose como servicio de usuario, con el puerto USB abierto.
- Permiso de teclado de Python comprobado desde el propio servicio: AX=True y enviar teclas=True.
- El diagnóstico inicial recibió pulsaciones cortas y largas y registró Enter y F18 DOWN/UP; después se sustituyó F18 por Shift+B, a petición de Luis.
- La versión de Shift+B está instalada y ejecutándose; coincide byte a byte con la versión probada y el proceso tiene abierto el puerto USB.
- Pasaron las pruebas de secuencia de teclas, pulsación corta/larga, desconexión, liberación e interrupción descritas más abajo.
- **Dictado confirmado por Luis:** «Sí, funciona al pulsar y soltar». Wispr Flow inicia y detiene el dictado con el botón usando Shift+B.
- Primer toque actualizado: cuando Claude está detrás, lo activa y enfoca el campo de mensaje Prompt. Instalado y comprobado mediante la API de Accesibilidad. Luis confirmó la prueba completa desde otra aplicación: «Sí, entra directamente».

## Qué he hecho como ChatGPT

1. Leí mediante Computer Use las instrucciones de la conversación «DISEÑO - ESP32C3» en Claude y contrasté los archivos con GitHub.
2. Usé Arduino IDE 2.3.11, que ya estaba instalado. Añadí la URL oficial de Espressif al gestor de placas:

   https://espressif.github.io/arduino-esp32/package_esp32_index.json

3. Instalé el paquete esp32 de Espressif Systems, versión 4.0.0.
4. Recuperé el firmware de main y guardé el sketch utilizado en el Mac en:

   ~/Documents/Arduino/boton_claude/boton_claude.ino

5. Seleccioné ESP32C3 Dev Module, puerto /dev/cu.usbmodem1101 y USB CDC On Boot: Enabled. Se mantuvieron los valores de 4 MB de flash, CPU a 160 MHz y Erase All Flash Before Sketch Upload: Disabled.
6. Compilé y subí el firmware. La compilación correcta mostró 297.261 bytes de programa y 14.572 bytes de variables globales. La carga terminó con «Hash of data verified» y «Hard resetting via RTS pin».
7. Abrí el monitor serie, observé varias parejas D/U procedentes del botón y dejé la velocidad en 115200. Cerré después el monitor para liberar el puerto al programa del Mac. No he comprobado visualmente el LED físico.
8. Con autorización expresa de Luis para usar ejecución local, descargué y revisé los tres archivos del programa Mac desde el commit 3efe98ae782949b528504efef7eea5304b3d9412: boton_claude.py, instalar.sh y es.lagu.boton-claude.plist. Comprobé la sintaxis Python y ejecuté el programa de prueba, que confirmó «escuchando /dev/cu.usbmodem1101».
9. Instalé los archivos en ~/Library/Application Support/Boton Claude/ y registré el servicio ~/Library/LaunchAgents/es.lagu.boton-claude.plist. En la instalación inicial conservé el código de boton_claude.py sin cambios; después lo adapté a Shift+B.
10. Registré el servicio con launchctl bootstrap en la sesión gráfica del usuario, en vez de ejecutar instalar.sh. El plist instalado mantiene RunAtLoad y KeepAlive, añade -u para registrar sin búfer y usa directamente el ejecutable de Python.app indicado más abajo. Fue necesario sustituir /usr/bin/python3 para que el servicio reconociera el permiso concedido en este Mac. Añadí temporalmente un lanzador de diagnóstico de permisos y gestos y lo retiré al terminar la comprobación. En esa fase el servicio volvió a ejecutar el programa original. La versión actual incluye el cambio a Shift+B descrito a continuación.
11. Comprobé que launchctl muestra el servicio es.lagu.boton-claude como running, que su proceso Python tiene abierto /dev/cu.usbmodem1101 y que /tmp/boton-claude.log contiene el mensaje de escucha.
12. Guardé este MD en GitHub mediante el navegador, porque Luis confirmó que no tiene una copia local del repo. No se ha creado una copia local de labil.

## Cambio solicitado: Shift+B para Wispr Flow

Luis indicó que Wispr Flow no aceptaba F18 y pidió usar Shift+B, el atajo que ya tenía configurado. No he comprobado que F18 sea incompatible en todos los casos; documento el problema comunicado por Luis.

- Modifiqué mac/boton_claude.py: al mantener BOOT más de 0,40 segundos se mantienen Shift y B. Al soltar BOOT se libera primero B y luego Shift. Los eventos de B incluyen la bandera Shift.
- El toque corto mantiene su función: traer Claude al frente o enviar Enter si ya está delante. El firmware continúa enviando D/U y no necesitó cambios.
- Añadí liberación de las teclas al desconectar la placa y al terminar el proceso con SIGTERM/SIGINT, e hice la liberación idempotente para evitar duplicados. El modo opcional de toque también libera las teclas mediante finally.
- Conservé una copia local de la versión anterior, instalé la nueva y reinicié el LaunchAgent. Verifiqué que está running, que Python tiene abierto /dev/cu.usbmodem1101 y que el archivo instalado coincide con el probado. El registro termina en «escuchando /dev/cu.usbmodem1101».
- Guardé el código mediante el navegador en [el commit 477fbe3](https://github.com/luis-alfo/labil/commit/477fbe3ac798985a56ba1dbec5a732bc6177acf4) y actualicé el README en [el commit 5d82016](https://github.com/luis-alfo/labil/commit/5d820167a77516bd85ac31923492d92df2897b73).

### Pruebas realizadas por ChatGPT

Usé eventos reales de Quartz interceptando su envío, sin inyectar teclas en aplicaciones durante las pruebas automatizadas. Comprobé los códigos nativos Shift=56 y B=11, el orden de pulsación/liberación y la bandera Shift=0x00020000. También probé con entradas serie simuladas el toque corto, la pulsación larga, entradas fragmentadas y duplicadas, desconexión mientras se mantiene pulsado, modo de toque, liberación repetida e interrupción durante la combinación. Las seis comprobaciones agrupadas terminaron correctamente.

Estas pruebas validan el programa. Después, Luis confirmó el dictado real con Shift+B: «Sí, funciona al pulsar y soltar». Esta confirmación procede de su prueba manual; Computer Use no accedió a Wispr Flow.

## Primer toque: activar Claude y enfocar el mensaje

Tras confirmar el dictado, Luis pidió que el primer toque dejara también activo el cuadro de texto de Claude. Añadí ese comportamiento al programa del Mac.

- Si Claude está detrás, el programa lo activa, localiza el campo editable llamado Prompt en su ventana activa y solicita el foco mediante Accesibilidad de macOS. Conserva el chat y el texto del borrador; no introduce texto ni envía Enter en ese primer toque.
- Si Claude ya está delante, el toque corto sigue enviando Enter. La pulsación larga mantiene Shift+B.
- La búsqueda está limitada en tiempo, profundidad y número de elementos. Comprueba que Claude continúa delante antes de enfocar y registra un aviso si no encuentra o no puede enfocar el campo.
- La prueba desde launchd, con el Python autorizado, obtuvo AXTrusted=True, Enfoque=True y AXFocused=True en el editor. El intento correcto con la versión final tardó aproximadamente 0,79 segundos. No se escribió texto de prueba ni se envió ningún mensaje.
- Volvieron a pasar las seis pruebas del protocolo/teclas y una séptima que verifica que activar Claude enfoca sin Enter, mientras que el toque con Claude delante conserva Enter.
- Instalé la versión probada, reinicié el servicio y confirmé que sigue running con el puerto USB abierto. El archivo instalado coincide byte a byte con el probado. Retiré el trabajo de launchd y los archivos temporales usados para la prueba.
- Publiqué el programa en [el commit e866fc5](https://github.com/luis-alfo/labil/commit/e866fc572bf7c4dfa7344f752380ad185db0c94d) y actualicé el README.

### Confirmación final de Luis

Luis probó el recorrido completo desde otra aplicación: toque corto para abrir Claude y pulsación larga para dictar directamente en el cuadro, sin hacer clic. Su respuesta fue: **«Sí, entra directamente»**.

Con esta prueba manual quedan confirmados el enfoque del mensaje y el dictado con Shift+B al pulsar y soltar. La configuración funcional del botón queda completada; las incidencias resueltas se conservan en este registro.

## ¿Fue todo sweet?

No del todo. La placa y el servicio quedaron funcionando, pero hubo complicaciones y fue necesario adaptar el atajo:

- La instalación de Espressif quedó en «Processing» tras cambios de ventana del IDE. Reinicié Arduino y completé la instalación; quedó confirmada por «Platform esp32:esp32@4.0.0 installed».
- Antes de instalar el paquete, el selector ofrecía «ESP32-C3 Dev Board». Tras instalarlo fue necesario elegir el nombre real del paquete: «ESP32C3 Dev Module».
- El ajuste USB CDC no se aplicó a la primera. La primera compilación falló porque Serial seguía siendo HardwareSerial y no tenía setTxTimeoutMs. Se corrigió activando USB CDC y verificando el valor en el menú. No fue necesario eliminar esa línea del firmware.
- Algunas interacciones de menú y teclado del IDE no se reflejaron inmediatamente; se restauró el contenido original del firmware antes de la compilación y carga definitivas. El primer guardado dejó una copia preliminar en ~/Documents/Arduino/sketch_nov21aboton_claude/; el sketch final utilizado es boton_claude.
- Computer Use bloqueó Terminal por seguridad y no autorizó Finder, Ajustes del Sistema ni Wispr Flow. Luis autorizó expresamente continuar la instalación del programa mediante ejecución local. Los permisos y el atajo de Wispr requieren intervención manual en las aplicaciones que Computer Use no permite controlar.
- El navegador disponible no tenía sesión de GitHub; Luis inició sesión personalmente para poder guardar este informe.
- Para comprobar el nuevo foco, ejecutar Python desde Codex no heredaba el permiso de Accesibilidad del servicio. Usé una prueba temporal desde launchd, alojada en Application Support porque macOS no permitía a ese proceso leer el script en Documents. El acceso al campo funcionó al dirigirse al proceso de Claude y su ventana activa. La prueba temporal quedó retirada.

## Diagnóstico inicial de permisos (antes del cambio a Shift+B)

El intento de registrar F18 en Wispr Flow no recibía ninguna tecla. El firmware no tenía que enviar F18: transmite D/U y el programa del Mac los convierte en pulsación corta o larga. El diagnóstico confirmó la recepción de pulsaciones cortas y registró Enter DOWN/UP y F18 DOWN/UP.

Luis confirmó que había activado Python en Accesibilidad. Sin embargo, al iniciar el servicio mediante /usr/bin/python3 seguían apareciendo AX=False y enviar teclas=False. Cambié el ejecutable del LaunchAgent por el de Python.app que realmente estaba ejecutando el proceso:

/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python

Después de ese cambio, el propio servicio confirmó AX=True y enviar teclas=True. Esa fue la solución observada en esta sesión. No se alteró la base de datos de permisos de macOS; Luis concedió el permiso desde Ajustes.

Retiré el lanzador temporal de diagnóstico y reinicié el servicio definitivo con el programa original. Verifiqué que estaba running, que tenía abierto el puerto USB, que RunAtLoad y KeepAlive estaban activos y que los bytes de boton_claude.py coincidían con el archivo descargado del repo. El último mensaje del registro fue «escuchando /dev/cu.usbmodem1101».

Después de esa comprobación, Luis pidió sustituir F18 por Shift+B. El estado actual y las pruebas de esa adaptación figuran arriba; esta sección conserva el diagnóstico histórico del permiso.

## Ubicaciones y mantenimiento

- Programa instalado: ~/Library/Application Support/Boton Claude/boton_claude.py
- Servicio: ~/Library/LaunchAgents/es.lagu.boton-claude.plist
- Registro: /tmp/boton-claude.log
- Parámetros del programa conservados: APP_CLAUDE = com.anthropic.claudefordesktop; LARGA_S = 0.40; DICTADO = mantener.
- Para comprobar el servicio: launchctl print gui/$(id -u)/es.lagu.boton-claude
- Para detener y desregistrar el servicio: launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/es.lagu.boton-claude.plist
- El número del puerto USB puede cambiar al reconectar; el programa busca automáticamente /dev/cu.usbmodem*.
- Si se vuelve a ejecutar instalar.sh del repo, se generará el plist original con /usr/bin/python3. En este Mac debe conservarse la ruta directa de Python.app cuya autorización se ha comprobado.

La carcasa impresa, el ajuste mecánico de la palanca y las medidas de la galga no forman parte de las comprobaciones realizadas en esta sesión.
