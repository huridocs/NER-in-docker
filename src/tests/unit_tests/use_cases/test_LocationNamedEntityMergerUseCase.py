from unittest import TestCase

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from use_cases.GroupNamedEntitiesUseCase import GroupNamedEntitiesUseCase


class TestLocationNamedEntityMergerUseCase(TestCase):
    def test_merge_when_countries_ISO(self):
        location_entities = [NamedEntity(type=NamedEntityType.LOCATION, text="Turkey")]
        location_entities += [NamedEntity(type=NamedEntityType.LOCATION, text="Türkiye")]
        location_entities += [NamedEntity(type=NamedEntityType.LOCATION, text="TR")]
        location_entities += [NamedEntity(type=NamedEntityType.LOCATION, text="TUR")]
        location_entities += [NamedEntity(type=NamedEntityType.LOCATION, text="ESP")]
        location_entities += [NamedEntity(type=NamedEntityType.LOCATION, text="Spain")]
        location_entities += [NamedEntity(type=NamedEntityType.LOCATION, text="ES")]

        locations_grouped = GroupNamedEntitiesUseCase().group(location_entities)

        self.assertEqual(2, len(locations_grouped))

        self.assertEqual("Türkiye", locations_grouped[0].name)
        self.assertEqual(NamedEntityType.LOCATION, locations_grouped[0].type)
        self.assertEqual(4, len(locations_grouped[0].named_entities))
        self.assertEqual("Turkey", locations_grouped[0].named_entities[0].text)
        self.assertEqual("Türkiye", locations_grouped[0].named_entities[1].text)
        self.assertEqual("TR", locations_grouped[0].named_entities[2].text)
        self.assertEqual("TUR", locations_grouped[0].named_entities[3].text)

        self.assertEqual("Spain", locations_grouped[1].name)
        self.assertEqual(NamedEntityType.LOCATION, locations_grouped[1].type)
        self.assertEqual(3, len(locations_grouped[1].named_entities))
        self.assertEqual("ESP", locations_grouped[1].named_entities[0].text)
        self.assertEqual("Spain", locations_grouped[1].named_entities[1].text)
        self.assertEqual("ES", locations_grouped[1].named_entities[2].text)

    def test_merge_when_they_are_cities(self):
        location_entities = [NamedEntity(type=NamedEntityType.LOCATION, text="Paris")]
        location_entities += [NamedEntity(type=NamedEntityType.LOCATION, text="PARIS")]
        location_entities += [NamedEntity(type=NamedEntityType.LOCATION, text="Mérida")]
        location_entities += [NamedEntity(type=NamedEntityType.LOCATION, text="merida")]

        locations_grouped = GroupNamedEntitiesUseCase().group(location_entities)

        self.assertEqual(2, len(locations_grouped))

        self.assertEqual("Paris", locations_grouped[0].name)
        self.assertEqual(NamedEntityType.LOCATION, locations_grouped[0].type)
        self.assertEqual(2, len(locations_grouped[0].named_entities))

        self.assertEqual("Mérida", locations_grouped[1].name)
        self.assertEqual(NamedEntityType.LOCATION, locations_grouped[1].type)
        self.assertEqual(2, len(locations_grouped[1].named_entities))
