import os
import io
import time
import subprocess
from PIL import Image
from PySide6.QtGui import QGuiApplication

from backend.models import ScreenRegion, TranslationJob

class CaptureHandler:
    """Handles screen capture on Wayland by delegating to native trusted tools (Spectacle)."""
    
    def __init__(self):
        # We will save the full-screen trusted capture to a temporary system file
        self.temp_file = "/tmp/mantaray_full_screen.png"
        print("KDE Spectacle Capture engine initialized.")

    def capture(self, region: ScreenRegion) -> TranslationJob:
        if not region:
            return TranslationJob(image_bytes=b"")
            
        try:
            # 1. Ask KDE's trusted native tool to take a full-desktop background screenshot
            subprocess.run(["spectacle", "-f", "-b", "-n", "-o", self.temp_file], check=True)
            img = Image.open(self.temp_file)
            
            # --- THE COORDINATE & HiDPI FIX ---
            app = QGuiApplication.instance()
            
            # Find the global minimums (Top-Left of the entire virtual desktop map)
            min_x = min(screen.geometry().x() for screen in app.screens())
            min_y = min(screen.geometry().y() for screen in app.screens())
            
            # Convert the region's local widget coordinates back to global desktop coordinates
            global_x = region.x + min_x
            global_y = region.y + min_y
            
            # Find the DPI Scaling factor for the specific monitor the user drew the box on
            ratio = 1.0
            for screen in app.screens():
                if screen.geometry().contains(global_x, global_y):
                    ratio = screen.devicePixelRatio()
                    break
            
            # Multiply the logical Qt coordinates by the monitor's physical scaling ratio
            crop_box = (
                int(region.x * ratio), 
                int(region.y * ratio), 
                int((region.x + region.width) * ratio), 
                int((region.y + region.height) * ratio)
            )
            # -----------------------------------
            
            cropped_img = img.crop(crop_box)
            
            buffer = io.BytesIO()
            cropped_img.save(buffer, format="PNG")
            
            return TranslationJob(image_bytes=buffer.getvalue())
            
        except Exception as e:
            print(f"❌ Capture Error: {e}")
            return TranslationJob(image_bytes=b"")

    def close(self):
        """Clean up the temporary screenshot file when Mantaray closes."""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

# --- STANDALONE TEST FUNCTION ---

def test_capture():
    """Runs a local test of the Spectacle capture system."""
    print("Initializing Spectacle CaptureHandler...")
    # Mocking QApplication for the standalone test so the Qt math works
    app = QGuiApplication.instance() or QGuiApplication([])
    
    handler = CaptureHandler()
    
    # Grab a small chunk of the top-left corner
    test_region = ScreenRegion(x=0, y=0, width=500, height=200)
    print(f"\nTargeting Region: {test_region}")
    
    try:
        start_time = time.time()
        job = handler.capture(test_region)
        end_time = time.time()
        
        capture_time_ms = (end_time - start_time) * 1000
        
        if job and job.image_bytes:
            print("✅ Capture Successful!")
            print(f" Image payload size: {len(job.image_bytes)} bytes")
            print(f" Capture latency: {capture_time_ms:.2f} ms\n")
            
            with open("test_spectacle_capture.png", "wb") as f:
                f.write(job.image_bytes)
            print("Saved cropped test frame to 'test_spectacle_capture.png'. Check it to verify!")
                
        else:
            print("❌ Capture failed: No bytes returned.")
            
    except Exception as e:
         print(f"❌ Error during capture: {e}")
    finally:
         handler.close()

if __name__ == "__main__":
    test_capture()