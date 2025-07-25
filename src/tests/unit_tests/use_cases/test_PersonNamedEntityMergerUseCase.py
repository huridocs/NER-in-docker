from unittest import TestCase

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from use_cases.GroupNamedEntitiesUseCase import GroupNamedEntitiesUseCase


class TestPersonNamedEntityMergerUseCase(TestCase):
    def test_merge_entities(self):
        name_entity_1 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_3 = NamedEntity(type=NamedEntityType.PERSON, text="Other Name")
        named_entities_grouped = GroupNamedEntitiesUseCase().group([name_entity_1, name_entity_2, name_entity_3])

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

    def test_merge_when_accents_differences(self):
        name_entity_1 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="Maria Díaz")
        named_entities_grouped = GroupNamedEntitiesUseCase().group([name_entity_1, name_entity_2])

        self.assertEqual(1, len(named_entities_grouped))
        self.assertEqual("María Diaz", named_entities_grouped[0].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[0].type)

    def test_merge_when_punctuation_differences(self):
        name_entity_1 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="Maria, Díaz")
        name_entity_3 = NamedEntity(type=NamedEntityType.PERSON, text="Maria. Díaz")
        named_entities_grouped = GroupNamedEntitiesUseCase().group([name_entity_1, name_entity_2, name_entity_3])

        self.assertEqual(1, len(named_entities_grouped))
        self.assertEqual("Maria, Díaz", named_entities_grouped[0].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[0].type)

    def test_merge_when_abbreviations(self):
        name_entity_1 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")
        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="M. Diaz")
        name_entity_3 = NamedEntity(type=NamedEntityType.PERSON, text="María D.")
        named_entities_grouped = GroupNamedEntitiesUseCase().group([name_entity_1, name_entity_2, name_entity_3])

        self.assertEqual(1, len(named_entities_grouped))
        self.assertEqual("María Diaz", named_entities_grouped[0].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[0].type)

    def test_merge_when_person_name_words_in_different_order(self):
        name_entity_1 = NamedEntity(type=NamedEntityType.PERSON, text="María Diaz Pérez")
        name_entity_2 = NamedEntity(type=NamedEntityType.PERSON, text="Díaz Perez Maria")
        name_entity_3 = NamedEntity(type=NamedEntityType.PERSON, text="Other Perez Maria")

        named_entities_grouped = GroupNamedEntitiesUseCase().group([name_entity_1, name_entity_2, name_entity_3])

        self.assertEqual(2, len(named_entities_grouped))

        self.assertEqual("María Diaz Pérez", named_entities_grouped[0].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[0].type)

        self.assertEqual("Other Perez Maria", named_entities_grouped[1].name)

    def test_merge_when_using_abbreviations(self):
        named_entities = [NamedEntity(type=NamedEntityType.PERSON, text="M. Diaz Pérez")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="María Diaz Pérez")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="Maria D. Perez")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="Maria D.Perez")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="M. D.Perez")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="M.D. Perez")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="M.D.Perez")]

        other_entity = [NamedEntity(type=NamedEntityType.PERSON, text="P. Perez Maria")]

        named_entities_grouped = GroupNamedEntitiesUseCase().group(named_entities + other_entity)

        self.assertEqual(2, len(named_entities_grouped))

        self.assertEqual("María Diaz Pérez", named_entities_grouped[0].name)
        self.assertEqual(NamedEntityType.PERSON, named_entities_grouped[0].type)

        self.assertEqual("P. Perez Maria", named_entities_grouped[1].name)

    def test_merge_when_one_letter_difference(self):
        named_entities = [NamedEntity(type=NamedEntityType.PERSON, text="Mría Diaz Pérez")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="María Diaz Perez")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="María Diaz Pére")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="María Diaz Parez")]

        other_entity = [NamedEntity(type=NamedEntityType.PERSON, text="María Diaz Pe")]

        named_entities_grouped = GroupNamedEntitiesUseCase().group(named_entities + other_entity)

        self.assertEqual(1, len(named_entities_grouped))

    def test_merge_when_two_last_names_in_same_context(self):
        named_entities = [NamedEntity(type=NamedEntityType.PERSON, text="María Diaz")]
        named_entities += [NamedEntity(type=NamedEntityType.PERSON, text="Maria Díaz Pérez")]

        other_entity = [NamedEntity(type=NamedEntityType.PERSON, text="Other Name")]
        named_entities_grouped = GroupNamedEntitiesUseCase().group(named_entities + other_entity)

        self.assertEqual(2, len(named_entities_grouped))
        self.assertEqual("Maria Díaz Pérez", named_entities_grouped[0].name)
