import time 
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QStyle
from PySide6.QtCore import Qt, QThread, Signal

from backend.capture_handler import CaptureHandler
from backend.ocr_handler import OCRHandler
from backend.llm_handler import LLMHandler

from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

# Import our modular pages
from frontend.pages.loading_page import LoadingPage
from frontend.pages.controls_page import ControlsPage
from frontend.pages.config_page import ConfigPage
from frontend.pages.guide_page import GuidePage

#import the functionality for screen translation
from frontend.selector import RegionSelector
from frontend.overlay import TranslationOverlay

class BackendLoaderThread(QThread):
    """Loads the heavy AI models in the background to prevent UI freezing."""
    finished_loading = Signal(object, object, object) 

    def run(self):
        capture = CaptureHandler()
        ocr = OCRHandler()
        llm = LLMHandler()
        self.finished_loading.emit(capture, ocr, llm)

class TranslationPipelineThread(QThread):
    """Runs the continuous Capture -> OCR -> LLM loop in the background."""
    translation_ready = Signal(str)
    status_update = Signal(str)

    def __init__(self, capture, ocr, llm):
        super().__init__()
        self.capture = capture
        self.ocr = ocr
        self.llm = llm
        self.region = None
        self.running = False
        self.last_text = ""

    def run(self):
        self.running = True
        while self.running:
            if not self.region:
                time.sleep(0.5)
                continue

            # 1. Capture the screen
            job = self.capture.capture(self.region)
            
            # 2. Extract Japanese Text
            job = self.ocr.process(job)

            # 3. Only translate if new text appeared
            if job.raw_japanese and job.raw_japanese != self.last_text:
                self.status_update.emit("Translating...")
                self.last_text = job.raw_japanese
                
                # 4. Translate via LLM
                job = self.llm.translate(job)
                self.translation_ready.emit(job.english_translation)
                self.status_update.emit("Monitoring screen...")

            time.sleep(0.5) # Sleep to prevent CPU thrashing

    def stop(self):
        self.running = False

