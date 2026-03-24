from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

class LoadingPage(QWidget):
    def __init__(self):
        super().__init__()
        
        lyt_loading = QVBoxLayout(self)
        lyt_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_subtitle = QLabel("Japanese Literature Translator")
        # Use a neutral gray that looks good on any theme
        lbl_subtitle.setStyleSheet("font-size: 16px; color: #888888; font-weight: bold;")
        
        # --- Native Qt "Indeterminate" Loading Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Setting range to 0,0 triggers the continuous sweeping animation
        self.progress_bar.setTextVisible(False) # Hide the "0%" text
        self.progress_bar.setFixedSize(200, 15) # Nice compact size
        
        lbl_status = QLabel("Loading AI Models...")
        lbl_status.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # Add to layout
        lyt_loading.addWidget(lbl_subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        lyt_loading.addSpacing(40)
        lyt_loading.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        lyt_loading.addSpacing(15)
        lyt_loading.addWidget(lbl_status, alignment=Qt.AlignmentFlag.AlignCenter)