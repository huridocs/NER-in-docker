from domain.NamedEntities import NamedEntitiesGrouped


class NamedEntityMergerUseCase:
    def __init__(self, named_entities: NamedEntitiesGrouped):
        self.named_entities = named_entities

    def merge(self) -> NamedEntitiesGrouped:
        pass