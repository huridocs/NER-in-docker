from pydantic import BaseModel

from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from drivers.rest.response_entities.EntityTextResponse import EntityTextResponse
from drivers.rest.response_entities.NamedEntityResponse import NamedEntityResponse
from drivers.rest.response_entities.SegmentResponse import SegmentResponse


class GroupResponse(BaseModel):
    group_name: str
    type: NamedEntityType
    entities: list[EntityTextResponse] = []
    top_score_entity: NamedEntityResponse

    @staticmethod
    def from_entity(entities: list[NamedEntityResponse], entity: NamedEntityResponse) -> "GroupResponse":
        entity_text = EntityTextResponse.from_entity(entities, entity)
        return GroupResponse(group_name=entity.group_name, type=entity.type, entities=[entity_text], top_score_entity=entity)
