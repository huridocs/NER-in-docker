from unittest import TestCase

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from use_cases.NamedEntitiesFromTextUseCase import NamedEntitiesFromTextUseCase


class TestNamedEntityMergerUseCase(TestCase):
    def test_get_entities(self):
        text = "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023"
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase(text).get_entities()

        self.assertEqual(5, len(entities))
        self.assertEqual("Maria Rodriguez", entities[0].text)
        self.assertEqual("Maria Rodriguez", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.PERSON, entities[0].type)
        self.assertEqual(0, entities[0].start)
        self.assertEqual(15, entities[0].end)

        self.assertEqual("the Louvre Museum", entities[1].text)
        self.assertEqual("the Louvre Museum", entities[1].normalized_text)
        self.assertEqual(NamedEntityType.ORGANIZATION, entities[1].type)
        self.assertEqual(24, entities[1].start)
        self.assertEqual(41, entities[1].end)

        self.assertEqual("Paris", entities[2].text)
        self.assertEqual("Paris", entities[2].normalized_text)
        self.assertEqual(NamedEntityType.LOCATION, entities[2].type)
        self.assertEqual(45, entities[2].start)
        self.assertEqual(50, entities[2].end)

        self.assertEqual("France", entities[3].text)
        self.assertEqual("France", entities[3].normalized_text)
        self.assertEqual(NamedEntityType.LOCATION, entities[3].type)
        self.assertEqual(52, entities[3].start)
        self.assertEqual(58, entities[3].end)

        self.assertEqual("Wednesday, July 12, 2023", entities[4].text)
        self.assertEqual("2023-07-12", entities[4].normalized_text)
        self.assertEqual(NamedEntityType.DATE, entities[4].type)
        self.assertEqual(0, entities[4].start)
        self.assertEqual(16, entities[4].end)

        # self.assertEqual("Wednesday, July 12, 2023", entities[2].text)
        # self.assertEqual("2023-07-12", entities[2].normalized_text)
        # self.assertEqual(NamedEntityType.DATE, entities[2].type)
        # self.assertEqual(0, entities[2].start)
        # self.assertEqual(16, entities[2].end)

    def test_get_entities_of_type_organization(self):
        text = "I work for HURIDOCS organization."
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase(text).get_entities()

        self.assertEqual(1, len(entities))
        self.assertEqual("HURIDOCS", entities[0].text)
        self.assertEqual("HURIDOCS", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.ORGANIZATION, entities[0].type)
        self.assertEqual(11, entities[0].start)
        self.assertEqual(19, entities[0].end)

    def test_get_entities_of_type_law(self):
        text = "It was the law ExampleLaw123"
        entities: list[NamedEntity] = NamedEntitiesFromTextUseCase(text).get_entities()

        self.assertEqual(1, len(entities))
        self.assertEqual("ExampleLaw123", entities[0].text)
        self.assertEqual("ExampleLaw123", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.LAW, entities[0].type)
        self.assertEqual(11, entities[0].start)
        self.assertEqual(24, entities[0].end)
