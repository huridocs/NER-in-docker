from unittest import TestCase
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.NamedEntityType import NamedEntityType
from ner_in_docker.use_cases.GetGLiNEREntitiesUseCase import GetGLiNEREntitiesUseCase


class TestGLINEREntitiesUseCase(TestCase):
    def test_datetime_normalized(self):
        window_entities: list[dict] = [{"start": 0, "end": 0, "text": "12 January 2024"}]
        entities: list[NamedEntity] = GetGLiNEREntitiesUseCase().convert_to_named_entity_type(window_entities)
        self.assertEqual("2024-01-12", entities[0].normalized_text)

    def test_remove_overlapping_entities(self):
        window_entities: list[NamedEntity] = [
            NamedEntity(type=NamedEntityType.DATE, character_start=0, character_end=10, text="12 January 2024"),
            NamedEntity(type=NamedEntityType.DATE, character_start=3, character_end=15, text="12 January 2024"),
            NamedEntity(type=NamedEntityType.DATE, character_start=0, character_end=15, text="12 January 2024"),
        ]
        entities: list[NamedEntity] = GetGLiNEREntitiesUseCase().remove_overlapping_entities(window_entities)
        self.assertEqual(len(entities), 1)
        self.assertEqual("12 January 2024", entities[0].text)
