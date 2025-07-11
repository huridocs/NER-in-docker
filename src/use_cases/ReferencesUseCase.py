from configuration import TITLES_TYPES
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from domain.NamedEntity import NamedEntity
from domain.Segment import Segment
from domain.TokenType import TokenType


class ReferencesUseCase:
    def __init__(self, prior_entities: list[NamedEntity] = None):
        self.prior_entities = prior_entities if prior_entities else []
        self.references_groups: list[NamedEntityGroup] = list()
        self.load_reference_destinations_groups()

    def get_entities(self, segment: Segment) -> list[NamedEntity]:
        if str(segment.type).lower() in TITLES_TYPES:
            return []

        entities: list[NamedEntity] = list()
        for group in self.references_groups:
            positions = group.get_references_in_text(segment.text)
            for character_start, character_end in positions:
                entity = NamedEntity(
                    type=NamedEntityType.REFERENCE,
                    text=segment.text[character_start:character_end],
                    character_start=character_start,
                    character_end=character_end,
                )
                entities.append(NamedEntity.from_segment(entity, segment, group.name))

        return entities

    def get_entities_from_segments(self, segments: list[Segment]) -> list[NamedEntity]:
        reference_entities: list[NamedEntity] = list()

        for segment in segments:
            if str(segment.type).lower() in TITLES_TYPES:
                title_entity = NamedEntity(
                    type=NamedEntityType.REFERENCE,
                    text=segment.text,
                    character_start=0,
                    character_end=len(segment.text),
                    relevance_percentage=1,
                    segment_type=TokenType.from_text(segment.type),
                )
                reference_entities.append(NamedEntity.from_segment(title_entity, segment))
                self.references_groups.append(
                    NamedEntityGroup(
                        type=NamedEntityType.REFERENCE,
                        name=segment.text,
                    )
                )

        for segment in segments:
            reference_entities.extend(self.get_entities(segment))

        return reference_entities

    def load_reference_destinations_groups(self):
        for entity in self.prior_entities:
            if entity.type == NamedEntityType.REFERENCE and entity.relevance_percentage == 100:
                self.references_groups.append(
                    NamedEntityGroup(
                        type=NamedEntityType.REFERENCE,
                        name=entity.text,
                    )
                )
