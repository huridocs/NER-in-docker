from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup


class NamedEntityMergerUseCase:
    def __init__(self, named_entities: list[NamedEntity]):
        self.named_entities = named_entities

    def merge(self) -> list[NamedEntityGroup]:
        pass
