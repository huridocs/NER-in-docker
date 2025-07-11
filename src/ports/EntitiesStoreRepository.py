from abc import abstractmethod, ABC

from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup


class EntitiesStoreRepository(ABC):

    @abstractmethod
    def get_entities(self) -> list[NamedEntity]:
        pass

    @abstractmethod
    def save_entities(self, named_entities: list[NamedEntity]) -> None:
        pass
