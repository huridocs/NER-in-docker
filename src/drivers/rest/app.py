import sys
import tempfile
import uuid
from pathlib import Path
from fastapi import FastAPI, Form, UploadFile, File
from adapters.PDFLayoutAnalysisRepository import PDFLayoutAnalysisRepository
from adapters.PersistencePDFsGroupNameRepository import SQLitePDFsGroupNameRepository
from domain.NamedEntity import NamedEntity
from drivers.rest.catch_exceptions import catch_exceptions
from drivers.rest.response_entities.NamedEntitiesResponse import NamedEntitiesResponse
from use_cases.NamedEntitiesFromPDFUseCase import NamedEntitiesFromPDFUseCase
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase
from use_cases.NamedEntityMergerUseCase import NamedEntityMergerUseCase
from use_cases.PDFsNamedEntityMergerUseCase import PDFNamedEntityMergerUseCase


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
@catch_exceptions
async def get_named_entities(text: str = Form(None), file: UploadFile = File(None)):
    if not file:
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase().get_entities(text)
        named_entity_groups = NamedEntityMergerUseCase().merge(entities)
        return NamedEntitiesResponse.from_named_entity_groups(named_entity_groups)

    pdf_layout_analysis_repository = PDFLayoutAnalysisRepository()
    pdf_path = pdf_content_to_pdf_path(file.file.read())
    entities = NamedEntitiesFromPDFUseCase(pdf_layout_analysis_repository).get_entities(pdf_path)

    pdfs_group_names_repository = SQLitePDFsGroupNameRepository()
    named_entity_groups = PDFNamedEntityMergerUseCase(pdfs_group_names_repository).merge(entities)
    return NamedEntitiesResponse.from_named_entity_groups(named_entity_groups)
