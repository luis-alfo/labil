#!/usr/bin/env python3
"""Botón Claude — programa del Mac. Escucha la placa por el puerto serie y decide.

  toque corto        Claude no está delante -> trae Claude al frente y enfoca el mensaje
                     Claude está delante    -> Enter (aceptar)
  mantener pulsado   Shift+B mientras dure (Wispr Flow, modo «mantener para hablar»)

Solo usa lo que trae macOS (sin instalar librerías). La primera vez, macOS pide permiso de
Accesibilidad para quien lo ejecuta (Terminal o python3): sin él no puede enviar teclas.

Uso:  python3 boton_claude.py            (Ctrl+C para parar)
      BOTON_PUERTO=/dev/cu.usbmodem101 python3 boton_claude.py
"""
import ctypes
import ctypes.util
import glob
import os
import select
import signal
import subprocess
import termios
import time

APP_CLAUDE = "com.anthropic.claudefordesktop"   # comprobar con: osascript -e 'id of app "Claude"'
LARGA_S = 0.40             # a partir de aquí, la pulsación es «larga»
DICTADO = "mantener"       # "mantener": Shift+B mientras se pulsa · "toque": un toque al llegar a larga
TECLA_ENTER, TECLA_SHIFT, TECLA_B = 36, 56, 11
FLAG_SHIFT = 0x00020000    # kCGEventFlagMaskShift
dictado_pulsado = False

_cg = ctypes.CDLL(ctypes.util.find_library("ApplicationServices"))
_cg.CGEventCreateKeyboardEvent.restype = ctypes.c_void_p
_cg.CGEventCreateKeyboardEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint16, ctypes.c_bool]
_cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
_cg.CGEventSetFlags.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
_cg.CFRelease.argtypes = [ctypes.c_void_p]

# Accesibilidad de macOS: enfocar el editor sin escribir ni cambiar de conversación.
_cg.AXUIElementCreateApplication.argtypes = [ctypes.c_int]
_cg.AXUIElementCreateApplication.restype = ctypes.c_void_p
_cg.AXUIElementCopyAttributeValue.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
_cg.AXUIElementSetAttributeValue.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
_cg.AXUIElementSetMessagingTimeout.argtypes = [ctypes.c_void_p, ctypes.c_float]
_cg.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
_cg.CFStringCreateWithCString.restype = ctypes.c_void_p
_cg.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long, ctypes.c_uint32]
_cg.CFStringGetCString.restype = ctypes.c_bool
_cg.CFGetTypeID.argtypes = [ctypes.c_void_p]
_cg.CFGetTypeID.restype = ctypes.c_ulong
_cg.CFStringGetTypeID.restype = ctypes.c_ulong
_cg.CFArrayGetTypeID.restype = ctypes.c_ulong
_cg.CFArrayGetCount.argtypes = [ctypes.c_void_p]
_cg.CFArrayGetCount.restype = ctypes.c_long
_cg.CFArrayGetValueAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_long]
_cg.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
_cg.CFBooleanGetValue.argtypes = [ctypes.c_void_p]
_cg.CFBooleanGetValue.restype = ctypes.c_bool
_cg.CFBooleanGetTypeID.restype = ctypes.c_ulong
_cg.CFRetain.argtypes = [ctypes.c_void_p]
_cg.CFRetain.restype = ctypes.c_void_p
_AX = {nombre: _cg.CFStringCreateWithCString(None, nombre.encode(), 0x08000100)
       for nombre in ("AXFocusedWindow", "AXRole", "AXTitle",
                      "AXDescription", "AXChildren", "AXFocused")}
_VERDADERO = ctypes.c_void_p.in_dll(_cg, "kCFBooleanTrue")


def atributo(elemento, nombre):
    valor = ctypes.c_void_p()
    if _cg.AXUIElementCopyAttributeValue(elemento, _AX[nombre], ctypes.byref(valor)) == 0:
        return valor.value                 # el llamador debe liberar esta referencia
    return None


def texto_atributo(elemento, nombre):
    valor = atributo(elemento, nombre)
    if not valor:
        return ""
    try:
        if _cg.CFGetTypeID(valor) != _cg.CFStringGetTypeID():
            return ""
        texto = ctypes.create_string_buffer(512)
        if _cg.CFStringGetCString(valor, texto, len(texto), 0x08000100):
            return texto.value.decode("utf-8")
        return ""
    finally:
        _cg.CFRelease(valor)


def buscar_prompt(elemento, limite, restantes, profundidad=0):
    if profundidad > 40 or restantes[0] <= 0 or time.monotonic() >= limite:
        return None
    restantes[0] -= 1
    if texto_atributo(elemento, "AXRole") in ("AXTextArea", "AXTextField"):
        if any(texto_atributo(elemento, nombre).strip().casefold() == "prompt"
               for nombre in ("AXDescription", "AXTitle")):
            return _cg.CFRetain(elemento)
    hijos = atributo(elemento, "AXChildren")
    if not hijos:
        return None
    try:
        if _cg.CFGetTypeID(hijos) == _cg.CFArrayGetTypeID():
            # El editor está después del historial: evita recorrer mensajes antiguos primero.
            for i in reversed(range(_cg.CFArrayGetCount(hijos))):
                encontrado = buscar_prompt(_cg.CFArrayGetValueAtIndex(hijos, i), limite,
                                           restantes, profundidad + 1)
                if encontrado:
                    return encontrado
    finally:
        _cg.CFRelease(hijos)
    return None


