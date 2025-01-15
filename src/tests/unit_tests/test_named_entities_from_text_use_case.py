import pytest
from os import getenv
from unittest import TestCase
from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase


@pytest.mark.skipif(getenv("CI") == "true", reason="Skip in CI environment as models are not downloaded locally")
class TestNamedEntityMergerUseCase(TestCase):
    def test_get_entities(self):
        text = "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023"
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase().get_entities(text)

        self.assertEqual(5, len(entities))
        self.assertEqual("Maria Rodriguez", entities[0].text)
        self.assertEqual("Maria Rodriguez", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.PERSON, entities[0].type)
        self.assertEqual(0, entities[0].character_start)
        self.assertEqual(15, entities[0].character_end)

        self.assertEqual("the Louvre Museum", entities[1].text)
        self.assertEqual("the Louvre Museum", entities[1].normalized_text)
        self.assertEqual(NamedEntityType.ORGANIZATION, entities[1].type)
        self.assertEqual(24, entities[1].character_start)
        self.assertEqual(41, entities[1].character_end)

        self.assertEqual("Paris", entities[2].text)
        self.assertEqual("Paris", entities[2].normalized_text)
        self.assertEqual(NamedEntityType.LOCATION, entities[2].type)
        self.assertEqual(45, entities[2].character_start)
        self.assertEqual(50, entities[2].character_end)

        self.assertEqual("France", entities[3].text)
        self.assertEqual("France", entities[3].normalized_text)
        self.assertEqual(NamedEntityType.LOCATION, entities[3].type)
        self.assertEqual(52, entities[3].character_start)
        self.assertEqual(58, entities[3].character_end)

        self.assertEqual("July 12, 2023", entities[4].text)
        self.assertEqual("2023-07-12", entities[4].normalized_text)
        self.assertEqual(NamedEntityType.DATE, entities[4].type)
        self.assertEqual(74, entities[4].character_start)
        self.assertEqual(87, entities[4].character_end)

    def test_get_entities_of_type_organization(self):
        text = "I work for HURIDOCS organization."
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase().get_entities(text)

        self.assertEqual(1, len(entities))
        self.assertEqual("HURIDOCS", entities[0].text)
        self.assertEqual("HURIDOCS", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.ORGANIZATION, entities[0].type)
        self.assertEqual(11, entities[0].character_start)
        self.assertEqual(19, entities[0].character_end)

    def test_get_entities_of_type_law(self):
        text = "The Senate passed Resolution No. 122, establishing a set of rules for the impeachment trial."
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase().get_entities(text)

        self.assertEqual(2, len(entities))
        self.assertEqual("Resolution No. 122", entities[1].text)
        self.assertEqual("Resolution No. 122", entities[1].normalized_text)
        self.assertEqual(NamedEntityType.LAW, entities[1].type)
        self.assertEqual(18, entities[1].character_start)
        self.assertEqual(36, entities[1].character_end)
