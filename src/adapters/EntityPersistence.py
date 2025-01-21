from pydantic import BaseModel
from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType


class EntityPersistence(BaseModel):
    group_name: str
    entity_type: str
    entity_text: str

    def to_named_entity(self) -> NamedEntity:
        entity_type = NamedEntityType(self.entity_type)
        return NamedEntity(text=self.entity_text, type=entity_type).get_with_normalize_entity_text()

    @staticmethod
    def from_row(row):
        (_, group_name, entity_type, entity_text) = row
        return EntityPersistence(group_name=group_name, entity_type=entity_type, entity_text=entity_text)
