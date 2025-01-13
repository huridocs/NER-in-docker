from unittest import TestCase

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from use_cases.NamedEntityMergerUseCase import NamedEntityMergerUseCase


class TestNamedEntityMergerUseCase(TestCase):
    def test_merge_when_accents(self):
        name_entity_1 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="Maria Díaz")
        named_entities_groped = NamedEntityMergerUseCase([name_entity_1, name_entity_2]).merge()

        self.assertEqual(1, len(named_entities_groped))
        self.assertEqual("María Diaz", named_entities_groped[0].text)
        self.assertEqual(NamedEntityType.PERSON, named_entities_groped[0].type)

    def test_merge_when_two_last_names_in_same_context(self):
        name_entity_1 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz", context="context")
        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="Maria Díaz Pérez", context="context")
        named_entities_groped = NamedEntityMergerUseCase([name_entity_1, name_entity_2]).merge()

        self.assertEqual(1, len(named_entities_groped))
        self.assertEqual("Maria Díaz Pérez", named_entities_groped[0].text)

    def test_avoid_merge_when_different_context(self):
        name_entity_1 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz", context="context1")
        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="Maria Díaz Pérez", context="context2")
        named_entities_groped = NamedEntityMergerUseCase([name_entity_1, name_entity_2]).merge()

        self.assertEqual(2, len(named_entities_groped))
