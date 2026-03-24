from PySide6.QtWidgets import QWidget, QRubberBand, QApplication
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent
from PySide6.QtCore import Qt, QRect, QPoint, Signal

from backend.models import ScreenRegion

class RegionSelector(QWidget):
    """A full-screen, translucent overlay for drawing a bounding box."""
    
    region_selected = Signal(ScreenRegion)
    selection_cancelled = Signal() # <--- 1. ADD THIS NEW SIGNAL

    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        screens = QApplication.screens()
        if not screens:
            self.setGeometry(0, 0, 800, 600)
        else:
            total_rect = screens[0].geometry()
            for screen in screens[1:]:
                total_rect = total_rect.united(screen.geometry())
            self.setGeometry(total_rect)

        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        
        # Mantaray Blue styling
        self.rubber_band.setStyleSheet("""
            QRubberBand {
                background-color: rgba(42, 59, 122, 100);
                border: 2px solid #2a3b7a;
            }
        """)
        
        self.origin = QPoint()

    def paintEvent(self, event):
        painter = QPainter(self)
        overlay_color = QColor(15, 25, 45, 120) 
        painter.fillRect(self.rect(), overlay_color)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.position().toPoint()
            self.rubber_band.setGeometry(QRect(self.origin, self.origin))
            self.rubber_band.show()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.origin.isNull():
            self.rubber_band.setGeometry(QRect(self.origin, event.position().toPoint()).normalized())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            selection_rect = self.rubber_band.geometry()
            self.rubber_band.hide()
            
            region = ScreenRegion(
                x=selection_rect.x(),
                y=selection_rect.y(),
                width=selection_rect.width(),
                height=selection_rect.height()
            )
            
            self.region_selected.emit(region)
            self.close()

    def keyPressEvent(self, event: QKeyEvent):
        """Allows the user to cancel selection safely by pressing Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.selection_cancelled.emit()
            self.close()