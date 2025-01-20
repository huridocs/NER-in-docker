from pathlib import Path

from adapters.GroupPersistence import GroupPersistence
from configuration import ROOT_PATH
from domain.NamedEntityGroup import NamedEntityGroup
from ports.PDFsGroupNameRepository import PDFsGroupNameRepository
import sqlite3


class SQLitePDFsGroupNameRepository(PDFsGroupNameRepository):

    def __init__(self):
        self.connection = sqlite3.connect(Path(ROOT_PATH, "data", "named_entities.db"))
        self.cursor = self.connection.cursor()
        self.create_database()
        self.saved_groups: list[GroupPersistence] = self.load_groups_persistence()

    def create_database(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL
            )"""
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                entity_name TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        """
        )
        self.connection.commit()

    def save_groups(self, named_entity_groups: list[NamedEntityGroup]):
        for group in named_entity_groups:
            self.cursor.execute("INSERT INTO groups (name, type) VALUES (?, ?)", (group.name, group.type.name))
            group_id = self.cursor.lastrowid
            for entity in group.named_entities:
                self.cursor.execute("INSERT INTO entities (group_id, entity_name) VALUES (?, ?)", (group_id, entity.text))
        self.connection.commit()

    def set_group_names_from_storage(self, named_entity_groups: list[NamedEntityGroup]):
        pass

    def get_groups_persistence(self) -> list[GroupPersistence]:
        pass

    def load_groups_persistence(self):
        self.cursor.execute(
            """
            SELECT g.id, g.name, g.type, e.entity_name
            FROM groups g
            LEFT JOIN entities e ON g.id = e.group_id
        """
        )
        rows = self.cursor.fetchall()

        groups_dict = {}
        for group_id, name, group_type, entity_name in rows:
            if group_id not in groups_dict:
                groups_dict[group_id] = GroupPersistence(name=name, type=group_type, entities_names=[])
            if entity_name:
                groups_dict[group_id].entities_names.append(entity_name)

        return list(groups_dict.values())