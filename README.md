# Mac Sticky Notes for Ubuntu 📌

Un'applicazione di note adesive sul desktop in stile macOS, sviluppata in Python con PySide6 (Qt).

## Caratteristiche
- 🎨 Colori pastello stile Mac
- 🖤 Testo nero per una leggibilità ottimale
- 📋 Template integrati (To-Do List, Spesa, Meeting Notes, Idea Rapida)
- 📌 Spostamento e ridimensionamento senza bordi
- 💾 Salvataggio automatico delle note e delle posizioni

## Installazione rapida

```bash
git clone [https://github.com/RubenNovello/Sticky_Notes_byRuben.git](https://github.com/RubenNovello/Sticky_Notes_byRuben.git)
cd Sticky_Notes_byRuben
./install.sh
cat << 'EOF' > .gitignore
__pycache__/
*.pyc
.mac_sticky_notes.json
.venv/
