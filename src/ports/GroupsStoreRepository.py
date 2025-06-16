from abc import abstractmethod, ABC

from domain.NamedEntityGroup import NamedEntityGroup


class GroupsStoreRepository(ABC):

    @abstractmethod
    def update_groups_by_old_groups(self, named_entity_groups: list[NamedEntityGroup]):
        pass

    @abstractmethod
    def update_reference_destinations(self, new_groups_destinations: list[NamedEntityGroup]) -> list[NamedEntityGroup]:
        pass
