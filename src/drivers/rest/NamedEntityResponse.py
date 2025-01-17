from pydantic import BaseModel
from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType


class NamedEntityResponse(BaseModel):
    group_name: str
    type: NamedEntityType
    text: str
    character_start: int
    character_end: int

    @staticmethod
    def from_named_entity(named_entity: NamedEntity, group_name: str):
        return NamedEntityResponse(
            group_name=group_name,
            type=named_entity.type,
            text=named_entity.text,
            character_start=named_entity.character_start,
            character_end=named_entity.character_end,
        )
