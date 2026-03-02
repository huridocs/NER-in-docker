from abc import abstractmethod, ABC

from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.Segment import Segment


class EntitiesStoreRepository(ABC):

    @abstractmethod
    def get_entities(self) -> list[NamedEntity]:
        pass

    @abstractmethod
    def save_entities(self, named_entities: list[NamedEntity]) -> None:
        pass

    @abstractmethod
    def delete_database(self):
        pass

    @abstractmethod
    def save_segments(self, segments: list[Segment]) -> bool:
        pass
