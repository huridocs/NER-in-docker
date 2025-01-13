from pydantic import BaseModel

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType


class NamedEntityGroup(BaseModel):
    type: NamedEntityType
    text: str
    named_entities: list[NamedEntity] = list()
    context: str = "default"

    def belongs_to_group(self, named_entity: NamedEntity) -> bool:
        if self.type == named_entity.type and self.text == named_entity.text:
            return True

        normalized_entity = named_entity.normalize_text()
        for group_named_entities in self.named_entities:
            if group_named_entities.normalized_text == normalized_entity.normalized_text:
                return True

        return False

    def add_named_entity(self, named_entity: NamedEntity):
        self.named_entities.append(named_entity.normalize_text())
