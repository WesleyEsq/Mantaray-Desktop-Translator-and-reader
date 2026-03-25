import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from the .env file into os.environ
load_dotenv()

@dataclass
class AppConfig:
    """Centralized configuration for the Desktop AI Reader."""
    # This enables or disables the debug mode
    DEBUG_MODE: bool = True       
    # API & LLM Settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # Engine Selection: "google" or "ollama"
    ACTIVE_ENGINE: str = "google"
    # Target Language
    TARGET_LANGUAGE: str = "English"
    
    # Model Names (Gemini gemini-2.5-flash-lite is currently the fastest/cheapest for API translation)
    GOOGLE_MODEL: str = "gemini-2.5-flash-lite" 
    OLLAMA_MODEL: str = "gemma2:9b"
    
    # UI Overlay Settings
    OVERLAY_FONT_FAMILY: str = "Segoe UI" # Good, readable default
    OVERLAY_FONT_SIZE: int = 28
    OVERLAY_TEXT_COLOR: str = "#FFFFFF"   # White text
    OVERLAY_BG_COLOR: str = "rgba(0, 0, 0, 180)" # Semi-transparent black background
    
    # Translation Logic
    MAX_HISTORY_LINES: int = 5
    
    # The default system prompt given to the LLM
    SYSTEM_PROMPT: str = (
        "You are an expert Japanese to {target_lang} translator specializing in visual novels and literature. "
        "Translate the following Japanese text into natural, conversational {target_lang}. "
        "Use the provided conversation history to correctly infer missing pronouns (I, you, he, she) "
        "and contextual tone. Output ONLY the {target_lang} translation, without any notes or formatting."
    )
    
    # Configuration for the Chat menu window
    OVERLAY_FONT_FAMILY: str = "Segoe UI"
    OVERLAY_FONT_SIZE: int = 28
    OVERLAY_TEXT_COLOR: str = "#FFFFFF"   
    OVERLAY_BG_COLOR: str = "rgba(0, 0, 0, 180)"
    
    # --- ADD THIS: Hardware Acceleration ---
    USE_GPU: bool = True # Set to True if you have CUDA/NVIDIA installed
    ACTIVE_ENGINE = "local"

# Instantiate a global config object to be imported by other modules
CONFIG = AppConfig()