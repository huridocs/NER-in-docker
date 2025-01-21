from domain.NamedEntityGroup import NamedEntityGroup
from domain.PDFNamedEntity import PDFNamedEntity
from ports.PDFsGroupNameRepository import PDFsGroupNameRepository
from use_cases.NamedEntityMergerUseCase import NamedEntityMergerUseCase


class PDFNamedEntityMergerUseCase:
    def __init__(self, group_names_repository: PDFsGroupNameRepository):
        self.group_names_repository = group_names_repository

    def merge(self, named_entities: list[PDFNamedEntity]) -> list[NamedEntityGroup]:
        named_entity_groups = NamedEntityMergerUseCase().merge(named_entities)
        return self.group_names_repository.update_group_names_by_old_groups(named_entity_groups)
