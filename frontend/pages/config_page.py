from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QComboBox, QPushButton
import qdarktheme

from config import CONFIG

class ConfigPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        
        self.main_window = main_window
        
        lyt_config = QVBoxLayout(self)
        lyt_config.setContentsMargins(20, 20, 20, 20)
        
        # --- Settings Group ---
        grp_settings = QGroupBox("Configuration")
        grp_settings.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; }")
        lyt_settings = QVBoxLayout()
        
        # API Key
        lbl_api = QLabel("Google API Key")
        self.inp_api = QLineEdit(CONFIG.GOOGLE_API_KEY)
        self.inp_api.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        self.inp_api.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px;")
        
        # Target Language
        lbl_lang = QLabel("Choose a Target Language")
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItems(["English", "Spanish", "French", "German", "Portuguese"])
        self.cmb_lang.setCurrentText(CONFIG.TARGET_LANGUAGE)
        self.cmb_lang.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px;")
        
        # Theme
        lbl_theme = QLabel("Theme")
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(["Auto (System)", "Dark", "Light"])
        self.cmb_theme.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px;")
        
        lyt_settings.addWidget(lbl_api)
        lyt_settings.addWidget(self.inp_api)
        lyt_settings.addSpacing(10)
        lyt_settings.addWidget(lbl_lang)
        lyt_settings.addWidget(self.cmb_lang)
        lyt_settings.addSpacing(10)
        lyt_settings.addWidget(lbl_theme)
        lyt_settings.addWidget(self.cmb_theme)
        grp_settings.setLayout(lyt_settings)
        
        # --- Actions ---
        lyt_actions = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("background-color: #D09394; color: black; font-weight: bold; padding: 10px; border-radius: 5px;")
        
        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet("background-color: #9ECC96; color: black; font-weight: bold; padding: 10px; border-radius: 5px;")
        
        lyt_actions.addWidget(self.btn_cancel)
        lyt_actions.addWidget(self.btn_save)
        
        lyt_config.addWidget(grp_settings)
        lyt_config.addLayout(lyt_actions)
        lyt_config.addStretch()
        
        Mantaray_accent = {"primary": "#A0522D"}
        
        # --- Signal Connections ---
        self.btn_cancel.clicked.connect(
            lambda: self.main_window.switch_page(self.main_window.page_controls, "Ready.")
        )
        self.btn_save.clicked.connect(self.save_configuration)

    def save_configuration(self):
        """Updates the global config and applies theme changes."""
        CONFIG.TARGET_LANGUAGE = self.cmb_lang.currentText()
        CONFIG.GOOGLE_API_KEY = self.inp_api.text()
        
        theme_choice = self.cmb_theme.currentText()
        if theme_choice == "Auto (System)": qdarktheme.setup_theme("auto")
        elif theme_choice == "Dark": qdarktheme.setup_theme("dark")
        elif theme_choice == "Light": qdarktheme.setup_theme("light")
        
        self.main_window.switch_page(self.main_window.page_controls, "Settings saved.")