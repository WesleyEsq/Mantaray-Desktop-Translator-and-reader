import time
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QBuffer, QIODevice

from backend.models import ScreenRegion, TranslationJob

class CaptureHandler:
    """Handles in-memory screen capture using native Qt bindings."""
    
    def __init__(self):
        # We grab the running PySide6 application instance (created in main.py)
        self.app = QGuiApplication.instance()
        if not self.app:
            raise RuntimeError("QApplication must be initialized before CaptureHandler.")

    def capture(self, region: ScreenRegion) -> TranslationJob:
        """
        Captures the specified region using Qt, converts it to PNG bytes, 
        and packages it into a TranslationJob.
        """
        
        # Get the primary screen (Qt handles the multi-monitor math for us)
        screen = self.app.primaryScreen()
        
        # Grab the specific region from the root window (WId 0 is the full X11 desktop)
        pixmap = screen.grabWindow(0, region.x, region.y, region.width, region.height)
        
        # Convert the QPixmap directly into PNG bytes in memory using a QBuffer
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        
        # Extract the raw byte data and return it
        return TranslationJob(image_bytes=buffer.data().data())

    def close(self):
        """Clean up if necessary (Qt handles most of its own garbage collection)."""
        pass

# --- STANDALONE TEST FUNCTION ---

def test_capture():
    """Runs a local test of the capture system."""
    print("Initializing Qt CaptureHandler...")
    app = QGuiApplication.instance() or QGuiApplication([])
    
    handler = CaptureHandler()
    test_region = ScreenRegion(x=0, y=0, width=500, height=200)
    print(f"\nTargeting Region: {test_region}")
    
    try:
        # Time the capture
        start_time = time.time()
        job = handler.capture(test_region)
        end_time = time.time()
        
        capture_time_ms = (end_time - start_time) * 1000
        
        if job and job.image_bytes:
            print(" Capture Successful!")
            print(f" Image payload size: {len(job.image_bytes)} bytes")
            print(f" Capture latency: {capture_time_ms:.2f} ms\n")
        else:
            print("  Capture failed: No bytes returned.")
            
    except Exception as e:
         print(f"-- Error during capture: {e}")

if __name__ == "__main__":
    test_capture()