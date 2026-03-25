import io
import easyocr
from PIL import Image
import numpy as np
from config import CONFIG

from backend.models import TranslationJob

class OCRHandler:
    """Handles extracting and grouping Japanese text using EasyOCR."""
    
    def __init__(self):
        print("Loading EasyOCR models into memory (this takes a moment)...")
        # GPU=False ensures it works on any machine. Set to True if you have CUDA installed!
        self.reader = easyocr.Reader(['ja', 'en'], gpu=CONFIG.USE_GPU)
        print("OCR Model loaded successfully!")

    def process(self, job: TranslationJob) -> TranslationJob:
        if not job.image_bytes:
            return job
            
        try:
            # 1. Convert PNG bytes into a format EasyOCR can read (NumPy array)
            image = Image.open(io.BytesIO(job.image_bytes)).convert('RGB')
            img_array = np.array(image)
            
            # 2. Run EasyOCR
            results = self.reader.readtext(img_array)
            
            if not results:
                job.raw_japanese = ""
                return job

            # 3. Clean and Group the Text
            blocks = []
            for (bbox, text, prob) in results:
                # Clean up common EasyOCR punctuation mistakes
                cleaned_text = text.replace('_', '、').replace(' ', '')
                if cleaned_text:
                    blocks.append(cleaned_text)

            # 4. Smart Formatting
            if blocks:
                job.raw_japanese = "".join(blocks)
            else:
                job.raw_japanese = ""
            
        except Exception as e:
            print(f"OCR Processing Error: {e}")
            job.raw_japanese = ""
            
        return job

# --- STANDALONE TEST FUNCTION ---
def test_ocr():
    handler = OCRHandler()
    
    # Let's mock a job using the file you tested earlier
    try:
        with open("image_299413.jpg", "rb") as f:
            dummy_bytes = f.read()
            
        dummy_job = TranslationJob(image_bytes=dummy_bytes)
        print("\nRunning OCR process...")
        result_job = handler.process(dummy_job)
        
        print("-" * 40)
        print("OCR Pipeline Test Complete!")
        print(f"Final Formatted String for LLM:\n{result_job.raw_japanese}")
        print("-" * 40)
    except FileNotFoundError:
        print("Could not find test image. Run this from the root directory!")

if __name__ == "__main__":
    test_ocr()