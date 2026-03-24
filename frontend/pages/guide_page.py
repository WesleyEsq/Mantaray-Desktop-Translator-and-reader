from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser
from PySide6.QtCore import Qt

class GuidePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        
        self.main_window = main_window
        self.current_page = 0
        
        # The content for our manual pages using simple HTML for formatting
        self.pages = [
            {
                "title": "1. Getting Started",
                "body": "<p><b>Welcome to Mantaray!</b></p>"
                        "<p>This tool translates Japanese Visual Novels in real-time.</p>"
                        "<p>First, go to the <b>Configuration</b> menu and ensure your Google API Key is entered.</p>"
            },
            {
                "title": "2. Capturing Text",
                "body": "<ol>"
                        "<li>Click <b>'Select Capture Region'</b>.</li>"
                        "<li>Draw a box over the dialogue area of your game.</li>"
                        "<li>Keep the game running in Windowed or Borderless mode for best results.</li>"
                        "</ol>"
            },
            {
                "title": "3. Translation",
                "body": "<p>Click <b>'Start translation'</b> to begin.</p>"
                        "<p>Mantaray will monitor the selected area and automatically translate new text as it appears on the screen.</p>"
            }
        ]
        
        lyt_main = QVBoxLayout(self)
        lyt_main.setContentsMargins(20, 20, 20, 20)
        
        # --- Title & Close Button ---
        lyt_header = QHBoxLayout()
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold;") 
        
        self.btn_close = QPushButton("Close")
        self.btn_close.setFixedSize(60, 25) 
        
        lyt_header.addWidget(self.lbl_title)
        lyt_header.addStretch()
        lyt_header.addWidget(self.btn_close)
        
        # --- Native Text Browser (Replaces ScrollArea) ---
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        # Give it a subtle border so it looks like a document view
        self.text_browser.setStyleSheet("font-size: 15px; border: 1px solid #555; border-radius: 5px; padding: 10px;")
        
        # --- Navigation Buttons ---
        lyt_nav = QHBoxLayout()
        self.btn_prev = QPushButton("Previous")
        self.btn_next = QPushButton("Next")
        
        self.btn_prev.setFixedSize(80, 25)
        self.btn_next.setFixedSize(80, 25)
        
        lyt_nav.addWidget(self.btn_prev)
        lyt_nav.addStretch()
        lyt_nav.addWidget(self.btn_next)
        
        # --- Assemble Layout ---
        lyt_main.addLayout(lyt_header)
        lyt_main.addSpacing(10)
        lyt_main.addWidget(self.text_browser, stretch=1) # stretch=1 forces it to fill available space
        lyt_main.addSpacing(10)
        lyt_main.addLayout(lyt_nav)
        
        # --- Signals ---
        self.btn_close.clicked.connect(self.close_guide)
        self.btn_prev.clicked.connect(self.page_backward)
        self.btn_next.clicked.connect(self.page_forward)
        
        # Load the first page
        self._update_ui()

    def _update_ui(self):
        """Updates the title, text, and button states based on the current page."""
        page_data = self.pages[self.current_page]
        self.lbl_title.setText(page_data["title"])
        self.text_browser.setHtml(page_data["body"])
        
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < len(self.pages) - 1)

    def page_forward(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self._update_ui()

    def page_backward(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_ui()

    def close_guide(self):
        # Reset to page 1 for the next time they open the guide
        self.current_page = 0
        self._update_ui()
        self.main_window.switch_page(self.main_window.page_controls, "Ready.")