def enfocar_entrada():
    """Espera a Claude y enfoca su campo Prompt en la ventana activa, sin tocar el texto."""
    limite = time.monotonic() + 2.0
    while time.monotonic() < limite:
        if app_delante() == APP_CLAUDE:
            asn = subprocess.run(["lsappinfo", "front"], capture_output=True, text=True).stdout.strip()
            info = subprocess.run(["lsappinfo", "info", "-only", "pid", asn],
                                  capture_output=True, text=True).stdout
            try:
                pid = int(info.split("=")[-1].strip())
            except ValueError:
                return False
            app = _cg.AXUIElementCreateApplication(pid)
            ventana = prompt = None
            try:
                if app:
                    _cg.AXUIElementSetMessagingTimeout(app, 0.2)
                    ventana = atributo(app, "AXFocusedWindow")
                if ventana:
                    prompt = buscar_prompt(ventana, limite, [1200])
                if prompt and app_delante() == APP_CLAUDE:
                    if _cg.AXUIElementSetAttributeValue(prompt, _AX["AXFocused"], _VERDADERO) == 0:
                        enfocado = atributo(prompt, "AXFocused")
                        if enfocado:
                            try:
                                if (_cg.CFGetTypeID(enfocado) == _cg.CFBooleanGetTypeID()
                                        and _cg.CFBooleanGetValue(enfocado)):
                                    return True
                            finally:
                                _cg.CFRelease(enfocado)
            finally:
                for referencia in (prompt, ventana, app):
                    if referencia:
                        _cg.CFRelease(referencia)
        time.sleep(0.05)
    print("Claude abierto; no se pudo enfocar el campo Prompt")
    return False


def tecla(codigo, abajo, flags=0):
    ev = _cg.CGEventCreateKeyboardEvent(None, codigo, abajo)
    if not ev:
        raise RuntimeError("No se pudo crear el evento de teclado")
    try:
        _cg.CGEventSetFlags(ev, flags)
        _cg.CGEventPost(0, ev)      # 0 = como si viniera de un teclado
    finally:
        _cg.CFRelease(ev)


def toque(codigo):
    tecla(codigo, True)
    time.sleep(0.02)
    tecla(codigo, False)


def dictado(abajo):
    """Mantiene Shift+B y suelta ambas teclas en orden inverso, una sola vez."""
    global dictado_pulsado
    if abajo == dictado_pulsado:
        return
    if abajo:
        dictado_pulsado = True
        tecla(TECLA_SHIFT, True, FLAG_SHIFT)
        tecla(TECLA_B, True, FLAG_SHIFT)
    else:
        try:
            tecla(TECLA_B, False, FLAG_SHIFT)
        finally:
            try:
                tecla(TECLA_SHIFT, False)
            finally:
                dictado_pulsado = False


def toque_dictado():
    try:
        dictado(True)
        time.sleep(0.02)
    finally:
        dictado(False)


def app_delante():
    asn = subprocess.run(["lsappinfo", "front"], capture_output=True, text=True).stdout.strip()
    info = subprocess.run(["lsappinfo", "info", "-only", "bundleid", asn], capture_output=True, text=True).stdout
    return info.split("=")[-1].strip().strip('"')


def corta():
    if app_delante() == APP_CLAUDE:
        toque(TECLA_ENTER)
    else:
        subprocess.run(["open", "-b", APP_CLAUDE])
        enfocar_entrada()


def abrir_puerto():
    ruta = os.environ.get("BOTON_PUERTO") or next(iter(sorted(glob.glob("/dev/cu.usbmodem*"))), None)
    if not ruta:
        return None
    fd = os.open(ruta, os.O_RDONLY | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0], a[1], a[3] = 0, 0, 0                      # en bruto: sin eco ni traducciones
    a[2] = (a[2] | termios.CLOCAL | termios.CREAD) & ~termios.HUPCL
    termios.tcsetattr(fd, termios.TCSANOW, a)
    print(f"escuchando {ruta}")
    return fd


def escuchar(fd):
    resto, desde, larga = b"", None, False        # desde: cuándo se pulsó · larga: ya se trató como larga
    while True:
        espera = None if desde is None or larga else max(0.0, desde + LARGA_S - time.monotonic())
        listo, _, _ = select.select([fd], [], [], espera)
        if not listo:                               # se cumplió el tiempo con el botón aún pulsado
            larga = True
            dictado(True) if DICTADO == "mantener" else toque_dictado()
            continue
        datos = os.read(fd, 64)
        if not datos:
            raise OSError("puerto cerrado")
        *lineas, resto = (resto + datos).split(b"\n")
        for linea in lineas:
            s = linea.strip()
            if s == b"D" and desde is None:
                desde, larga = time.monotonic(), False
            elif s == b"U" and desde is not None:
                if larga:
                    if DICTADO == "mantener":
                        dictado(False)
                else:
                    corta()
                desde = None


def main():
    while True:
        fd = None
        try:
            fd = abrir_puerto()
            if fd is not None:
                escuchar(fd)
        except OSError as e:                        # desenchufado: se suelta Shift+B y se reintenta
            print(f"sin placa ({e}); reintento")
            dictado(False)
        finally:
            if fd is not None:
                os.close(fd)
        time.sleep(2)


if __name__ == "__main__":
    def detener(signum, frame):
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, detener)
    signal.signal(signal.SIGINT, detener)
    try:
        main()
    finally:
        dictado(False)
