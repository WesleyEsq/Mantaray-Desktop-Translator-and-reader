import os
import sys

os.environ["QT_QPA_PLATFORM"] = "xcb" 

from PySide6.QtWidgets import QApplication
import qdarktheme

from frontend.main_window import MantarayMainWindow

def main():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("auto")
    
    window = MantarayMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()