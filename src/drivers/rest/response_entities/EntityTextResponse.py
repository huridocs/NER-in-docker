from pydantic import BaseModel

from drivers.rest.response_entities.NamedEntityResponse import NamedEntityResponse


class EntityTextResponse(BaseModel):
    index: int
    text: str

    @staticmethod
    def from_entity(entities: list[NamedEntityResponse], entity: NamedEntityResponse) -> "EntityTextResponse":
        index = entities.index(entity)
        return EntityTextResponse(index=index, text=entity.text)
