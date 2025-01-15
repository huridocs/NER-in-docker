from pathlib import Path

SRC_PATH = Path(__file__).parent.absolute()
ROOT_PATH = Path(__file__).parent.parent.absolute()
MODELS_PATH = Path(ROOT_PATH, "models")
PDF_ANALYSIS_SERVICE_URL = "http://worker-pdf-layout-gpu:5060"
