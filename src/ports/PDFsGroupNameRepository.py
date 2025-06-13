from abc import abstractmethod, ABC

from domain.NamedEntityGroup import NamedEntityGroup


class PDFsGroupNameRepository(ABC):

    @abstractmethod
    def update_groups_by_old_groups(self, named_entity_groups: list[NamedEntityGroup]):
        pass

    @abstractmethod
    def get_reference_destinations(self) -> list[NamedEntityGroup]:
        pass
