from unittest import TestCase

from domain.NamedEntityType import NamedEntityType
from domain.NamedEntity import NamedEntity
from use_cases.GroupNamedEntitiesUseCase import GroupNamedEntitiesUseCase


class TestNamedEntityMergerUseCase(TestCase):
    def test_merge_entities(self):
        name_entity_1 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_3 = NamedEntity(type=NamedEntityType.PERSON, text="Other Name")
        pdf_named_entity_merger_use_case = GroupNamedEntitiesUseCase()
        named_entities_grouped = pdf_named_entity_merger_use_case.group([name_entity_1, name_entity_2, name_entity_3])

        self.assertEqual(2, len(named_entities_grouped))
        self.assertEqual("María Diaz", named_entities_grouped[0].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[0].type)
        self.assertEqual(2, len(named_entities_grouped[0].named_entities))
        self.assertEqual("María Diaz", named_entities_grouped[0].named_entities[0].text)
        self.assertEqual("María Diaz", named_entities_grouped[0].named_entities[1].text)

        self.assertEqual("Other Name", named_entities_grouped[1].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[1].type)
        self.assertEqual(1, len(named_entities_grouped[1].named_entities))
        self.assertEqual("Other Name", named_entities_grouped[1].named_entities[0].text)

    def test_merge_entities_using_previous_pdfs(self):
        prior_entity = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz Perez", group_name="María Diaz Perez")
        group_use_case = GroupNamedEntitiesUseCase(prior_entities=[prior_entity])

        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        named_entities_grouped = group_use_case.group([name_entity_2])

        self.assertEqual(1, len(named_entities_grouped))
        self.assertEqual("María Diaz Perez", named_entities_grouped[0].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[0].type)
        self.assertEqual(1, len(named_entities_grouped[0].named_entities))
        self.assertEqual("María Diaz", named_entities_grouped[0].named_entities[0].text)
