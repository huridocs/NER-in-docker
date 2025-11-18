from pathlib import Path
import os

SRC_PATH = Path(__file__).parent.parent.absolute()
ROOT_PATH = SRC_PATH.parent.absolute()
MODELS_PATH = Path(ROOT_PATH, "models")
DATA_PATH = Path(ROOT_PATH, "data")
TITLES_TYPES = ["title", "section header"]
SEPARATOR = " ||| "
PDF_ANALYSIS_SERVICE_URL = "http://pdf-layout-analysis:5060"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")
