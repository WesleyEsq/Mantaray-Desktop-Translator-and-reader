import io
from PIL import Image
from manga_ocr import MangaOcr

from backend.models import TranslationJob

class OCRHandler:
    """Handles extracting Japanese text from image bytes using manga-ocr."""
    
    def __init__(self):
        # This initializes the AI model. It takes a few seconds to load into RAM.
        print("Loading manga-ocr model into memory (this takes a moment)...")
        self.mocr = MangaOcr()
        print("OCR Model loaded successfully!")

    def process(self, job: TranslationJob) -> TranslationJob:
        """
        Takes a TranslationJob containing image_bytes, runs the OCR, 
        and updates the job with the extracted Japanese text.
        """
        if not job.image_bytes:
            print("OCR skipped: No image bytes provided.")
            return job
            
        try:
            # 1. Convert the raw PNG bytes back into a Pillow Image object
            image = Image.open(io.BytesIO(job.image_bytes))
            
            # 2. Feed the image to the model
            extracted_text = self.mocr(image)
            
            # 3. Save the result to our job object (strip trailing whitespace)
            job.raw_japanese = extracted_text.strip()
            
        except Exception as e:
            print(f"OCR Processing Error: {e}")
            job.raw_japanese = ""
            
        return job

# --- STANDALONE TEST FUNCTION ---

def test_ocr():
    """Runs a local test to ensure the model downloads and processes correctly."""
    
    print("Initializing OCRHandler...")
    handler = OCRHandler()
    dummy_image = Image.new('RGB', (300, 100), color=(255, 255, 255))
    byte_io = io.BytesIO()
    dummy_image.save(byte_io, format='PNG')
    
    
    # Create a dummy job
    dummy_job = TranslationJob(image_bytes=byte_io.getvalue())
    print("Running OCR process...")
    result_job = handler.process(dummy_job)
    
    # Output the results
    print("-" * 40)
    print(" OCR Pipeline Test Complete!")
    print(f"Extracted Text: '{result_job.raw_japanese}'")
    print("(Note: It is perfectly normal for this to be empty or gibberish since we fed it a blank white image.)")
    print("-" * 40)

if __name__ == "__main__":
    test_ocr()