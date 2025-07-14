import sys
import tempfile
import uuid
from pathlib import Path
from fastapi import FastAPI, Form, UploadFile, File
from adapters.PDFLayoutAnalysisRepository import PDFLayoutAnalysisRepository
from adapters.SQLiteEntitiesStoreRepository import SQLiteEntitiesStoreRepository
from domain.NamedEntityType import NamedEntityType
from domain.Segment import Segment
from drivers.rest.catch_exceptions import catch_exceptions
from drivers.rest.response_entities.NamedEntitiesResponse import NamedEntitiesResponse
from use_cases.GroupNamedEntitiesUseCase import GroupNamedEntitiesUseCase
from use_cases.NamedEntitiesUseCase import NamedEntitiesUseCase
from use_cases.ReferencesUseCase import ReferencesUseCase
import logging

logging.basicConfig(level=logging.INFO)

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
async def get_named_entities(
    namespace: str = Form(None),
    identifier: str = Form(None),
    text: str = Form(None),
    file: UploadFile = File(None),
    fast: bool = Form(False),
):
    if file:
        pdf_path = pdf_content_to_pdf_path(await file.read(), file.filename)
        segments = PDFLayoutAnalysisRepository().get_segments(pdf_path, fast)
    else:
        segments = [Segment.from_text(text=text if text else "", source_id=identifier)]

    entities_from_db = SQLiteEntitiesStoreRepository(namespace).get_entities() if namespace else list()

    named_entities = NamedEntitiesUseCase().get_entities_from_segments(segments)
    named_entities += ReferencesUseCase(entities_from_db).get_entities_from_segments(segments)
    named_entities_groups = GroupNamedEntitiesUseCase(entities_from_db).group(named_entities)

    if namespace:
        SQLiteEntitiesStoreRepository(namespace).save_entities(named_entities)

    return NamedEntitiesResponse.from_groups(named_entities_groups)


@app.post("/delete_namespace")
@catch_exceptions
async def delete_namespace(namespace: str = Form(None)):
    SQLiteEntitiesStoreRepository(namespace).delete_database()
    return "Deleted"
