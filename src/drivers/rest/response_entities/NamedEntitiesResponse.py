from pydantic import BaseModel

from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from domain.PDFNamedEntity import PDFNamedEntity
from drivers.rest.response_entities.NamedEntityResponse import NamedEntityResponse
from drivers.rest.response_entities.GroupResponse import GroupResponse
from drivers.rest.response_entities.PDFNamedEntityResponse import PDFNamedEntityResponse


class NamedEntitiesResponse(BaseModel):
    entities: list[NamedEntityResponse | PDFNamedEntityResponse]
    groups: list[GroupResponse]

    def sort_entities(self):
        if not self.entities:
            return

        if isinstance(self.entities[0], PDFNamedEntityResponse):
            self.entities.sort(
                key=lambda x: (x.pdf_segment.page_number, x.pdf_segment.segment_number, x.pdf_segment.character_start)
            )
        else:
            self.entities.sort(key=lambda x: x.character_start)

    def add_entity(self, entity: NamedEntity | PDFNamedEntity, group_name: str):
        entity_response = (
            PDFNamedEntityResponse.from_pdf_named_entity(entity, group_name)
            if isinstance(entity, PDFNamedEntity)
            else NamedEntityResponse.from_named_entity(entity, group_name)
        )
        self.entities.append(entity_response)

    def add_group(self, named_entity_group: NamedEntityGroup):
        self.groups.append(GroupResponse.from_named_entity_group(named_entity_group, self.entities))

    @staticmethod
    def from_named_entity_groups(named_entity_groups: list[NamedEntityGroup]):
        named_entities_response = NamedEntitiesResponse(entities=list(), groups=list())

        for group in named_entity_groups:
            for entity in group.named_entities:
                named_entities_response.add_entity(entity, group.name)

        named_entities_response.sort_entities()

        for group in named_entity_groups:
            named_entities_response.add_group(group)

        return named_entities_response
