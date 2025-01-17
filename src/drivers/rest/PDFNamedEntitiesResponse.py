from pydantic import BaseModel
from domain.NamedEntityGroup import NamedEntityGroup
from drivers.rest.GroupResponse import GroupResponse
from drivers.rest.PDFNamedEntityResponse import PDFNamedEntityResponse


class PDFNamedEntitiesResponse(BaseModel):
    entities: list[PDFNamedEntityResponse]
    groups: list[GroupResponse]

    @staticmethod
    def from_named_entity_groups(named_entity_groups: list[NamedEntityGroup]):
        pdf_named_entity_responses = [
            PDFNamedEntityResponse.from_named_entity(entity, group.name)
            for group in named_entity_groups
            for entity in group.named_entities
        ]
        pdf_named_entity_responses = sorted(pdf_named_entity_responses, key=lambda x: x.character_start)
        group_responses = [
            GroupResponse.from_named_entity_group(group, pdf_named_entity_responses) for group in named_entity_groups
        ]
        return PDFNamedEntitiesResponse(entities=pdf_named_entity_responses, groups=group_responses)
