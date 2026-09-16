#!/bin/bash
set -e

APP_NAME="mac-stickies"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "🚀 Installazione di $APP_NAME in corso..."

# 1. Crea le directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"

# 2. Installa dipendenza PySide6
echo "📦 Installazione dipendenze Python..."
python3 -m pip install PySide6 --break-system-packages

# 3. Copia lo script postit.py nella directory d'installazione
echo "📁 Copia dei file..."
cp postit.py "$INSTALL_DIR/postit.py"

# 4. Crea l'eseguibile di avvio
cat << 'INNER_EOF' > "$BIN_DIR/mac-stickies"
#!/bin/bash
python3 "$HOME/.local/share/mac-stickies/postit.py" "$@"
INNER_EOF
chmod +x "$BIN_DIR/mac-stickies"

# 5. Crea il launcher .desktop per il menu
cat << INNER_EOF > "$DESKTOP_DIR/mac-stickies.desktop"
[Desktop Entry]
Name=Mac Sticky Notes
Comment=Post-it in stile macOS
Exec=$BIN_DIR/mac-stickies
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Utility;Office;
INNER_EOF

chmod +x "$DESKTOP_DIR/mac-stickies.desktop"

echo "✅ Installazione completata! Puoi avviarla dal menu o digita 'mac-stickies' nel terminale."
