from pydantic import BaseModel
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.NamedEntityType import NamedEntityType
from ner_in_docker.drivers.rest.response_entities.SegmentResponse import SegmentResponse


class NamedEntityResponse(BaseModel):
    group_name: str
    type: NamedEntityType
    text: str
    character_start: int
    character_end: int
    relevance_percentage: int = 0
    segment: SegmentResponse
    source_id: str

    @staticmethod
    def from_named_entity(named_entity: NamedEntity):
        return NamedEntityResponse(
            group_name=named_entity.group_name,
            type=named_entity.type,
            text=named_entity.text,
            character_start=named_entity.character_start,
            character_end=named_entity.character_end,
            relevance_percentage=named_entity.relevance_percentage,
            segment=SegmentResponse.from_named_entity(named_entity),
            source_id=named_entity.segment.source_id,
        )
