from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton

class ControlsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        
        self.main_window = main_window # Store reference to the orchestrator
        
        lyt_controls = QVBoxLayout(self)
        lyt_controls.setContentsMargins(20, 20, 20, 20)
        
        # --- Group Box ---
        grp_control = QGroupBox("control:")
        lyt_grp = QVBoxLayout()
        
        btn_style = "QPushButton { border: 1px solid #ccc; border-radius: 5px; padding: 10px; font-weight: bold; font-size: 14px; }"
        
        # --- Buttons ---
        self.btn_select = QPushButton("Select Capture Region")
        self.btn_select.setStyleSheet(btn_style)
        
        self.btn_start = QPushButton("Start translation")
        self.btn_start.setStyleSheet(btn_style)
        
        self.btn_stop = QPushButton("Stop translator")
        self.btn_stop.setStyleSheet(btn_style)
        self.btn_stop.setEnabled(False) # Disabled initially
        
        lyt_grp.addWidget(self.btn_select)
        lyt_grp.addWidget(self.btn_start)
        lyt_grp.addWidget(self.btn_stop)
        grp_control.setLayout(lyt_grp)
        
        # Configuration Button
        self.btn_config = QPushButton("Enter configuration")
        self.btn_config.setStyleSheet(btn_style)
        
        # Build Layout
        lyt_controls.addWidget(grp_control)
        lyt_controls.addSpacing(15)
        lyt_controls.addWidget(self.btn_config)
        lyt_controls.addStretch()

        # --- Signal Connections ---
        # Notice how we use self.main_window to trigger the page switch!
        self.btn_config.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.page_config, "Configuration...")
        )
        self.btn_select.clicked.connect(self.main_window.open_selector) # <-- Update this line
        self.btn_start.clicked.connect(self.main_window.on_start)
        self.btn_stop.clicked.connect(self.main_window.on_stop)