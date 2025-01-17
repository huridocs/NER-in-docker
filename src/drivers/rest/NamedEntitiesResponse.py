from pydantic import BaseModel

from domain.NamedEntityGroup import NamedEntityGroup
from drivers.rest.NamedEntityResponse import NamedEntityResponse
from drivers.rest.GroupResponse import GroupResponse


class NamedEntitiesResponse(BaseModel):
    entities: list[NamedEntityResponse]
    groups: list[GroupResponse]

    @staticmethod
    def from_named_entity_groups(named_entity_groups: list[NamedEntityGroup]):
        named_entity_responses = [
            NamedEntityResponse.from_named_entity(entity, group.name)
            for group in named_entity_groups
            for entity in group.named_entities
        ]
        named_entity_responses = sorted(named_entity_responses, key=lambda x: x.character_start)
        group_responses = [
            GroupResponse.from_named_entity_group(group, named_entity_responses) for group in named_entity_groups
        ]
        return NamedEntitiesResponse(entities=named_entity_responses, groups=group_responses)
