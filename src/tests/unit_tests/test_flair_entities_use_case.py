import pytest
from os import getenv
from unittest import TestCase
from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType


@pytest.mark.skipif(getenv("GITHUB_ACTIONS") == "true", reason="Skip in CI environment as models are not downloaded locally")
class TestFlairEntitiesUseCase(TestCase):
    def setUp(self):
        from use_cases.GetFlairEntitiesUseCase import GetFlairEntitiesUseCase

        self.use_case = GetFlairEntitiesUseCase()

    def test_entity_extraction(self):
        text = "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023"
        entities: list[NamedEntity] = self.use_case.get_entities(text)

        self.assertEqual(4, len(entities))
        self.assertEqual("Maria Rodriguez", entities[0].text)
        self.assertEqual("Maria Rodriguez", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.PERSON, entities[0].type)
        self.assertEqual(0, entities[0].character_start)
        self.assertEqual(15, entities[0].character_end)
