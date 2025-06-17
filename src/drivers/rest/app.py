import sys
import tempfile
import uuid
from pathlib import Path
from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from adapters.PDFLayoutAnalysisRepository import PDFLayoutAnalysisRepository
from adapters.SQLitePDFsGroupNameRepository import SQLiteGroupsStoreRepository
from domain.NamedEntity import NamedEntity
from drivers.rest.catch_exceptions import catch_exceptions
from drivers.rest.response_entities.NamedEntitiesResponse import NamedEntitiesResponse
from use_cases.NamedEntitiesFromPDFUseCase import NamedEntitiesFromPDFUseCase
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase
from use_cases.NamedEntityMergerUseCase import NamedEntityMergerUseCase
from use_cases.PDFNamedEntityMergerUseCase import PDFNamedEntityMergerUseCase


app = FastAPI()


def pdf_content_to_pdf_path(file_content, file_name: str = None) -> Path:
    file_name = file_name if file_name else str(uuid.uuid1()) + ".pdf"
    pdf_path = Path(tempfile.gettempdir()) / file_name
    pdf_path.write_bytes(file_content)
    return pdf_path


@app.get("/")
async def info():
    return sys.version


@app.post("/")
@catch_exceptions
async def get_named_entities(text: str = Form(None), fast: bool = Form(False), file: UploadFile = File(None)):
    if not file:
        named_entities: list[NamedEntity] = NamedEntitiesFromTextUseCase().get_entities(text)
        named_entity_groups = NamedEntityMergerUseCase().merge(named_entities)
        return NamedEntitiesResponse.from_named_entity_groups(named_entity_groups)

    pdf_layout_analysis_repository = PDFLayoutAnalysisRepository()
    pdfs_group_names_repository = SQLiteGroupsStoreRepository()
    named_entities_from_pdf_use_case = NamedEntitiesFromPDFUseCase(
        pdf_layout_analysis_repository, pdfs_group_names_repository
    )

    pdf_path = pdf_content_to_pdf_path(await file.read(), file.filename)
    pdf_named_entities = named_entities_from_pdf_use_case.get_entities(pdf_path, fast)
    named_entity_groups = PDFNamedEntityMergerUseCase(pdfs_group_names_repository).merge(pdf_named_entities)
    named_entity_groups.extend(named_entities_from_pdf_use_case.get_reference_groups())

    return NamedEntitiesResponse.from_named_entity_groups(named_entity_groups)
