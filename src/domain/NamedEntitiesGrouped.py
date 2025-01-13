from pydantic import BaseModel

from domain.NamedEntity import NamedEntity


class NamedEntitiesGrouped(BaseModel):
    named_entities_grouped: dict[NamedEntity, NamedEntity] = dict()


if __name__ == '__main__':
    a = NamedEntitiesGrouped()