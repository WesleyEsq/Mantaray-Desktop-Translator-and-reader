from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from config import CONFIG

class TranslationOverlay(QWidget):
    """The frameless, transparent, click-through window that displays the translation."""
    
    def __init__(self):
        super().__init__()

        # --- 1. The Magic Window Flags ---
        # Frameless, Always on Top, Ignores Mouse Clicks, and hidden from Taskbar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.Tool
        )
        
        # Tell the OS we want a completely transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Default size and position (we will align this to the bottom of the screen later)
        self.setGeometry(100, 100, 800, 200)

        # --- 2. Layout ---
        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(20, 20, 20, 20)
        lyt.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        # --- 3. Text Label ---
        self.lbl_text = QLabel("Waiting for text...")
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Apply styling directly from your config.py
        self.lbl_text.setStyleSheet(f"""
            QLabel {{
                color: {CONFIG.OVERLAY_TEXT_COLOR};
                font-family: '{CONFIG.OVERLAY_FONT_FAMILY}';
                font-size: {CONFIG.OVERLAY_FONT_SIZE}px;
                font-weight: bold;
                background-color: {CONFIG.OVERLAY_BG_COLOR};
                border-radius: 10px;
                padding: 15px;
            }}
        """)

        # --- 4. Drop Shadow for ultimate readability ---
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(2, 2)
        self.lbl_text.setGraphicsEffect(shadow)

        lyt.addWidget(self.lbl_text)

    def update_text(self, new_text: str):
        """Updates the overlay with the newly translated text."""
        self.lbl_text.setText(new_text)