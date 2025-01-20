from abc import abstractmethod, ABC

from domain.NamedEntityGroup import NamedEntityGroup


class PDFsGroupNameRepository(ABC):

    @abstractmethod
    def save_group(self, named_entity_groups: list[NamedEntityGroup]):
        pass

    @abstractmethod
    def set_group_names_from_storage(self, named_entity_groups: list[NamedEntityGroup]):
        pass
