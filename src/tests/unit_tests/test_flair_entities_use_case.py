from unittest import TestCase
from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from use_cases.GetFlairEntitiesUseCase import GetFlairEntitiesUseCase


class TestFlairEntitiesUseCase(TestCase):
    def test_entity_extraction(self):
        text = "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023"
        entities: list[NamedEntity] = GetFlairEntitiesUseCase().get_entities(text)

        self.assertEqual(4, len(entities))
        self.assertEqual("Maria Rodriguez", entities[0].text)
        self.assertEqual("Maria Rodriguez", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.PERSON, entities[0].type)
        self.assertEqual(0, entities[0].character_start)
        self.assertEqual(15, entities[0].character_end)
