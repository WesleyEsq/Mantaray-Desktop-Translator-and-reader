from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ScreenRegion:
    """Defines the bounding box coordinates for the screen capture."""
    x: int
    y: int
    width: int
    height: int

    @property
    def mss_dict(self) -> dict:
        """
        Helper property that converts the standard x/y coordinates into 
        the specific dictionary format required by the 'mss' library.
        """
        return {
            "top": self.y, 
            "left": self.x, 
            "width": self.width, 
            "height": self.height
        }


@dataclass
class TranslationJob:
    """
    Represents a single translation pipeline cycle. 
    Flows from Capture -> OCR -> LLM -> UI.
    """
    image_bytes: bytes
    raw_japanese: Optional[str] = None
    english_translation: Optional[str] = None


@dataclass
class ConversationContext:
    """
    Maintains the recent dialogue history to provide context to the LLM,
    allowing it to accurately resolve omitted pronouns and subjects.
    """
    history: List[str] = field(default_factory=list)
    max_history: int = 5

    def add_line(self, text: str) -> None:
        """Adds a new line to the history, dropping the oldest if at capacity."""
        if not text:
            return
            
        self.history.append(text)
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
    def get_context_string(self) -> str:
        """Formats the current history into a single string for the LLM prompt."""
        if not self.history:
            return "No previous context."
        return "\n".join(self.history)