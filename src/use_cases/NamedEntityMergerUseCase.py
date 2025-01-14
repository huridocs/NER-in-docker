from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup


class NamedEntityMergerUseCase:
    def __init__(self):
        self.named_entities_groups = list()

    def get_entity_group(self, named_entity: NamedEntity) -> NamedEntityGroup:
        for named_entity_group in self.named_entities_groups:
            if named_entity_group.belongs_to_group(named_entity):
                return named_entity_group

        return NamedEntityGroup(type=named_entity.type, text=named_entity.text)

    def merge(self, named_entities: list[NamedEntity]) -> list[NamedEntityGroup]:
        for named_entity in named_entities:
            named_entity_group = self.get_entity_group(named_entity)
            named_entity_group.add_named_entity(named_entity)

            if named_entity_group not in self.named_entities_groups:
                self.named_entities_groups.append(named_entity_group)

        return self.named_entities_groups
