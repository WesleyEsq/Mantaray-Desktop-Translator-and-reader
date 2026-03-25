import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPushButton
from PySide6.QtCore import Qt
from config import CONFIG

class ChatWindow(QWidget):
    """A highly legible, accessible chat window for reading Visual Novel translations."""
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mantaray - Live Translation")
        self.resize(450, 650)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)

        self.messages = []

        lyt_main = QVBoxLayout(self)
        lyt_main.setContentsMargins(0, 0, 0, 0)
        lyt_main.setSpacing(0)

        # --- 1. Blue Header ---
        self.lbl_header = QLabel("Live Translations")
        self.lbl_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_header.setStyleSheet("""
            background-color: #2a3b7a; 
            color: white; 
            font-size: 16px; 
            font-weight: bold; 
            padding: 12px;
        """)

        # --- 2. The Chat Area ---
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        # Ensure scrollbar appears gracefully when text fills the window
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                padding: 15px;
                border: none;
            }
        """)
        
        # --- 3. Blue Footer with Buttons ---
        self.wg_footer = QWidget()
        self.wg_footer.setStyleSheet("background-color: #2a3b7a;")
        lyt_footer = QHBoxLayout(self.wg_footer)
        lyt_footer.setContentsMargins(15, 10, 15, 10)
        
        btn_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.3); }
        """
        
        self.btn_clear = QPushButton("Clear History")
        self.btn_clear.setToolTip("Erase all current chat history.")
        self.btn_clear.setStyleSheet(btn_style)
        self.btn_clear.clicked.connect(self.clear_chat)
        
        # Centering the clear button cleanly
        lyt_footer.addStretch()
        lyt_footer.addWidget(self.btn_clear)
        lyt_footer.addStretch()

        # Assemble Layout
        lyt_main.addWidget(self.lbl_header)
        lyt_main.addWidget(self.text_browser, stretch=1)
        lyt_main.addWidget(self.wg_footer)

    def append_translation(self, jp_text: str, en_text: str):
        """Saves the message and triggers a UI re-render."""
        # No more Regex! Just save the raw text directly.
        self.messages.append({
            "jp": jp_text,
            "en": en_text
        })
        
        self._render_chat_html()

    def _render_chat_html(self):
        """Builds the HTML. Uses a left-border to highlight the newest text."""
        html_content = ""
        
        for index, msg in enumerate(self.messages):
            is_newest = (index == len(self.messages) - 1)
            
            opacity = "1.0" if is_newest else "0.6"
            left_border = "4px solid #4a6bdf" if is_newest else "4px solid transparent"
            
            bubble = f"""
            <div style='border-left: {left_border}; border-bottom: 1px solid rgba(128, 128, 128, 0.2); padding-left: 12px; padding-bottom: 15px; margin-bottom: 15px; opacity: {opacity};'>
                <div style='font-size: 14px; margin-bottom: 8px;'>
                    {msg['jp']}
                </div>
                <div style='font-size: {CONFIG.OVERLAY_FONT_SIZE - 4}px; font-weight: bold; font-family: "{CONFIG.OVERLAY_FONT_FAMILY}";'>
                    {msg['en']}
                </div>
            </div>
            """
            html_content += bubble

        self.text_browser.setHtml(html_content)
        
        scrollbar = self.text_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_chat(self):
        self.messages.clear()
        self.text_browser.clear()