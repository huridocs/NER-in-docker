from pydantic import BaseModel

from ner_in_docker.domain.NamedEntityGroup import NamedEntityGroup
from ner_in_docker.domain.NamedEntityType import NamedEntityType
from ner_in_docker.drivers.rest.response_entities.EntityTextResponse import EntityTextResponse
from ner_in_docker.drivers.rest.response_entities.NamedEntityResponse import NamedEntityResponse


class GroupResponse(BaseModel):
    group_name: str
    type: NamedEntityType
    entities: list[EntityTextResponse] = []
    top_relevance_entity: NamedEntityResponse

    @staticmethod
    def from_entity(
        entities: list[NamedEntityResponse], entity: NamedEntityResponse, group: NamedEntityGroup
    ) -> "GroupResponse":
        entity_text = EntityTextResponse.from_entity(entities, entity)
        if group.top_relevance_entity and group.top_relevance_entity.relevance_percentage > entity.relevance_percentage:
            top_relevance_entity = NamedEntityResponse.from_named_entity(group.top_relevance_entity)
        else:
            top_relevance_entity = entity

        return GroupResponse(
            group_name=entity.group_name, type=entity.type, entities=[entity_text], top_relevance_entity=top_relevance_entity
        )
