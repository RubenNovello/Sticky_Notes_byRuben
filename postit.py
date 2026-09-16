import sys
import json
from pathlib import Path
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QFrame, QMenu
)
from PySide6.QtGui import QAction

CONFIG_FILE = Path.home() / ".mac_sticky_notes.json"

# Template predefiniti per velocizzare le note
TEMPLATES = {
    "📌 To-Do List": "• [ ] Operazione 1\n• [ ] Operazione 2\n• [ ] Operazione 3",
    "🛒 Lista Spesa": "• Pane\n• Latte\n• Frutta",
    "📅 Meeting Notes": "Data: \nPartecipanti: \n\nNote:\n- \n\nAction Items:\n- ",
    "💡 Idea Rapida": "Titolo:\n\nDescrizione:\n"
}

class StickyNote(QWidget):
    def __init__(self, data=None):
        super().__init__()
        
        self.note_data = data or {
            "text": "",
            "color": "#FFF59D",  # Giallo Mac
            "x": 200, "y": 200, "w": 250, "h": 250
        }

        self.old_pos = None
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.background_frame = QFrame(self)
        self.update_style()
        
        frame_layout = QVBoxLayout(self.background_frame)
        frame_layout.setContentsMargins(8, 6, 8, 8)

        # Header (Barra superiore)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(4, 2, 4, 2)

        # Bottone Cambio Colore
        btn_color = QPushButton("🎨")
        btn_color.setFixedSize(20, 20)
        btn_color.setStyleSheet("border: none; background: transparent;")
        btn_color.clicked.connect(self.change_color)

        # Bottone Template (📋)
        btn_template = QPushButton("📋")
        btn_template.setFixedSize(20, 20)
        btn_template.setStyleSheet("border: none; background: transparent;")
        btn_template.setToolTip("Inserisci Template")
        btn_template.clicked.connect(self.show_template_menu)

        # Bottone Nuova Nota (+)
        btn_add = QPushButton("+")
        btn_add.setFixedSize(20, 20)
        btn_add.setStyleSheet("border: none; background: transparent; font-weight: bold; font-size: 14px; color: #333333;")
        btn_add.setToolTip("Nuova Nota")
        btn_add.clicked.connect(self.create_new_note)

        # Bottone Chiudi (Stile Mac)
        btn_close = QPushButton("×")
        btn_close.setFixedSize(18, 18)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #FF5F56; 
                color: white; 
                border-radius: 9px; 
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #E0443E; }
        """)
        btn_close.clicked.connect(self.close)

        header_layout.addWidget(btn_color)
        header_layout.addWidget(btn_template)
        header_layout.addWidget(btn_add)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)

        # Area di testo (Testo NERO)
        self.text_edit = QTextEdit()
        self.text_edit.setFrameStyle(QFrame.NoFrame)
        self.text_edit.setPlainText(self.note_data.get("text", ""))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: transparent; 
                color: #000000; 
                font-size: 14px;
                font-family: 'Ubuntu', 'Helvetica Neue', sans-serif;
            }
        """)

        frame_layout.addLayout(header_layout)
        frame_layout.addWidget(self.text_edit)
        main_layout.addWidget(self.background_frame)

        self.setGeometry(
            self.note_data["x"], self.note_data["y"], 
            self.note_data["w"], self.note_data["h"]
        )

    def update_style(self):
        color = self.note_data["color"]
        self.background_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
            }}
        """)

    def change_color(self):
        colors = ["#FFF59D", "#F48FB1", "#81D4FA", "#A5D6A7", "#E0E0E0"]
        current_idx = colors.index(self.note_data["color"]) if self.note_data["color"] in colors else 0
        next_color = colors[(current_idx + 1) % len(colors)]
        self.note_data["color"] = next_color
        self.update_style()

    def show_template_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #E0E0E0;
            }
        """)
        
        for name, text in TEMPLATES.items():
            action = QAction(name, self)
            action.triggered.connect(lambda _, t=text: self.apply_template(t))
            menu.addAction(action)
            
        menu.exec_(self.cursor().pos())

    def apply_template(self, text):
        if self.text_edit.toPlainText().strip():
            # Aggiunge in coda se c'è già del testo
            self.text_edit.append(f"\n{text}")
        else:
            self.text_edit.setPlainText(text)

    def create_new_note(self):
        new_data = {
            "text": "",
            "color": self.note_data["color"],
            "x": self.x() + 30,
            "y": self.y() + 30,
            "w": self.width(),
            "h": self.height()
        }
        app_instance = QApplication.instance()
        if hasattr(app_instance, "manager"):
            app_instance.manager.add_note(new_data)

    # --- Trascinamento Finestra ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def get_data(self):
        return {
            "text": self.text_edit.toPlainText(),
            "color": self.note_data["color"],
            "x": self.x(),
            "y": self.y(),
            "w": self.width(),
            "h": self.height()
        }


class NoteManager:
    def __init__(self):
        self.notes = []
        self.load_notes()

    def add_note(self, data=None):
        note = StickyNote(data)
        note.show()
        self.notes.append(note)

    def load_notes(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    data_list = json.load(f)
                    for data in data_list:
                        self.add_note(data)
            except Exception:
                pass

        if not self.notes:
            self.add_note({"text": "Benvenuto! Scrivi qui le tue note...", "color": "#FFF59D", "x": 300, "y": 200, "w": 250, "h": 250})

    def save_notes(self):
        active_notes = [n.get_data() for n in self.notes if n.isVisible()]
        with open(CONFIG_FILE, "w") as f:
            json.dump(active_notes, f, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = NoteManager()
    app.manager = manager  # Riferimento globale per il pulsante "+"
    
    app.aboutToQuit.connect(manager.save_notes)
    sys.exit(app.exec())