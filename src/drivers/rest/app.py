import sys
import tempfile
import uuid
from pathlib import Path
from fastapi import FastAPI, Form, UploadFile, File
from adapters.PDFLayoutAnalysisRepository import PDFLayoutAnalysisRepository
from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from drivers.rest.NamedEntitiesResponse import NamedEntitiesResponse
from drivers.rest.PDFNamedEntitiesResponse import PDFNamedEntitiesResponse
from use_cases.NamedEntitiesFromPDFUseCase import NamedEntitiesFromPDFUseCase
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase
from use_cases.NamedEntityMergerUseCase import NamedEntityMergerUseCase


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
    entities: list[NamedEntity] = NamedEntitiesFromTextUseCase().get_entities(text)
    named_entity_groups: list[NamedEntityGroup] = NamedEntityMergerUseCase().merge(entities)
    return NamedEntitiesResponse.from_named_entity_groups(named_entity_groups)


@app.post("/pdf")
async def get_pdf_named_entities(file: UploadFile = File(...)):
    pdf_path: Path = pdf_content_to_pdf_path(file.file.read())
    pdf_layout_analysis_repository = PDFLayoutAnalysisRepository()
    entities = [entity for entity in NamedEntitiesFromPDFUseCase(pdf_layout_analysis_repository).get_entities(pdf_path)]
    named_entity_groups: list[NamedEntityGroup] = NamedEntityMergerUseCase().merge(entities)
    return PDFNamedEntitiesResponse.from_named_entity_groups(named_entity_groups)
