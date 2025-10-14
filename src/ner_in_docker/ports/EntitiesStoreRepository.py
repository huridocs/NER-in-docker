from abc import abstractmethod, ABC

from ner_in_docker.domain.NamedEntity import NamedEntity


class EntitiesStoreRepository(ABC):

    @abstractmethod
    def get_entities(self) -> list[NamedEntity]:
        pass

    @abstractmethod
    def save_entities(self, named_entities: list[NamedEntity]) -> None:
        pass
