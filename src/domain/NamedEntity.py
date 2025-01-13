from pydantic import BaseModel

from domain.NamedEntityType import NamedEntityType


class NamedEntity(BaseModel):
    type: NamedEntityType
    text: str
    normalized_text: str = ""
    start: int
    end: int
    context: str = "default"


if __name__ == '__main__':
    entity = NamedEntity(**{"type":"PERSON","text":"John Doe","start":0,"end":7,"context":"default"})
    print(entity.model_dump())