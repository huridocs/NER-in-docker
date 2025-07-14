from pydantic import BaseModel
from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from drivers.rest.response_entities.EntityTextResponse import EntityTextResponse
from drivers.rest.response_entities.GroupResponse import GroupResponse
from drivers.rest.response_entities.NamedEntityResponse import NamedEntityResponse


class NamedEntitiesResponse(BaseModel):
    entities: list[NamedEntityResponse]
    groups: list[GroupResponse]

    @staticmethod
    def from_groups(named_entity_groups: list[NamedEntityGroup]) -> "NamedEntitiesResponse":
        named_entities: list[NamedEntity] = []

        groups_dict = {}
        for group in named_entity_groups:
            named_entities.extend(group.named_entities)
            if group.name not in groups_dict:
                groups_dict[group.name] = group

        named_entities.sort(key=lambda x: (x.segment.source_id, x.character_start), reverse=True)
        entities_response = NamedEntitiesResponse._create_entities_response(named_entities)
        entities_response = NamedEntitiesResponse._sort_entities(entities_response)
        groups_response = NamedEntitiesResponse._create_groups_response(groups_dict, entities_response)

        return NamedEntitiesResponse(entities=entities_response, groups=groups_response)

    @staticmethod
    def _create_entities_response(named_entities: list[NamedEntity]) -> list[NamedEntityResponse]:
        entities_response: list[NamedEntityResponse] = []

        for named_entity in named_entities:
            entity_response = NamedEntityResponse.from_named_entity(named_entity)
            entities_response.append(entity_response)

        return entities_response

    @staticmethod
    def _sort_entities(entities_response: list[NamedEntityResponse]) -> list[NamedEntityResponse]:
        sort_key = lambda x: (x.source_id, x.segment.page_number, x.segment.segment_number, x.segment.character_start)

        return sorted(entities_response, key=sort_key)

    @staticmethod
    def group_min_index(group: GroupResponse):
        if not group.entities:
            return float("inf")
        return min(getattr(entity, "index", float("inf")) for entity in group.entities)

    @staticmethod
    def _sort_groups(groups_response: list[GroupResponse]) -> list[GroupResponse]:
        for group in groups_response:
            group.entities.sort(key=lambda x: x.index)

        return sorted(groups_response, key=NamedEntitiesResponse.group_min_index)

    @staticmethod
    def _create_groups_response(
        groups_dict: dict[str, NamedEntityGroup], entities_response: list[NamedEntityResponse]
    ) -> list[GroupResponse]:
        groups_response: dict[str, GroupResponse] = {}
        sorted_entities_by_score = sorted(entities_response, key=lambda x: x.relevance_percentage, reverse=True)
        for entity in sorted_entities_by_score:
            group_name = entity.group_name

            if group_name not in groups_response:
                groups_response[group_name] = GroupResponse.from_entity(entities_response, entity, groups_dict[group_name])
                continue

            entity_text_response = EntityTextResponse.from_entity(entities_response, entity)
            groups_response[group_name].entities.append(entity_text_response)

        return NamedEntitiesResponse._sort_groups(list(groups_response.values()))
