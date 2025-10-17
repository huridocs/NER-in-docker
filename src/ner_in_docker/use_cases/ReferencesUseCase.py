from ner_in_docker.configuration import TITLES_TYPES
from ner_in_docker.domain.NamedEntityGroup import NamedEntityGroup
from ner_in_docker.domain.NamedEntityType import NamedEntityType
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.Segment import Segment
from pdf_token_type_labels import TokenType


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
                    group_name=group.name,
                    normalized_text=group.name,
                    character_start=character_start,
                    character_end=character_end,
                )
                entities.append(NamedEntity.from_segment(entity, segment, group.name))

        return self.remove_references_in_same_words(entities)

    def get_entities_from_segments(self, segments: list[Segment]) -> list[NamedEntity]:
        reference_entities: list[NamedEntity] = list()

        for segment in segments:
            if not segment.text:
                continue
            if str(segment.type).lower() in TITLES_TYPES:
                title_entity = NamedEntity(
                    type=NamedEntityType.REFERENCE,
                    text=segment.text,
                    group_name=segment.text,
                    normalized_text=segment.text,
                    character_start=0,
                    character_end=len(segment.text),
                    relevance_percentage=100,
                    segment_type=TokenType.from_text(segment.type),
                )
                named_entity = NamedEntity.from_segment(title_entity, segment)
                reference_entities.append(named_entity)
                self.references_groups.append(
                    NamedEntityGroup(
                        type=NamedEntityType.REFERENCE,
                        name=named_entity.group_name,
                        top_relevance_entity=named_entity,
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

    @staticmethod
    def remove_references_in_same_words(entities: list[NamedEntity]) -> list[NamedEntity]:
        only_references = [e for e in entities if e.type == NamedEntityType.REFERENCE]
        ordered_entities = sorted(
            only_references,
            key=lambda e: (e.segment.source_id, e.segment.page_number, e.segment.segment_number, e.character_start),
        )
        indexes_to_remove = set()
        for index, (entity, next_entity) in enumerate(zip(ordered_entities, ordered_entities[1:])):
            if entity.segment.source_id != next_entity.segment.source_id:
                continue
            if entity.segment.page_number != next_entity.segment.page_number:
                continue
            if entity.segment.segment_number != next_entity.segment.segment_number:
                continue
            if entity.character_end <= next_entity.character_start:
                continue
            if len(entity.text) > len(next_entity.text):
                indexes_to_remove.add(index + 1)
            else:
                indexes_to_remove.add(index)

        for index in indexes_to_remove:
            entity_index = entities.index(ordered_entities[index])
            del entities[entity_index]

        return entities
