from pathlib import Path

from configuration import TITLES_TYPES
from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity
from domain.PDFSegment import PDFSegment
from ports.PDFToSegmentsRepository import PDFToSegmentsRepository
from ports.GroupsStoreRepository import GroupsStoreRepository
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase
from use_cases.ReferenceEntitiesFromPDFUseCase import ReferenceEntitiesFromPDFUseCase


class NamedEntitiesFromPDFUseCase:
    def __init__(
        self,
        pdf_to_segments_repository: PDFToSegmentsRepository,
        groups_store_repository: GroupsStoreRepository,
    ):
        self.pdf_to_segments_repository = pdf_to_segments_repository
        self.pdfs_group_name_repository = groups_store_repository
        self.pdf_segments = list()
        self.reference_destinations_groups: dict[str, NamedEntityGroup] = dict()

    def get_entities(self, pdf_path: Path, fast: bool = False) -> list[PDFNamedEntity]:
        self.load_pdf_segments(pdf_path, fast)
        entities: list[PDFNamedEntity] = []
        named_entities_from_text_use_case = NamedEntitiesFromTextUseCase()
        for pdf_segment in self.pdf_segments:
            named_entities: list[NamedEntity] = named_entities_from_text_use_case.get_entities(pdf_segment.text)
            pdf_named_entities = [
                PDFNamedEntity.from_pdf_segment(named_entity, pdf_segment) for named_entity in named_entities
            ]
            entities.extend(pdf_named_entities)
        return entities

    def get_reference_groups(self, pdf_path: Path = None, fast: bool = False) -> list[NamedEntityGroup]:
        self.load_pdf_segments(pdf_path, fast)
        self.load_reference_destinations_groups()

        if not self.reference_destinations_groups:
            return []

        reference_destinations_groups_list = list(self.reference_destinations_groups.values())
        reference_entities_from_pdf_use_case = ReferenceEntitiesFromPDFUseCase(reference_destinations_groups_list)
        reference_entities: list[PDFNamedEntity] = list()
        for pdf_segment in self.pdf_segments:
            reference_entities.extend(reference_entities_from_pdf_use_case.get_entities(pdf_segment))

        for reference_entity in reference_entities:
            self.reference_destinations_groups[reference_entity.group_name].named_entities.append(reference_entity)

        return [group for group in self.reference_destinations_groups.values() if group.named_entities]

    def load_pdf_segments(self, pdf_path: Path = None, fast: bool = False):
        if self.pdf_segments or not pdf_path:
            return

        self.pdf_segments: list[PDFSegment] = self.pdf_to_segments_repository.get_segments(pdf_path, fast)

    def load_reference_destinations_groups(self):
        if self.reference_destinations_groups:
            return

        new_groups_destinations = list()
        for pdf_segment in self.pdf_segments:
            if str(pdf_segment.type).lower() not in TITLES_TYPES:
                continue

            new_groups_destinations.append(
                NamedEntityGroup(
                    type=NamedEntityType.REFERENCE_DESTINATION,
                    name=pdf_segment.text,
                    pdf_segment=pdf_segment,
                )
            )

        reference_destinations_groups_list = self.pdfs_group_name_repository.update_reference_destinations(
            new_groups_destinations
        )
        for group in reference_destinations_groups_list:
            self.reference_destinations_groups[group.name] = group
