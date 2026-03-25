import os
import google.generativeai as genai
from huggingface_hub import hf_hub_download

from backend.models import TranslationJob
from config import CONFIG

class LLMHandler:
    """A hybrid handler that routes translation to either Google Gemini or a Local Model."""
    
    def __init__(self):
        self.engine = getattr(CONFIG, 'ACTIVE_ENGINE', 'google').lower()
        
        if self.engine == "google":
            self._init_google()
        else:
            self._init_local()

    def _init_google(self):
        print("Initializing Google Gemini Engine...")
        genai.configure(api_key=CONFIG.GOOGLE_API_KEY)
        
        # Inject the target language into the prompt
        dynamic_prompt = CONFIG.SYSTEM_PROMPT.format(target_lang=CONFIG.TARGET_LANGUAGE)
        
        self.model = genai.GenerativeModel(
            model_name=CONFIG.GOOGLE_MODEL,
            system_instruction=dynamic_prompt
        )
        print(" Google Gemini Engine Ready!")

    def _init_local(self):
        print("Initializing Offline HY-MT 1.5 Engine...")
        from llama_cpp import Llama # Import here so it doesn't crash if someone only uses Google
        
        # Using the incredibly fast 1.8B version for offline translation
        repo_id = "tencent/HY-MT1.5-1.8B-GGUF" # This is a model by tencent, yes, THAT tencent.
        filename = "HY-MT1.5-1.8B-Q4_K_M.gguf" 
        
        model_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, filename)

        if not os.path.exists(model_path):
            print(f"Downloading HY-MT 1.5 Local Model. This might take a minute...")
            hf_hub_download(
                repo_id=repo_id, 
                filename=filename, 
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )

        print("Loading HY-MT 1.5 into memory...")
        self.local_model = Llama(
            model_path=model_path,
            n_ctx=2048, 
            n_gpu_layers=-1 if getattr(CONFIG, 'USE_GPU', False) else 0,
            chat_format="chatml", 
            verbose=False 
        )
        print(" Offline Translation Engine Ready!")

    def translate(self, job: TranslationJob) -> TranslationJob:
        if not job.raw_japanese:
            return job

        if self.engine == "google":
            return self._translate_google(job)
        else:
            return self._translate_local(job)

    def _translate_google(self, job: TranslationJob) -> TranslationJob:
        try:
            response = self.model.generate_content(job.raw_japanese)
            job.english_translation = response.text.strip()
        except Exception as e:
            print(f" Gemini API Error: {e}")
            job.english_translation = "[Cloud Translation Failed]"
        return job

    def _translate_local(self, job: TranslationJob) -> TranslationJob:
        try:
            target_lang = getattr(CONFIG, 'TARGET_LANGUAGE', 'English')
            
            # 1. Fetch the exact same Expert Persona prompt used by Gemini
            system_instruction = CONFIG.SYSTEM_PROMPT.format(target_lang=target_lang)
            
            # 2. Pass it to the local model using the ChatML 'system' role
            messages = [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": job.raw_japanese}
            ]

            # 3. Ask the model to generate
            response = self.local_model.create_chat_completion(
                messages=messages,
                max_tokens=512, 
                temperature=0.1, # Bumped slightly to allow the AI to "guess" missing context
            )

            english_text = response['choices'][0]['message']['content'].strip()
            
            # --- THE "DO YOUR JOB" FILTER ---
            # We keep the filter just in case the Expert Persona fails and it still complains
            sass_keywords = ["makes no sense", "empty string", "cannot be translated", "invalid"]
            if any(keyword in english_text.lower() for keyword in sass_keywords):
                job.english_translation = "[Awaiting clearer text...]"
            elif english_text == job.raw_japanese:
                job.english_translation = "[AI Echoed Text - Prompt Failed]"
            else:
                job.english_translation = english_text

        except Exception as e:
            print(f"❌ Local Translation Error: {e}")
            job.english_translation = "[Offline Translation Failed]"

        return job