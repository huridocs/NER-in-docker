from pydantic import BaseModel
from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType


class GroupPersistence(BaseModel):
    name: str
    type: str
    entities_names: list[str]

    def to_named_entity_group(self):
        entity_type = NamedEntityType(self.type)
        entities = [
            NamedEntity(text=entity_name, type=entity_type).normalize_entity_text() for entity_name in self.entities_names
        ]
        return NamedEntityGroup(name=self.name, type=entity_type, named_entities=entities)
