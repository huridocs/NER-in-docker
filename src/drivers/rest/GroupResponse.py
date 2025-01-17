from pydantic import BaseModel

from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from drivers.rest.NamedEntityResponse import NamedEntityResponse


class GroupResponse(BaseModel):
    group_name: str
    type: NamedEntityType
    entities_ids: list[int]
    entities_text: list[str]

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
            type=entities[entity_indexes[0]].type if entity_indexes else NamedEntityType.PERSON,
            entities_ids=entity_indexes,
            entities_text=entity_texts,
        )
