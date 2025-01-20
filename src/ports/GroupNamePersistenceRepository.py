from abc import abstractmethod, ABC

from domain.NamedEntityGroup import NamedEntityGroup


class GroupNamePersistenceRepository(ABC):

    @abstractmethod
    def save(self, named_entity_groups: list[NamedEntityGroup]):
        pass

    @abstractmethod
    def get_group_name(self, named_entity_group: NamedEntityGroup) -> str:
        pass
