from unittest import TestCase
from adapters.SQLitePDFsGroupNameRepository import SQLitePDFsGroupNameRepository
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity


class TestPersistencePDFsGroupNameRepository(TestCase):

    def test_save_group(self):
        SQLitePDFsGroupNameRepository("test.db").delete_database()
        group_name_repository = SQLitePDFsGroupNameRepository("test.db")
        entity_1 = PDFNamedEntity(text="María Diaz", type=NamedEntityType.PERSON)
        entity_2 = PDFNamedEntity(text="María Diaz Perez", type=NamedEntityType.PERSON)
        other_entity = PDFNamedEntity(text="Other Entity", type=NamedEntityType.ORGANIZATION)
        group_1 = NamedEntityGroup(name="María Diaz Perez", type=NamedEntityType.PERSON, named_entities=[entity_1, entity_2])
        group_2 = NamedEntityGroup(name="Other Group", type=NamedEntityType.ORGANIZATION, named_entities=[other_entity])
        group_name_repository.save_group(group_1)
        group_name_repository.save_group(group_2)

        groups_persistence = group_name_repository.load_groups_persistence()

        self.assertEqual(2, len(groups_persistence))

        self.assertEqual("María Diaz Perez", groups_persistence[0].name)
        self.assertEqual(NamedEntityType.PERSON, groups_persistence[0].type)
        self.assertEqual(2, len(groups_persistence[0].named_entities))
        self.assertEqual("María Diaz", groups_persistence[0].named_entities[0].text)
        self.assertEqual("María Diaz Perez", groups_persistence[0].named_entities[1].text)

        self.assertEqual("Other Group", groups_persistence[1].name)
        self.assertEqual(NamedEntityType.ORGANIZATION, groups_persistence[1].type)
        self.assertEqual(1, len(groups_persistence[1].named_entities))
        self.assertEqual("Other Entity", groups_persistence[1].named_entities[0].text)

    def test_load_groups_persistence(self):
        SQLitePDFsGroupNameRepository("test.db").delete_database()
        group_name_repository = SQLitePDFsGroupNameRepository("test.db")
        group_name_repository.cursor.execute(
            "INSERT INTO groups (id, name, type) VALUES (?, ?, ?)", (1, "Maria Diaz Perez", "PERSON")
        )
        group_name_repository.cursor.execute(
            "INSERT INTO groups (id, name, type) VALUES (?, ?, ?)", (2, "HURIDOCS", "ORGANIZATION")
        )
        entities_data = [(1, "Maria Diaz Perez"), (1, "Maria Diaz"), (2, "HURIDOCS")]
        group_name_repository.cursor.executemany("INSERT INTO entities (group_id, entity_text) VALUES (?, ?)", entities_data)
        group_name_repository.connection.commit()

        loaded_groups = group_name_repository.load_groups_persistence()
        self.assertEqual(len(loaded_groups), 2)

        person_group = [g for g in loaded_groups if g.type == "PERSON"][0]
        org_group = [g for g in loaded_groups if g.type == "ORGANIZATION"][0]

        self.assertEqual(person_group.name, "Maria Diaz Perez")
        self.assertEqual(len(person_group.named_entities), 2)
        self.assertEqual("Maria Diaz", person_group.named_entities[0].text)
        self.assertEqual("Maria Diaz Perez", person_group.named_entities[1].text)

        self.assertEqual(org_group.name, "HURIDOCS")
        self.assertEqual(len(org_group.named_entities), 1)
        self.assertEqual("HURIDOCS", org_group.named_entities[0].text)

    def test_set_group_names_from_storage(self):
        SQLitePDFsGroupNameRepository("test.db").delete_database()
        group_name_repository = SQLitePDFsGroupNameRepository("test.db")
        entity_1 = PDFNamedEntity(text="María Diaz", type=NamedEntityType.PERSON)
        entity_2 = PDFNamedEntity(text="María Diaz Perez", type=NamedEntityType.PERSON)
        initial_person_group = NamedEntityGroup(
            name="Maria Diaz Perez", type=NamedEntityType.PERSON, named_entities=[entity_1, entity_2]
        )

        org_entity = PDFNamedEntity(text="HURIDOCS", type=NamedEntityType.ORGANIZATION)
        org_group = NamedEntityGroup(name="HURIDOCS", type=NamedEntityType.ORGANIZATION, named_entities=[org_entity])

        group_name_repository.save_group(initial_person_group)
        group_name_repository.save_group(org_group)
        group_name_repository.saved_groups = group_name_repository.load_groups_persistence()

        new_entity_1 = PDFNamedEntity(text="María D.", type=NamedEntityType.PERSON)
        new_entity_2 = PDFNamedEntity(text="María Diaz", type=NamedEntityType.PERSON)

        new_person_group = NamedEntityGroup(
            name="María Diaz", type=NamedEntityType.PERSON, named_entities=[new_entity_1, new_entity_2]
        )

        another_person = PDFNamedEntity(text="Jane Doe", type=NamedEntityType.PERSON)
        another_person_group = NamedEntityGroup(
            name="Jane Doe", type=NamedEntityType.PERSON, named_entities=[another_person]
        )

        updated_groups = group_name_repository.set_group_names_from_storage([new_person_group, another_person_group])
        self.assertEqual(2, len(updated_groups))
        self.assertEqual("Maria Diaz Perez", updated_groups[0].name)
        self.assertEqual(2, len(updated_groups[0].named_entities))
        self.assertEqual("Jane Doe", updated_groups[1].name)
        self.assertEqual(1, len(updated_groups[1].named_entities))
