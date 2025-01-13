from pydantic import BaseModel

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType


class NamedEntityGroup(BaseModel):
    type: NamedEntityType
    text: str
    named_entities: list[NamedEntity] = list()
    context: str = "default"
