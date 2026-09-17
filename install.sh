#!/bin/bash
set -e

APP_NAME="Sticky Notes by Ruben"
INSTALL_DIR="$HOME/.local/share/sticky-notes-by-ruben"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "🚀 Installazione di $APP_NAME in corso..."

mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"

echo "📦 Installazione dipendenze Python..."
python3 -m pip install PySide6 --break-system-packages

echo "📁 Copia dei file..."
cp postit.py "$INSTALL_DIR/postit.py"

cat << 'INNER_EOF' > "$BIN_DIR/sticky-notes-by-ruben"
#!/bin/bash
python3 "$HOME/.local/share/sticky-notes-by-ruben/postit.py" "$@"
INNER_EOF
chmod +x "$BIN_DIR/sticky-notes-by-ruben"

cat << INNER_EOF > "$DESKTOP_DIR/sticky-notes-by-ruben.desktop"
[Desktop Entry]
Name=Sticky Notes by Ruben
Comment=Post-it in stile macOS
Exec=$BIN_DIR/sticky-notes-by-ruben
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Utility;Office;
INNER_EOF

chmod +x "$DESKTOP_DIR/sticky-notes-by-ruben.desktop"

echo "✅ Installazione completata! Ora trovi 'Sticky Notes by Ruben' nel menu applicazioni."
