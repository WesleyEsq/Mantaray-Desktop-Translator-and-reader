import time
import google.generativeai as genai

from config import CONFIG
from backend.models import TranslationJob, ConversationContext

class LLMHandler:
    """Handles translation and context management via Google AI Studio."""
    
    def __init__(self):
        self.context = ConversationContext(max_history=CONFIG.MAX_HISTORY_LINES)
        
        # Check if the API key was actually set in the .env file
        if not CONFIG.GOOGLE_API_KEY or CONFIG.GOOGLE_API_KEY == "your_google_ai_studio_key_here":
            print("- WARNING: GOOGLE_API_KEY is missing or invalid in your .env file!")
            self.model = None
            return
            
        genai.configure(api_key=CONFIG.GOOGLE_API_KEY)
        
        # Initialize the Gemini 1.5 model and pass our system prompt
        self.model = genai.GenerativeModel(
            model_name=CONFIG.GOOGLE_MODEL,
            system_instruction=CONFIG.SYSTEM_PROMPT
        )
        print(f"- LLM Model '{CONFIG.GOOGLE_MODEL}' initialized successfully.")

    def translate(self, job: TranslationJob) -> TranslationJob:
        """Sends the Japanese text and history to the LLM and updates the job."""
        if not job.raw_japanese:
            return job
            
        if not self.model:
            job.english_translation = "[API Key Missing - Check .env]"
            return job
            
        try:
            # 1. Build the prompt with our running history
            prompt = (
                f"Previous Context:\n{self.context.get_context_string()}\n\n"
                f"Current Line to Translate:\n{job.raw_japanese}"
            )
            
            # 2. Call the API
            response = self.model.generate_content(prompt)
            translation = response.text.strip()
            
            # 3. Save the result to our job pipeline
            job.english_translation = translation
            
            # 4. Update the history with both the JP and EN so the AI 
            # remembers who is talking for the next line
            self.context.add_line(f"JP: {job.raw_japanese} | EN: {translation}")
            
        except Exception as e:
            print(f"- LLM API Error: {e}")
            job.english_translation = "[Translation Error - Check Console]"
            
        return job

# --- STANDALONE TEST FUNCTION ---

def test_llm():
    """Runs a local test of the LLM connection and context memory."""
    print("Initializing LLMHandler...")
    handler = LLMHandler()
    
    if not handler.model:
        print("Aborting test: No API key found.")
        return
        
    # We will feed it exactly what your OCR hallucinated!
    test_text = "そういえば" 
    print(f"\nCreating test job with text: '{test_text}'")
    
    job = TranslationJob(image_bytes=b"", raw_japanese=test_text)
    
    start_time = time.time()
    result_job = handler.translate(job)
    end_time = time.time()
    
    print("-" * 40)
    print(" LLM Pipeline Test Complete!")
    print(f" > Original:    {result_job.raw_japanese}")
    print(f" > Translation: {result_job.english_translation}")
    print(f" > Latency:   {(end_time - start_time) * 1000:.2f} ms")
    print("-" * 40)
    
    # Let's peek at the context memory to make sure it saved!
    print(f"Current Memory Context:\n{handler.context.get_context_string()}")

if __name__ == "__main__":
    test_llm()