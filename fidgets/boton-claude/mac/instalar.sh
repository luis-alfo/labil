#!/bin/sh
# Deja el programa arrancando solo en cada inicio de sesión del Mac.
# Para quitarlo: launchctl unload ~/Library/LaunchAgents/es.lagu.boton-claude.plist
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Library/LaunchAgents/es.lagu.boton-claude.plist"
mkdir -p "$HOME/Library/LaunchAgents"
sed "s|RUTA|$AQUI|" "$AQUI/es.lagu.boton-claude.plist" > "$DEST"
launchctl unload "$DEST" 2>/dev/null || true
launchctl load "$DEST"
echo "instalado. registro en /tmp/boton-claude.log"
