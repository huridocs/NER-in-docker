from configuration import TITLES_TYPES
from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity
from domain.PDFSegment import PDFSegment


class ReferenceEntitiesFromPDFUseCase:
    def __init__(self, reference_destinations_groups: list[NamedEntityGroup] = None):
        self.reference_destinations_groups = reference_destinations_groups if reference_destinations_groups else []

    def get_entities(self, pdf_segment: PDFSegment) -> list[PDFNamedEntity]:
        if str(pdf_segment.type).lower() in TITLES_TYPES:
            return []

        entities: list[PDFNamedEntity] = list()
        for group in self.reference_destinations_groups:
            positions = group.get_references_in_text(pdf_segment.text)
            for character_start, character_end in positions:
                entity = NamedEntity(
                    type=NamedEntityType.REFERENCE_POINTER,
                    text=pdf_segment.text[character_start:character_end],
                    character_start=character_start,
                    character_end=character_end,
                )
                entities.append(PDFNamedEntity.from_pdf_segment(entity, pdf_segment, group.name))

        return entities
