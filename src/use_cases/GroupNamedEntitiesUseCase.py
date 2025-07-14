from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType


class GroupNamedEntitiesUseCase:
    def __init__(self, prior_entities: list[NamedEntity] = None):
        self.prior_entities = prior_entities if prior_entities else []
        self.prior_groups: dict[str, NamedEntityGroup] = dict()
        self._initialize_prior_groups()
        self.groups: dict[str, NamedEntityGroup] = dict()

    def _initialize_prior_groups(self):
        """Initialize groups from prior entities, sorted by relevance."""
        sorted_prior_entities = sorted(self.prior_entities, key=lambda x: x.relevance_percentage, reverse=True)
        for prior_entity in sorted_prior_entities:
            group_name = prior_entity.group_name
            if group_name in self.prior_groups:
                self.prior_groups[group_name].named_entities.append(prior_entity)
                continue

            self.prior_groups[group_name] = NamedEntityGroup(
                type=prior_entity.type,
                name=prior_entity.group_name,
                named_entities=[prior_entity],
                top_relevance_entity=prior_entity,
            )

    def group(self, named_entities: list[NamedEntity]) -> list[NamedEntityGroup]:
        self._calculate_relevance_scores(named_entities)

        for named_entity in named_entities:
            normalized_entity = named_entity.get_with_normalize_entity_text()

            if self._try_assign_to_prior_group(normalized_entity):
                continue

            if self._try_assign_to_existing_group(normalized_entity):
                continue

            self._create_new_group_for_entity(normalized_entity)

        self._remove_empty_references_groups()
        return list(self.groups.values())

    @staticmethod
    def _calculate_relevance_scores(named_entities: list[NamedEntity]):
        for named_entity in named_entities:
            named_entity.set_relevance_score(named_entities)

    def _try_assign_to_prior_group(self, named_entity: NamedEntity) -> bool:
        for prior_group in self.prior_groups.values():
            if prior_group.belongs_to_group(named_entity):
                named_entity.group_name = prior_group.name
                prior_group.named_entities = [named_entity]
                prior_group.top_relevance_entity = self._determine_top_relevance_entity(
                    prior_group.top_relevance_entity, named_entity
                )
                del self.prior_groups[prior_group.name]
                self.groups[prior_group.name] = prior_group
                return True
        return False

    def _try_assign_to_existing_group(self, named_entity: NamedEntity) -> bool:
        """Try to assign the named entity to an existing group. Returns True if assigned."""
        for group in self.groups.values():
            if group.belongs_to_group(named_entity):
                self._assign_to_existing_group(named_entity, group)
                return True
        return False

    def _assign_to_existing_group(self, named_entity: NamedEntity, group: NamedEntityGroup):
        """Assign the named entity to a specific existing group."""
        # Update group name if the new entity has a better name
        better_group_name = self._choose_better_group_name(group.name, named_entity.text, named_entity.type)
        if better_group_name != group.name:
            # Update the group name and key in the groups dictionary
            del self.groups[group.name]
            group.name = better_group_name
            self.groups[better_group_name] = group
            # Update all entities in the group to have the new group name
            for entity in group.named_entities:
                entity.group_name = better_group_name

        named_entity.group_name = group.name
        group.top_relevance_entity = self._determine_top_relevance_entity(group.top_relevance_entity, named_entity)
        group.named_entities.append(named_entity)

    @staticmethod
    def _choose_better_group_name(current_name: str, candidate_name: str, entity_type: NamedEntityType) -> str:
        """Choose the better group name between current and candidate based on entity type."""
        if entity_type in [NamedEntityType.LOCATION, NamedEntityType.PERSON, NamedEntityType.ORGANIZATION]:
            if len(candidate_name) > len(current_name):
                return candidate_name
            if "," in candidate_name and "," not in current_name:
                return candidate_name

        return current_name

    @staticmethod
    def _determine_top_relevance_entity(current_top: NamedEntity, candidate: NamedEntity) -> NamedEntity:
        """Determine which entity has higher relevance percentage."""
        return current_top if current_top.relevance_percentage > candidate.relevance_percentage else candidate

    def _create_new_group_for_entity(self, named_entity: NamedEntity):
        """Create a new group for the named entity using the appropriate group identifier."""
        group_name = self._get_group_name_for_entity(named_entity)
        named_entity.group_name = group_name

        self.groups[group_name] = NamedEntityGroup(
            type=named_entity.type, name=group_name, named_entities=[named_entity], top_relevance_entity=named_entity
        )

    @staticmethod
    def _get_group_name_for_entity(named_entity: NamedEntity) -> str:
        """Get the appropriate group name for a named entity based on its type."""
        if named_entity.type == NamedEntityType.DATE and named_entity.normalized_text:
            return named_entity.normalized_text

        return named_entity.text

    def _remove_empty_references_groups(self):
        keys_to_remove = []
        for key, group in self.groups.items():
            if group.type != NamedEntityType.REFERENCE:
                continue
            if len(group.named_entities) != 1:
                continue
            if group.named_entities[0].relevance_percentage != 100:
                continue
            keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.groups[key]
