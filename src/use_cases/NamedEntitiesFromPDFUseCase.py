from pathlib import Path

from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from domain.PDFNamedEntity import PDFNamedEntity
from domain.PDFSegment import PDFSegment
from ports.PDFToSegmentsRepository import PDFToSegmentsRepository
from ports.PDFsGroupNameRepository import PDFsGroupNameRepository
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase
from use_cases.ReferenceEntitiesFromPDFUseCase import ReferenceEntitiesFromPDFUseCase


class NamedEntitiesFromPDFUseCase:
    def __init__(
        self,
        pdf_to_segments_repository: PDFToSegmentsRepository,
        pdfs_group_name_repository: PDFsGroupNameRepository,
    ):
        self.pdf_to_segments_repository = pdf_to_segments_repository
        self.pdfs_group_name_repository = pdfs_group_name_repository

    def get_entities(self, pdf_path: Path, fast: bool = False) -> list[PDFNamedEntity]:
        pdf_segments: list[PDFSegment] = self.pdf_to_segments_repository.get_segments(pdf_path, fast)
        reference_destinations_groups = self.pdfs_group_name_repository.get_reference_destinations()

        entities: list[PDFNamedEntity] = []
        named_entities_from_text_use_case = NamedEntitiesFromTextUseCase()
        reference_entities_from_pdf_use_case = ReferenceEntitiesFromPDFUseCase(reference_destinations_groups)
        for pdf_segment in pdf_segments:
            named_entities: list[NamedEntity] = named_entities_from_text_use_case.get_entities(pdf_segment.text)
            pdf_named_entities = [
                PDFNamedEntity.from_pdf_segment(pdf_segment, named_entity) for named_entity in named_entities
            ]
            pdf_named_entities.extend(reference_entities_from_pdf_use_case.get_entities(pdf_segment))
            entities.extend(pdf_named_entities)
        return entities
