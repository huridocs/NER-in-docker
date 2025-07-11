from unittest import TestCase

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from use_cases.GroupNamedEntitiesUseCase import GroupNamedEntitiesUseCase


class TestDatesNamedEntityMergerUseCase(TestCase):
    def test_merge_dates(self):
        dates_entities = [NamedEntity(type=NamedEntityType.DATE, text="12 May 2023", normalized_text="2023-05-12")]
        dates_entities += [NamedEntity(type=NamedEntityType.DATE, text="twelve may 2023", normalized_text="2023-05-12")]
        dates_entities += [NamedEntity(type=NamedEntityType.DATE, text="11 4 2022", normalized_text="2022-04-11")]
        dates_entities += [NamedEntity(type=NamedEntityType.DATE, text="eleven april 2022", normalized_text="2022-04-11")]

        dates_grouped = GroupNamedEntitiesUseCase().group(dates_entities)

        self.assertEqual(2, len(dates_grouped))

        self.assertEqual("2023-05-12", dates_grouped[0].name)
        self.assertEqual(NamedEntityType.DATE, dates_grouped[0].type)
        self.assertEqual(2, len(dates_grouped[0].named_entities))
        self.assertEqual("12 May 2023", dates_grouped[0].named_entities[0].text)
        self.assertEqual("twelve may 2023", dates_grouped[0].named_entities[1].text)

        self.assertEqual("2022-04-11", dates_grouped[1].name)
        self.assertEqual(NamedEntityType.DATE, dates_grouped[1].type)
        self.assertEqual(2, len(dates_grouped[1].named_entities))
        self.assertEqual("11 4 2022", dates_grouped[1].named_entities[0].text)
        self.assertEqual("eleven april 2022", dates_grouped[1].named_entities[1].text)

    def test_should_not_merge_dates_that_are_similar(self):
        dates_entities = [NamedEntity(type=NamedEntityType.DATE, text="12 May 2023", normalized_text="2023-05-12")]
        dates_entities += [NamedEntity(type=NamedEntityType.DATE, text="22 May 2023", normalized_text="2023-05-22")]

        dates_grouped = GroupNamedEntitiesUseCase().group(dates_entities)

        self.assertEqual(2, len(dates_grouped))
