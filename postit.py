import sys
import json
from pathlib import Path
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QFrame, QMenu, QLabel
)
from PySide6.QtGui import QAction

CONFIG_FILE = Path.home() / ".mac_sticky_notes.json"

TEMPLATES = {
    "📌 To-Do List": "• [ ] Operazione 1\n• [ ] Operazione 2\n• [ ] Operazione 3",
    "🛒 Lista Spesa": "• Pane\n• Latte\n• Frutta",
    "📅 Meeting Notes": "Data: \nPartecipanti: \n\nNote:\n- \n\nAction Items:\n- ",
    "💡 Idea Rapida": "Titolo:\n\nDescrizione:\n",
    "📅 Calendario": "📅 [GG/MM/AAAA]\n\n🕐 Orario: \n\n📍 Luogo: \n\n📝 Evento: \n\n🔔 Promemoria:\n"
}

class StickyNote(QWidget):
    FONT_SIZES = [10, 12, 14, 16, 18, 20, 24, 28, 32]
    
    def __init__(self, data=None):
        super().__init__()
        
        default_data = {
            "text": "",
            "color": "#FFF59D",
            "x": 200, "y": 200, "w": 250, "h": 250,
            "font_family": "Ubuntu",
            "font_size": 14
        }
        if data:
            default_data.update(data)
        self.note_data = default_data
        
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

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(4, 2, 4, 2)

        btn_color = QPushButton("🎨")
        btn_color.setFixedSize(20, 20)
        btn_color.setStyleSheet("border: none; background: transparent;")
        btn_color.clicked.connect(self.change_color)

        btn_font = QPushButton("A")
        btn_font.setFixedSize(20, 20)
        btn_font.setStyleSheet("border: none; background: transparent; color: #000000;")
        btn_font.setToolTip("Font e dimensione")
        btn_font.clicked.connect(self.show_font_menu)

        btn_template = QPushButton("📋")
        btn_template.setFixedSize(20, 20)
        btn_template.setStyleSheet("border: none; background: transparent;")
        btn_template.setToolTip("Inserisci Template")
        btn_template.clicked.connect(self.show_template_menu)

        btn_add = QPushButton("+")
        btn_add.setFixedSize(20, 20)
        btn_add.setStyleSheet("border: none; background: transparent; font-weight: bold; font-size: 14px; color: #000000;")
        btn_add.setToolTip("Nuova Nota")
        btn_add.clicked.connect(self.create_new_note)

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
        header_layout.addWidget(btn_font)
        header_layout.addWidget(btn_template)
        header_layout.addWidget(btn_add)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)

        self.text_edit = QTextEdit()
        self.text_edit.setFrameStyle(QFrame.NoFrame)
        self.text_edit.setPlainText(self.note_data.get("text", ""))
        self.apply_font()

        self.resize_grip = QLabel("↔", self)
        self.resize_grip.setCursor(Qt.SizeFDiagCursor)
        self.resize_grip.setFixedSize(16, 16)
        self.resize_grip.setStyleSheet("""
            QLabel {
                border: none;
                background: rgba(255, 255, 255, 80);
                border-radius: 4px;
            }
        """)
        self.resize_grip.mousePressEvent = self._resize_press_event
        self.resize_grip.mouseMoveEvent = self._resize_move_event

        frame_layout.addLayout(header_layout)
        frame_layout.addWidget(self.text_edit)
        
        main_layout.addWidget(self.background_frame)

        self.setGeometry(
            self.note_data["x"], self.note_data["y"], 
            self.note_data["w"], self.note_data["h"]
        )
        self._update_resize_grip_position()

    def update_style(self):
        color = self.note_data["color"]
        self.background_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
            }}
        """)
    
    def _update_resize_grip_position(self):
        grip_x = self.width() - self.resize_grip.width() - 4
        grip_y = self.height() - self.resize_grip.height() - 4
        self.resize_grip.move(grip_x, grip_y)
    
    def _resize_press_event(self, event):
        if hasattr(self, '_resize_start_pos'):
            return
        self._resize_start_pos = event.globalPosition().toPoint()
        self._resize_start_size = QSize(self.width(), self.height())

    def _resize_move_event(self, event):
        if not hasattr(self, '_resize_start_pos'):
            return
        delta = QPoint(event.globalPosition().toPoint() - self._resize_start_pos)
        new_width = max(150, self._resize_start_size.width() + delta.x())
        new_height = max(100, self._resize_start_size.height() + delta.y())
        self.resize(QSize(new_width, new_height))

    def _resize_release_event(self, event):
        if hasattr(self, '_resize_start_pos'):
            del self._resize_start_pos
            del self._resize_start_size

    def change_color(self):
        colors = ["#FFF59D", "#F48FB1", "#81D4FA", "#A5D6A7", "#E0E0E0"]
        current_idx = colors.index(self.note_data["color"]) if self.note_data["color"] in colors else 0
        next_color = colors[(current_idx + 1) % len(colors)]
        self.note_data["color"] = next_color
        self.update_style()

    def apply_font(self):
        font_family = self.note_data.get("font_family", "Ubuntu")
        font_size = self.note_data.get("font_size", 14)
        self.text_edit.setFontFamily(font_family)
        self.text_edit.setFontPointSize(font_size)
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background: transparent; 
                color: #000000; 
                font-size: {font_size}px;
                font-family: {font_family}, sans-serif;
            }}
        """)

    def show_font_menu(self):
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
        
        fonts_menu = menu.addMenu("💬 Font")
        standard_fonts = ["Ubuntu", "Helvetica Neue", "Arial", "Times New Roman", "Courier New"]
        for font in standard_fonts:
            action = QAction(font, self)
            action.triggered.connect(lambda _, f=font: self.set_font_family(f))
            fonts_menu.addAction(action)
        
        size_menu = menu.addMenu("🔢 Dimensione")
        for size in self.FONT_SIZES:
            action = QAction(f"{size}px", self)
            action.triggered.connect(lambda _, s=size: self.set_font_size(s))
            size_menu.addAction(action)
        
        menu.exec_(self.cursor().pos())

    def set_font_family(self, font_family):
        self.note_data["font_family"] = font_family
        self.apply_font()

    def set_font_size(self, font_size):
        self.note_data["font_size"] = font_size
        self.apply_font()

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
            "h": self.height(),
            "font_family": self.note_data["font_family"],
            "font_size": self.note_data["font_size"]
        }
        app_instance = QApplication.instance()
        if hasattr(app_instance, "manager"):
            app_instance.manager.add_note(new_data)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._update_resize_grip_position()
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
            "h": self.height(),
            "font_family": self.note_data.get("font_family", "Ubuntu"),
            "font_size": self.note_data.get("font_size", 14)
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
            self.add_note({"text": "Benvenuto! Scrivi qui le tue note...", "color": "#FFF59D", "x": 300, "y": 200, "w": 250, "h": 250, "font_family": "Ubuntu", "font_size": 14})

    def save_notes(self):
        active_notes = [n.get_data() for n in self.notes if n.isVisible()]
        with open(CONFIG_FILE, "w") as f:
            json.dump(active_notes, f, indent=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = NoteManager()
    app.manager = manager
    
    app.aboutToQuit.connect(manager.save_notes)
    sys.exit(app.exec())