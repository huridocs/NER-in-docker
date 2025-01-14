from unittest import TestCase

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from use_cases.NamedEntityMergerUseCase import NamedEntityMergerUseCase


class TestDatesNamedEntityMergerUseCase(TestCase):
    def test_merge_dates(self):
        location_entities = [NamedEntity(type=NamedEntityType.DATE, text="12 May 2023", normalized_text="2023-05-12")]
        location_entities += [NamedEntity(type=NamedEntityType.DATE, text="twelve may 2023", normalized_text="2023-05-12")]
        location_entities += [NamedEntity(type=NamedEntityType.DATE, text="11 4 2022", normalized_text="2022-04-11")]
        location_entities += [NamedEntity(type=NamedEntityType.DATE, text="eleven april 2022", normalized_text="2022-04-11")]

        locations_grouped = NamedEntityMergerUseCase().merge(location_entities)

        self.assertEqual(2, len(locations_grouped))

        self.assertEqual("2023-05-12", locations_grouped[0].text)
        self.assertEqual(NamedEntityType.DATE, locations_grouped[0].type)
        self.assertEqual(2, len(locations_grouped[0].named_entities))
        self.assertEqual("12 May 2023", locations_grouped[0].named_entities[0].text)
        self.assertEqual("twelve may 2023", locations_grouped[0].named_entities[1].text)

        self.assertEqual("2022-04-11", locations_grouped[1].text)
        self.assertEqual(NamedEntityType.DATE, locations_grouped[1].type)
        self.assertEqual(2, len(locations_grouped[1].named_entities))
        self.assertEqual("11 4 2022", locations_grouped[1].named_entities[0].text)
        self.assertEqual("eleven april 2022", locations_grouped[1].named_entities[1].text)
