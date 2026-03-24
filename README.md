
# Desktop AI translator for reading literature

A high-performance, modular screen translation overlay designed for reading Japanese Visual Novels, Light Novels, and E-books in a desktop environment. This tool captures a user-defined screen region, extracts complex Japanese text using a specialized OCR model, and translates it into natural English using Large Language Models (LLMs), displaying the result in a seamless, frameless UI overlay. Other languages are also supported.

---

## Core Features

- **In-Memory Screen Capture:** Utilizes `mss` for lightning-fast, low-overhead region capture, bypassing slow disk I/O so your system resources remain focused on your game or reading app.
- **Literature-Optimized Japanese OCR:** Integrates `manga-ocr`, a model specifically trained to handle complex visual novel fonts, vertical/horizontal rendering, and noisy backgrounds where standard OCRs fail.
- **Context-Aware AI Translation:** Connects to LLM APIs to provide context-aware translations. By remembering the last several lines of dialogue, it accurately resolves Japanese pronouns and implicit subjects common in literature.
- **Native Wayland/X11 Overlay:** Built with `PySide6` (Qt) to provide a transparent, click-through, and frameless window overlay that works cleanly on modern Linux desktop environments.

---

## Project Architecture

The application is strictly divided between the frontend presentation layer and the backend business logic to ensure maintainability and easy swapping of components.

```text
vn_translator/
├── main.py                 # Application entry point; initializes Qt loop and threads
├── config.py               # Centralized configuration (API keys, UI settings, target monitor)
├── requirements.txt        # Python package dependencies
├── README.md               # Project documentation
│
├── backend/                # Business Logic & Data Processing
│   ├── capture_handler.py  # Manages mss bounding box definitions and in-memory screenshots
│   ├── ocr_handler.py      # Interfaces with manga-ocr to extract Japanese text strings
│   ├── llm_handler.py      # Manages dialogue history and API calls to the translation LLM
│   └── models.py           # Dataclasses defining data flow (ScreenRegion, TranslationJob)
│
└── frontend/               # Presentation Layer (PySide6)
    ├── main_menu.py        # Control panel for adjusting settings and API keys
    ├── overlay.py          # The frameless, transparent window rendering the English text
    └── selector.py         # The interactive tool for drawing the capture bounding box
```

---

## Prerequisites

- Python 3.10 or higher
- A Linux environment (Tested on Fedora, XWayland compatible, maybe this could work on WSL)
- A Google AI Studio API Key (or a local Ollama instance for offline translation)

---

## Installation

*(Note: A standalone Flatpak release is planned for the future to simplify Linux installation. For now, please use the following source-build instructions.)*

1. **Clone the repository:**
   `git clone https://github.com/yourusername/desktop_ai_reader.git`
   `cd desktop_ai_reader`

2. **Create a virtual environment:**
   `python -m venv venv`
   `source venv/bin/activate`

3. **Install dependencies:**
   `pip install -r requirements.txt`

   **Note on first run:** The `manga-ocr` library will automatically download its pre-trained model weights upon the first execution.

---

## Usage

1. Configure your API key and preferred translation model inside `config.py` or via the main menu UI.
2. Run the application:
   `python main.py`
3. Use the **Selector** tool to draw a bounding box precisely over the text area of your visual novel or e-book reader.
4. Position the **Overlay** window where you want the English translation to appear on your screen.
5. The system will automatically monitor the boxed region and update the overlay whenever new text is displayed.

---

## Future Roadmap

- Package and distribute as a Flatpak for universal Linux compatibility.
- Implement an interactive history log to request detailed cultural explanations for specific translated lines (slang, idioms, etc.).
- Add support for local offline LLMs via Ollama integration for fully disconnected reading.