class MantarayMainWindow(QWidget):
    """The primary UI window orchestrating the different application pages."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Manta - Desktop AI Reader")
        self.resize(350, 480) 
        
        # Store our backend handlers here once they load
        self.capture_handler = None
        self.ocr_handler = None
        self.llm_handler = None
        # Region on screen that needs a translation 
        self.current_region = None
        
        # --- Master Layout ---
        self.lyt_main = QVBoxLayout(self)
        self.lyt_main.setContentsMargins(0, 0, 0, 0) # Remove edge gaps for header/footer
        self.lyt_main.setSpacing(0)
        
        # 1. Build Header
        self._build_header()
        
        # 2. Build Stacked Central Area (The Deck of Cards)
        self.stk_pages = QStackedWidget()
        
        # Instantiate our modular pages, passing 'self' so they can trigger navigation
        self.page_loading = LoadingPage()
        self.page_controls = ControlsPage(self) 
        self.page_config = ConfigPage(self)
        self.page_guide = GuidePage(self)
        
        self.stk_pages.addWidget(self.page_loading)
        self.stk_pages.addWidget(self.page_controls)
        self.stk_pages.addWidget(self.page_config)
        self.stk_pages.addWidget(self.page_guide)
        
        # 3. Build Footer
        self._build_footer()
        
        # Assemble Master Layout
        self.lyt_main.addWidget(self.wg_header)
        self.lyt_main.addWidget(self.stk_pages, stretch=1)
        self.lyt_main.addWidget(self.lbl_footer)
        
        # Start State
        self.switch_page(self.page_loading, "loading the model...")
        self.start_backend_loader()

    # --- UI Builders ---
    
    def _build_header(self):
        self.wg_header = QWidget()
        self.wg_header.setStyleSheet("background-color: #2a3b7a; color: white;")
        self.wg_header.setMinimumHeight(70)
        
        lyt_header = QHBoxLayout(self.wg_header)
        lyt_header.setContentsMargins(15, 10, 15, 10)
        
        # Guide Book Button (Circular SVG)
        self.btn_guide = QPushButton()
        self.btn_guide.setIcon(QIcon("assets/book.svg"))
        self.btn_guide.setIconSize(QSize(25, 25)) # Size of the SVG inside the circle
        self.btn_guide.setFixedSize(40, 40) # Make the button a perfect square
        self.btn_guide.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.8); 
                border-radius: 18px; 
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 1);
            }
        """)
        self.btn_guide.clicked.connect(lambda: self.switch_page(self.page_guide, "User Guide"))
        
        
        lbl_title = QLabel("Mantaray")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        lyt_header.addWidget(self.btn_guide)
        lyt_header.addWidget(lbl_title)
        lyt_header.addStretch()
        

    def _build_footer(self):
        self.lbl_footer = QLabel()
        self.lbl_footer.setStyleSheet("background-color: #2a3b7a; color: white; font-weight: bold; font-size: 14px;")
        self.lbl_footer.setMinimumHeight(40)
        self.lbl_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # --- Logic Methods ---

    def set_status(self, message: str):
        """Updates the text in the bottom footer."""
        self.lbl_footer.setText(message)

    def switch_page(self, page: QWidget, status: str):
        """Changes the visible card in the stacked widget and updates the footer."""
        self.stk_pages.setCurrentWidget(page)
        self.set_status(status)

    def start_backend_loader(self):
        """Spawns the thread to load the heavy models."""
        self.loader_thread = BackendLoaderThread()
        self.loader_thread.finished_loading.connect(self.on_backend_loaded)
        self.loader_thread.start()

    def on_backend_loaded(self, capture, ocr, llm):
        """Triggered when the background thread finishes loading."""
        self.capture_handler = capture
        self.ocr_handler = ocr
        self.llm_handler = llm
        
        # Initialize the continuous pipeline thread
        self.pipeline_thread = TranslationPipelineThread(capture, ocr, llm)
        self.pipeline_thread.translation_ready.connect(self.on_translation_ready)
        self.pipeline_thread.status_update.connect(self.set_status)
        
        # Initialize the Overlay window (keep it hidden for now)
        self.overlay = TranslationOverlay()
        
        self.switch_page(self.page_controls, "Ready.")

    # --- Pipeline Control Methods (Triggered by controls_page.py) ---
    
    def on_start(self):
        if not self.current_region:
            self.set_status("Error: Please select a capture region first!")
            return
            
        self.page_controls.btn_start.setEnabled(False)
        self.page_controls.btn_stop.setEnabled(True)
        self.set_status("Starting translation engine...")
        
        # Pass the region to the thread, show the overlay, and start the loop!
        self.pipeline_thread.region = self.current_region
        self.overlay.show()
        self.pipeline_thread.start()
        
    def on_stop(self):
        self.page_controls.btn_start.setEnabled(True)
        self.page_controls.btn_stop.setEnabled(False)
        self.set_status("Paused.")
        
        # Stop the background loop and hide the overlay
        self.pipeline_thread.stop()
        self.pipeline_thread.wait() # Safely wait for the thread to close
        self.overlay.hide()
        
    def on_translation_ready(self, english_text):
        """Triggered by the pipeline thread when a new translation is ready."""
        self.overlay.update_text(english_text)
        
    # ---------------------------------------------
    #         SCREEN REGION SELECTION LOGIC
    # ---------------------------------------------
    def open_selector(self):
        """Hides the main menu and opens the full-screen selector tool."""
        self.hide() 
        
        self.selector = RegionSelector()
        self.selector.region_selected.connect(self.on_region_selected)
        
        # 1. Listen for the cancel signal
        self.selector.selection_cancelled.connect(self.on_selection_cancelled) 
        
        self.selector.show()
        
    def on_region_selected(self, region):
        """Triggered when the user finishes dragging the bounding box."""
        self.current_region = region
        self.show() 
        self.set_status(f"Target locked: {region.width}x{region.height} px")

    # 2. Add this new method to handle the cancellation safely
    def on_selection_cancelled(self):
        """Triggered when the user presses Escape during selection."""
        self.show() # Bring the main menu back!
        self.set_status("Selection cancelled.")