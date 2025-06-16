from unittest import TestCase
from adapters.SQLitePDFsGroupNameRepository import SQLiteGroupsStoreRepository
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity

TEST_DATABASE_NAME = "test.db"


class TestPersistencePDFsGroupNameRepository(TestCase):

    def setUp(self):
        entity_1 = PDFNamedEntity(text="María Diaz", type=NamedEntityType.PERSON)
        entity_2 = PDFNamedEntity(text="María Diaz Perez", type=NamedEntityType.PERSON)
        group_to_save = NamedEntityGroup(
            name="María Diaz Perez", type=NamedEntityType.PERSON, named_entities=[entity_1, entity_2]
        )

        sqlite_repository = SQLiteGroupsStoreRepository(TEST_DATABASE_NAME)
        sqlite_repository.delete_database()
        sqlite_repository.save_group(group_to_save)

    def test_save_group(self):
        entity_1 = PDFNamedEntity(text="HURIDOCS ORG", type=NamedEntityType.ORGANIZATION)
        entity_2 = PDFNamedEntity(text="HURIDOCS", type=NamedEntityType.ORGANIZATION)
        group = NamedEntityGroup(name="HURIDOCS ORG", type=NamedEntityType.ORGANIZATION, named_entities=[entity_1, entity_2])

        sqlite_repository = SQLiteGroupsStoreRepository(TEST_DATABASE_NAME)
        sqlite_repository.save_group(group)

        groups_in_database = sqlite_repository.groups_in_database

        self.assertEqual(2, len(groups_in_database))

        self.assertEqual("María Diaz Perez", groups_in_database[0].name)
        self.assertEqual(NamedEntityType.PERSON, groups_in_database[0].type)

        person_entities = groups_in_database[0].named_entities
        self.assertEqual(2, len(person_entities))
        self.assertEqual("María Diaz", person_entities[0].text)
        self.assertEqual("María Diaz Perez", person_entities[1].text)

        self.assertEqual("HURIDOCS ORG", groups_in_database[1].name)
        self.assertEqual(NamedEntityType.ORGANIZATION, groups_in_database[1].type)

        organization_entities = groups_in_database[1].named_entities
        self.assertEqual(2, len(organization_entities))
        self.assertEqual({"HURIDOCS", "HURIDOCS ORG"}, {organization_entities[0].text, organization_entities[1].text})

    def test_set_group_names_from_storage(self):
        group_name_repository = SQLiteGroupsStoreRepository(TEST_DATABASE_NAME)

        new_entity_1 = PDFNamedEntity(text="María D.", type=NamedEntityType.PERSON)
        new_entity_2 = PDFNamedEntity(text="María Diaz", type=NamedEntityType.PERSON)

        new_person_group = NamedEntityGroup(
            name="María Diaz", type=NamedEntityType.PERSON, named_entities=[new_entity_1, new_entity_2]
        )

        another_person = PDFNamedEntity(text="Jane Doe", type=NamedEntityType.PERSON)
        other_group = NamedEntityGroup(name="Jane Doe", type=NamedEntityType.PERSON, named_entities=[another_person])

        updated_groups = group_name_repository.update_groups_by_old_groups([new_person_group, other_group])
        self.assertEqual(2, len(updated_groups))
        self.assertEqual("María Diaz Perez", updated_groups[0].name)
        self.assertEqual(2, len(updated_groups[0].named_entities))
        self.assertEqual(PDFNamedEntity, type(updated_groups[0].named_entities[1]))

        self.assertEqual(PDFNamedEntity, type(updated_groups[1].named_entities[0]))
        self.assertEqual("Jane Doe", updated_groups[1].name)
        self.assertEqual(1, len(updated_groups[1].named_entities))
