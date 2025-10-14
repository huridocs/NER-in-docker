from pydantic import BaseModel

from ner_in_docker.domain.BoundingBox import BoundingBox
from ner_in_docker.domain.NamedEntityGroup import NamedEntityGroup
from ner_in_docker.domain.NamedEntity import NamedEntity


class SegmentResponse(BaseModel):
    text: str
    page_number: int
    segment_number: int
    character_start: int
    character_end: int
    bounding_box: BoundingBox
    pdf_name: str = ""

    @staticmethod
    def from_named_entity(named_entity: NamedEntity) -> "SegmentResponse":
        return SegmentResponse(
            text=named_entity.segment.text,
            page_number=named_entity.segment.page_number,
            segment_number=named_entity.segment.segment_number,
            character_start=named_entity.character_start,
            character_end=named_entity.character_end,
            bounding_box=named_entity.segment.bounding_box,
            pdf_name=named_entity.segment.source_id,
        )

    @staticmethod
    def from_named_entity_group(named_entity_group: NamedEntityGroup) -> "SegmentResponse | None":
        if not named_entity_group.segment:
            return None

        if named_entity_group.name in named_entity_group.segment.text:
            character_start = named_entity_group.segment.text.index(named_entity_group.name)
            character_end = character_start + len(named_entity_group.name)
        else:
            character_start = 0
            character_end = 0

        return SegmentResponse(
            text=named_entity_group.segment.text,
            page_number=named_entity_group.segment.page_number,
            segment_number=named_entity_group.segment.segment_number,
            character_start=character_start,
            character_end=character_end,
            bounding_box=named_entity_group.segment.bounding_box,
            pdf_name=named_entity_group.segment.source_id,
        )
