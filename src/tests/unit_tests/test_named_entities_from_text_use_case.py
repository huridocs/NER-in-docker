from unittest import TestCase

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase


class TestNamedEntityMergerUseCase(TestCase):
    def test_get_entities(self):
        text = "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023"
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase(text).get_entities()

        self.assertEqual(3, len(entities))
        self.assertEqual("Maria Rodriguez", entities[0].text)
        self.assertEqual("Maria Rodriguez", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.PERSON, entities[0].type)
        self.assertEqual(0, entities[0].start)
        self.assertEqual(16, entities[0].end)

        self.assertEqual("Paris, France", entities[1].text)
        self.assertEqual("Paris, France", entities[1].normalized_text)
        self.assertEqual(NamedEntityType.LOCATION, entities[1].type)
        self.assertEqual(0, entities[1].start)
        self.assertEqual(16, entities[1].end)

        self.assertEqual("Wednesday, July 12, 2023", entities[2].text)
        self.assertEqual("2023-07-12", entities[2].normalized_text)
        self.assertEqual(NamedEntityType.DATE, entities[2].type)
        self.assertEqual(0, entities[2].start)
        self.assertEqual(16, entities[2].end)

    def test_get_entities_of_type_organization(self):
        text = "I work for HURIDOCS"
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase(text).get_entities()

        self.assertEqual(1, len(entities))
        self.assertEqual("HURIDOCS", entities[0].text)
        self.assertEqual("HURIDOCS", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.ORGANIZATION, entities[0].type)
        self.assertEqual(11, entities[0].start)
        self.assertEqual(19, entities[0].end)

    def test_get_entities_of_type_law(self):
        text = "It was the law 1234"
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase(text).get_entities()

        self.assertEqual(1, len(entities))
        self.assertEqual("law 1234", entities[0].text)
        self.assertEqual("law 1234", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.LAW, entities[0].type)
        self.assertEqual(11, entities[0].start)
        self.assertEqual(19, entities[0].end)
