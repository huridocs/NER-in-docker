from unittest import TestCase

from adapters.SQLitePDFsGroupNameRepository import SQLitePDFsGroupNameRepository
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity


class TestPersistencePDFsGroupNameRepository(TestCase):

    def test_save_group(self):
        group_name_repository = SQLitePDFsGroupNameRepository()
        entity_1 = PDFNamedEntity(text="María Diaz", type=NamedEntityType.PERSON)
        entity_2 = PDFNamedEntity(text="María Diaz Perez", type=NamedEntityType.PERSON)
        other_entity = PDFNamedEntity(text="Other Entity", type=NamedEntityType.ORGANIZATION)
        group_1 = NamedEntityGroup(name="María Diaz Perez", type=NamedEntityType.PERSON, named_entities=[entity_1, entity_2])
        group_2 = NamedEntityGroup(name="Other Group", type=NamedEntityType.ORGANIZATION, named_entities=[other_entity])
        group_name_repository.save_groups([group_1, group_2])

        groups_persistence = group_name_repository.get_groups_persistence()

        self.assertEqual(2, len(groups_persistence))

        self.assertEqual("María Diaz Perez", groups_persistence[0].name)
        self.assertEqual(NamedEntityType.PERSON, groups_persistence[0].type)
        self.assertEqual(2, len(groups_persistence[0].entities_names))
        self.assertEqual("María Diaz", groups_persistence[0].entities_names[0])
        self.assertEqual("María Diaz Perez", groups_persistence[0].entities_names[1])

        self.assertEqual("Other Group", groups_persistence[1].name)
        self.assertEqual(NamedEntityType.ORGANIZATION, groups_persistence[1].type)
        self.assertEqual(1, len(groups_persistence[1].entities_names))
        self.assertEqual("Other Entity", groups_persistence[1].entities_names[0])
