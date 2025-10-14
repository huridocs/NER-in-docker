from pathlib import Path

SRC_PATH = Path(__file__).parent.absolute()
ROOT_PATH = Path(__file__).parent.parent.absolute()
MODELS_PATH = Path(ROOT_PATH, "models")
TITLES_TYPES = ["title", "section header"]
SEPARATOR = " ||| "
PDF_ANALYSIS_SERVICE_URL = "http://pdf-layout-analysis:5060"
