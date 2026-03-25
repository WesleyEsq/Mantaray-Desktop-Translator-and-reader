import time 
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

from backend.capture_handler import CaptureHandler
from backend.ocr_handler import OCRHandler
from backend.llm_handler import LLMHandler

from frontend.pages.loading_page import LoadingPage
from frontend.pages.controls_page import ControlsPage
from frontend.pages.config_page import ConfigPage
from frontend.pages.guide_page import GuidePage

from frontend.selector import RegionSelector
from frontend.chat_window import ChatWindow



from config import CONFIG

class BackendLoaderThread(QThread):
    finished_loading = Signal(object, object, object) 

    def run(self):
        capture = CaptureHandler()
        ocr = OCRHandler()
        llm = LLMHandler()
        self.finished_loading.emit(capture, ocr, llm)

class TranslationPipelineThread(QThread):
    """Runs the continuous Capture -> OCR -> LLM loop with Debounce protection."""
    translation_ready = Signal(str, str) # Now emits (Japanese, English)
    status_update = Signal(str)

    def __init__(self, capture, ocr, llm):
        super().__init__()
        self.capture = capture
        self.ocr = ocr
        self.llm = llm
        self.region = None
        self.running = False
        
        self.last_translated_text = ""
        self.current_ocr_text = ""
        self.stability_counter = 0
        self.STABILITY_THRESHOLD = 3 

    def run(self):
        self.running = True
        while self.running:
            if not self.region:
                time.sleep(0.3)
                continue

            # Start total pipeline timer
            loop_start = time.perf_counter()

            # 1. Measure Capture Time
            t0 = time.perf_counter()
            job = self.capture.capture(self.region)
            t1 = time.perf_counter()
            capture_time = (t1 - t0) * 1000 # Convert to milliseconds
            
            # 2. Measure OCR Time
            t0 = time.perf_counter()
            job = self.ocr.process(job)
            t1 = time.perf_counter()
            ocr_time = (t1 - t0) * 1000
            
            raw_text = job.raw_japanese

            # 3. Debounce & Translate
            if raw_text:
                if raw_text == self.current_ocr_text:
                    self.stability_counter += 1
                else:
                    self.current_ocr_text = raw_text
                    self.stability_counter = 0
                    self.status_update.emit("Reading text...")

                # Translate if stable
                if self.stability_counter >= self.STABILITY_THRESHOLD and raw_text != self.last_translated_text:
                    self.status_update.emit("Translating via API...")
                    self.last_translated_text = raw_text
                    
                    # Measure LLM Translation Time
                    t0 = time.perf_counter()
                    job = self.llm.translate(job)
                    t1 = time.perf_counter()
                    llm_time = (t1 - t0) * 1000
                    
                    self.translation_ready.emit(job.raw_japanese, job.english_translation)
                    self.status_update.emit("Monitoring screen...")
                    
                    # --- PRINT THE LATENCY REPORT TO TERMINAL ---
                    print("\n" + "="*40)
                    print("> LATENCY REPORT:")
                    print(f"   Screen Capture : {capture_time:.1f} ms")
                    print(f"   EasyOCR        : {ocr_time:.1f} ms")
                    print(f"   LLM API        : {llm_time:.1f} ms")
                    print(f"   Total Pipeline : {(time.perf_counter() - loop_start) * 1000:.1f} ms")
                    print("="*40 + "\n")

            time.sleep(0.3)

    def stop(self):
        self.running = False

class MantarayMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Mantaray - Desktop AI Reader")
        self.resize(350, 480) 
        
        self.capture_handler = None
        self.ocr_handler = None
        self.llm_handler = None
        self.current_region = None
        self.bounding_box = None # <--- NEW: Store the visual indicator
        
        self.lyt_main = QVBoxLayout(self)
        self.lyt_main.setContentsMargins(0, 0, 0, 0)
        self.lyt_main.setSpacing(0)
        
        self._build_header()
        
        self.stk_pages = QStackedWidget()
        self.page_loading = LoadingPage()
        self.page_controls = ControlsPage(self) 
        self.page_config = ConfigPage(self)
        self.page_guide = GuidePage(self)
        
        self.stk_pages.addWidget(self.page_loading)
        self.stk_pages.addWidget(self.page_controls)
        self.stk_pages.addWidget(self.page_config)
        self.stk_pages.addWidget(self.page_guide)
        
        self._build_footer()
        
        self.lyt_main.addWidget(self.wg_header)
        self.lyt_main.addWidget(self.stk_pages, stretch=1)
        self.lyt_main.addWidget(self.lbl_footer)
        
        self.switch_page(self.page_loading, "loading the model...")
        self.start_backend_loader()

    def _build_header(self):
        self.wg_header = QWidget()
        self.wg_header.setStyleSheet("background-color: #2a3b7a; color: white;")
        self.wg_header.setMinimumHeight(70)
        
        lyt_header = QHBoxLayout(self.wg_header)
        lyt_header.setContentsMargins(15, 10, 15, 10)
        
        self.btn_guide = QPushButton()
        self.btn_guide.setIcon(QIcon("assets/book.svg"))
        self.btn_guide.setIconSize(QSize(25, 25))
        self.btn_guide.setFixedSize(40, 40)
        self.btn_guide.setStyleSheet("""
            QPushButton { background-color: rgba(255, 255, 255, 0.8); border-radius: 18px; border: none; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 1); }
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

    def set_status(self, message: str):
        self.lbl_footer.setText(message)

    def switch_page(self, page: QWidget, status: str):
        self.stk_pages.setCurrentWidget(page)
        self.set_status(status)

    def start_backend_loader(self):
        self.loader_thread = BackendLoaderThread()
        self.loader_thread.finished_loading.connect(self.on_backend_loaded)
        self.loader_thread.start()

    def on_backend_loaded(self, capture, ocr, llm):
        self.capture_handler = capture
        self.ocr_handler = ocr
        self.llm_handler = llm
        
        self.pipeline_thread = TranslationPipelineThread(capture, ocr, llm)
        self.pipeline_thread.translation_ready.connect(self.on_translation_ready)
        self.pipeline_thread.status_update.connect(self.set_status)
        
        self.chat_window = ChatWindow() # <--- Initialize the new chat window
        
        self.switch_page(self.page_controls, "Ready.")

    def on_start(self):
        if not self.current_region:
            self.set_status("Error: Please select a capture region first!")
            return
            
        self.page_controls.btn_start.setEnabled(False)
        self.page_controls.btn_stop.setEnabled(True)
        self.set_status("Starting translation engine...")
        
        self.chat_window.show() # <--- Show the window
            
        self.pipeline_thread.region = self.current_region
        self.pipeline_thread.start()
        
    def on_stop(self):
        self.page_controls.btn_start.setEnabled(True)
        self.page_controls.btn_stop.setEnabled(False)
        self.set_status("Paused.")
        
        self.pipeline_thread.stop()
        self.pipeline_thread.wait()
        
    def on_translation_ready(self, jp_text, en_text):
        self.chat_window.append_translation(jp_text, en_text)
        
    def open_selector(self):
        self.hide() 
        self.selectors = [] # Keep a list of all active overlays
        from PySide6.QtWidgets import QApplication
        # Spawn a perfect overlay for EVERY monitor connected to the PC
        for screen in QApplication.screens():
            selector = RegionSelector(screen.geometry())
            selector.region_selected.connect(self.on_region_selected)
            selector.selection_cancelled.connect(self.on_selection_cancelled) 
            selector.show()
            self.selectors.append(selector)
        
    def on_region_selected(self, region):
        self.current_region = region
        # Close all the selector overlays since we got our box
        for selector in self.selectors:
            selector.close()
        self.selectors.clear()
        self.show() 
        self.set_status(f"Target locked: {region.width}x{region.height} px")

    def on_selection_cancelled(self):
        # Safely close all overlays if the user hits Escape
        for selector in self.selectors:
            selector.close()
        self.selectors.clear()
        
        self.show() 
        self.set_status("Selection cancelled.")

    def closeEvent(self, event):
        """Catches the Window Close event to safely kill background threads."""
        print("Shutting down Mantaray...")
        if hasattr(self, 'pipeline_thread') and self.pipeline_thread.isRunning():
            self.pipeline_thread.stop()
            self.pipeline_thread.wait() 
            
        if hasattr(self, 'chat_window'):
            self.chat_window.close() # <--- Safely close the chat window
            
        event.accept()
        print("Shutdown complete.")