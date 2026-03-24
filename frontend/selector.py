from PySide6.QtWidgets import QWidget, QRubberBand
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QKeyEvent
from PySide6.QtCore import Qt, QRect, QPoint, Signal

from backend.models import ScreenRegion

class RegionSelector(QWidget):
    """A translucent overlay for drawing a bounding box on a specific screen."""
    
    region_selected = Signal(ScreenRegion)
    selection_cancelled = Signal()

    def __init__(self, screen_geometry):
        super().__init__()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # Instead of spanning all monitors, this instance perfectly covers ONE monitor
        self.setGeometry(screen_geometry)

        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        
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
            
            # CRITICAL FIX: Convert the local widget coordinates to global desktop coordinates
            # This ensures that drawing on Monitor 2 doesn't return X=0, but rather X=1920
            global_top_left = self.mapToGlobal(selection_rect.topLeft())
            
            region = ScreenRegion(
                x=global_top_left.x(),
                y=global_top_left.y(),
                width=selection_rect.width(),
                height=selection_rect.height()
            )
            
            self.region_selected.emit(region)
            self.close()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.selection_cancelled.emit()
            self.close()