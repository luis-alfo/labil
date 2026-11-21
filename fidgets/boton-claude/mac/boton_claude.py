#!/usr/bin/env python3
"""Botón Claude — programa del Mac. Escucha la placa por el puerto serie y decide.

  toque corto        Claude no está delante -> trae la app de Claude al frente
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
