from pathlib import Path

from domain.NamedEntity import NamedEntity
from domain.PDFNamedEntity import PDFNamedEntity
from domain.PDFSegment import PDFSegment
from port.PDFToSegmentsRepository import PDFToSegmentsRepository
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase


class NamedEntitiesFromPDFUseCase:
    def __init__(self, pdf_to_segments_repository: PDFToSegmentsRepository):
        self.pdf_to_segments_repository = pdf_to_segments_repository

    def get_entities(self, pdf_path: Path) -> list[PDFNamedEntity]:
        pdf_segments: list[PDFSegment] = self.pdf_to_segments_repository.get_segments(pdf_path)
        entities: list[PDFNamedEntity] = []
        named_entities_from_text_use_case = NamedEntitiesFromTextUseCase()
        for pdf_segment in pdf_segments:
            named_entities: list[NamedEntity] = named_entities_from_text_use_case.get_entities(pdf_segment.text)
            pdf_named_entities = [
                PDFNamedEntity.from_pdf_segment(pdf_segment, named_entity) for named_entity in named_entities
            ]
            entities.extend(pdf_named_entities)
        return entities
