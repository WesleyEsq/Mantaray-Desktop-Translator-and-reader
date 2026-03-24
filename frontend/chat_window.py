from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PySide6.QtCore import Qt
from config import CONFIG

class ChatWindow(QWidget):
    """A standard, minimizable window that displays translation history like a chat."""
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mantaray - Translation Log")
        self.resize(400, 600)
        
        # Standard window flags so it has a title bar, minimize, and close buttons
        # WindowStaysOnTopHint keeps it visible while you read your game
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)

        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(10, 10, 10, 10)

        self.text_browser = QTextBrowser()
        # Clean, modern dark styling for the background
        self.text_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: #1e1e1e;
                border-radius: 8px;
                padding: 10px;
                font-family: '{CONFIG.OVERLAY_FONT_FAMILY}';
            }}
        """)
        
        lyt.addWidget(self.text_browser)

    def append_translation(self, jp_text: str, en_text: str):
        """Formats the texts as a chat bubble and appends to the history."""
        
        # HTML formatting to create a "Chat Bubble" look
        html = f"""
        <div style='margin-bottom: 15px;'>
            <div style='color: #888888; font-size: 13px; margin-bottom: 4px; padding-left: 5px;'>
                {jp_text}
            </div>
            <div style='background-color: #2a3b7a; padding: 12px; border-radius: 10px; color: white; font-size: {CONFIG.OVERLAY_FONT_SIZE - 4}px; font-weight: bold;'>
                {en_text}
            </div>
        </div>
        """
        self.text_browser.append(html)
        
        # Force the scrollbar to the bottom so the newest text is always visible
        scrollbar = self.text_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())