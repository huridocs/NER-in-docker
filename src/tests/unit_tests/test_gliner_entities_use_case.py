import pytest
from os import getenv
from unittest import TestCase
from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType


@pytest.mark.skipif(getenv("GITHUB_ACTIONS") == "true", reason="Skip in CI environment as models are not downloaded locally")
class TestGLiNEREntitiesUseCase(TestCase):
    def setUp(self):
        from use_cases.GetGLiNEREntitiesUseCase import GetGLiNEREntitiesUseCase

        self.use_case = GetGLiNEREntitiesUseCase()

    def test_datetime_normalized(self):
        window_entities: list[dict] = [{"start": 0, "end": 0, "text": "12 January 2024"}]
        entities: list[NamedEntity] = self.use_case.convert_to_named_entity_type(window_entities)
        self.assertEqual("2024-01-12", entities[0].normalized_text)

    def test_date_extraction(self):
        text = "Today is 13th January 2024."
        entities: list[NamedEntity] = self.use_case.extract_dates(text)
        self.assertEqual(1, len(entities))
        self.assertEqual(entities[0].type, NamedEntityType.DATE)
        self.assertEqual("2024-01-13", entities[0].normalized_text)

    def test_avoid_uncompleted_date_extraction(self):
        text = "It should be Wednesday"
        entities: list[NamedEntity] = self.use_case.extract_dates(text)
        self.assertEqual(0, len(entities))

    def test_remove_overlapping_entities(self):
        window_entities: list[NamedEntity] = [
            NamedEntity(type=NamedEntityType.DATE, character_start=0, character_end=10, text="12 January 2024"),
            NamedEntity(type=NamedEntityType.DATE, character_start=3, character_end=15, text="12 January 2024"),
            NamedEntity(type=NamedEntityType.DATE, character_start=0, character_end=15, text="12 January 2024"),
        ]
        entities: list[NamedEntity] = self.use_case.remove_overlapping_entities(window_entities)
        self.assertEqual(len(entities), 1)
        self.assertEqual("12 January 2024", entities[0].text)
