from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity
from ports.GroupsStoreRepository import GroupsStoreRepository
from use_cases.NamedEntityMergerUseCase import NamedEntityMergerUseCase


class PDFNamedEntityMergerUseCase:
    def __init__(self, group_names_repository: GroupsStoreRepository):
        self.group_names_repository = group_names_repository

    def merge(self, named_entities: list[PDFNamedEntity]) -> list[NamedEntityGroup]:
        ner_entities = [
            x
            for x in named_entities
            if x.type not in [NamedEntityType.REFERENCE_POINTER, NamedEntityType.REFERENCE_DESTINATION]
        ]
        named_entity_groups = NamedEntityMergerUseCase().merge(ner_entities)
        return self.group_names_repository.update_groups_by_old_groups(named_entity_groups)
