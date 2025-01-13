from abc import abstractmethod, ABC

from domain.NamedEntities import NamedEntitiesGrouped


class NameEntitiesPersistenceRepository(ABC):
    @abstractmethod
    def save(self, named_entities: NamedEntitiesGrouped):
        pass

    def get(self) -> NamedEntitiesGrouped:
        pass
