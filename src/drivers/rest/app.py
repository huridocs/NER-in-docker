import json
import sys
import tempfile
import uuid
from pathlib import Path
from fastapi import FastAPI, Form, UploadFile, File
from adapters.PDFLayoutAnalysisRepository import PDFLayoutAnalysisRepository
from use_cases.NamedEntitiesFromPDFUseCase import NamedEntitiesFromPDFUseCase
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase


def get_file_path(file_name, extension) -> Path:
    return Path(tempfile.gettempdir(), file_name + "." + extension)


def pdf_content_to_pdf_path(file_content) -> Path:
    file_id = str(uuid.uuid1())
    pdf_path = Path(get_file_path(file_id, "pdf"))
    pdf_path.write_bytes(file_content)
    return pdf_path


app = FastAPI()


@app.get("/info")
async def info():
    return sys.version


@app.post("/")
async def get_named_entities(text: str = Form("")):
    entities = NamedEntitiesFromTextUseCase().get_entities(text)
    return entities


@app.post("/pdf")
async def get_pdf_named_entities(file: UploadFile = File(...), save_locally: bool = Form(False)):
    pdf_layout_analysis_repository = PDFLayoutAnalysisRepository()
    pdf_path: Path = pdf_content_to_pdf_path(file.file.read())
    entities = [entity for entity in NamedEntitiesFromPDFUseCase(pdf_layout_analysis_repository).get_entities(pdf_path)]

    if save_locally:
        entities_json = [entity.model_dump() for entity in entities]
        save_path: Path = Path("/app/data", pdf_path.name.replace(".pdf", ".json"))
        save_path.write_text(json.dumps(entities_json, indent=2))

    return entities
