from pydantic import BaseModel

from domain.NamedEntityType import NamedEntityType


class NamedEntity(BaseModel):
    type: NamedEntityType
    text: str
    normalized_text: str = ""
    start: int = 0
    end: int = 0
    context: str = "default"
