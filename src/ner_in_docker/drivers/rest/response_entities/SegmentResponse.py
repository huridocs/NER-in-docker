from pydantic import BaseModel

from ner_in_docker.domain.NamedEntityGroup import NamedEntityGroup
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.drivers.rest.response_entities.BoundingBoxResponse import BoundingBoxResponse


class SegmentResponse(BaseModel):
    text: str
    page_number: int
    segment_number: int
    character_start: int
    character_end: int
    bounding_box: BoundingBoxResponse
    pdf_name: str = ""

    @staticmethod
    def from_named_entity(named_entity: NamedEntity) -> "SegmentResponse":
        return SegmentResponse(
            text=named_entity.segment.text,
            page_number=named_entity.segment.page_number,
            segment_number=named_entity.segment.segment_number,
            character_start=named_entity.character_start,
            character_end=named_entity.character_end,
            bounding_box=BoundingBoxResponse.from_rectangle(named_entity.segment.bounding_box),
            pdf_name=named_entity.segment.source_id,
        )
