from abc import abstractmethod, ABC

from domain.NamedEntityGroup import NamedEntityGroup


class PDFsGroupNameRepository(ABC):

    @abstractmethod
    def update_group_names_by_old_groups(self, named_entity_groups: list[NamedEntityGroup]):
        pass
