from domain.NamedEntityGroup import NamedEntityGroup
from domain.PDFNamedEntity import PDFNamedEntity
from ports.PDFsGroupNameRepository import PDFsGroupNameRepository
from use_cases.NamedEntityMergerUseCase import NamedEntityMergerUseCase


class PDFNamedEntityMergerUseCase:
    def __init__(self, group_names_repository: PDFsGroupNameRepository):
        self.group_names_repository = group_names_repository

    def merge(self, named_entities: list[PDFNamedEntity]) -> list[NamedEntityGroup]:
        named_entity_groups = NamedEntityMergerUseCase().merge(named_entities)
        self.group_names_repository.save_groups(named_entity_groups)
        return self.group_names_repository.set_group_names_from_storage(named_entity_groups)
