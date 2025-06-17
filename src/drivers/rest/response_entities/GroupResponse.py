from pydantic import BaseModel

from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from drivers.rest.response_entities.NamedEntityResponse import NamedEntityResponse
from drivers.rest.response_entities.SegmentResponse import SegmentResponse


class GroupResponse(BaseModel):
    group_name: str
    type: NamedEntityType
    entities_ids: list[int]
    entities_text: list[str]
    segment: SegmentResponse | None = None

    @staticmethod
    def from_named_entity_group(named_entity_group: NamedEntityGroup, entities: list[NamedEntityResponse]):
        entity_indexes = []
        entity_texts = []

        for index, entity in enumerate(entities):
            if named_entity_group.name == entity.group_name:
                entity_indexes.append(index)
                entity_texts.append(entity.text)

        return GroupResponse(
            group_name=named_entity_group.name,
            type=named_entity_group.type,
            entities_ids=entity_indexes,
            entities_text=entity_texts,
            segment=SegmentResponse.from_named_entity_group(named_entity_group) if named_entity_group.pdf_segment else None,
        )
