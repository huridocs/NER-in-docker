from unittest import TestCase

from adapters.SQLiteEntitiesStoreRepository import SQLiteEntitiesStoreRepository
from domain.NamedEntityType import NamedEntityType
from domain.NamedEntity import NamedEntity

TEST_DATABASE_NAME = "test.db"


class TestSQLiteEntitiesStoreRepository(TestCase):
    def setUp(self):
        entity_1 = NamedEntity(text="María Diaz", type=NamedEntityType.PERSON)
        entity_2 = NamedEntity(text="María Diaz Perez", type=NamedEntityType.PERSON)
        self.entities = [entity_1, entity_2]
        self.sqlite_repository = SQLiteEntitiesStoreRepository(TEST_DATABASE_NAME)
        self.sqlite_repository.delete_database()
        self.sqlite_repository.save_entities(self.entities)

    def test_save_entities(self):
        entity_1 = NamedEntity(text="HURIDOCS ORG", type=NamedEntityType.ORGANIZATION)
        entity_2 = NamedEntity(text="HURIDOCS", type=NamedEntityType.ORGANIZATION)
        entities = [entity_1, entity_2]
        sqlite_repository = SQLiteEntitiesStoreRepository(TEST_DATABASE_NAME)
        sqlite_repository.save_entities(entities)
        entities_in_database = sqlite_repository.get_entities()
        self.assertEqual(4, len(entities_in_database))
        self.assertEqual("María Diaz", entities_in_database[0].text)
        self.assertEqual(NamedEntityType.PERSON, entities_in_database[0].type)
        self.assertEqual("María Diaz Perez", entities_in_database[1].text)
        self.assertEqual(NamedEntityType.PERSON, entities_in_database[1].type)
        self.assertEqual("HURIDOCS ORG", entities_in_database[2].text)
        self.assertEqual(NamedEntityType.ORGANIZATION, entities_in_database[2].type)
        self.assertEqual("HURIDOCS", entities_in_database[3].text)
        self.assertEqual(NamedEntityType.ORGANIZATION, entities_in_database[3].type)

    def test_get_entities_empty(self):
        sqlite_repository = SQLiteEntitiesStoreRepository("empty_test.db")
        sqlite_repository.delete_database()
        entities = sqlite_repository.get_entities()
        self.assertEqual(0, len(entities))
