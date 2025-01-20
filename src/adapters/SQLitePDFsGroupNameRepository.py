import sqlite3
from os import remove
from pathlib import Path
from adapters.GroupPersistence import GroupPersistence
from configuration import ROOT_PATH
from domain.NamedEntity import NamedEntity
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from ports.PDFsGroupNameRepository import PDFsGroupNameRepository


class SQLitePDFsGroupNameRepository(PDFsGroupNameRepository):

    def __init__(self, database_name: str = "named_entities.db"):
        self.database_name = database_name
        self.connection = sqlite3.connect(Path(ROOT_PATH, "data", database_name))
        self.cursor = self.connection.cursor()
        self.create_database()
        self.saved_groups: list[NamedEntityGroup] = self.load_groups_persistence()

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
                entity_text TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        """
        )
        self.connection.commit()

    def delete_database(self):
        if Path(ROOT_PATH, "data", self.database_name).exists():
            remove((Path(ROOT_PATH, "data", self.database_name)))

    def save_group(self, group: [NamedEntityGroup]):
        self.cursor.execute("INSERT INTO groups (name, type) VALUES (?, ?)", (group.name, group.type.name))
        group_id = self.cursor.lastrowid
        for entity in group.named_entities:
            self.cursor.execute("INSERT INTO entities (group_id, entity_text) VALUES (?, ?)", (group_id, entity.text))
        self.connection.commit()

    def group_exists_in_database(self, group: NamedEntityGroup) -> tuple[bool, NamedEntityGroup]:
        for group_in_database in self.saved_groups:
            if group_in_database.is_same_group(group):
                group.name = group_in_database.name
                return True, group_in_database

        return False, group

    def set_group_names_from_storage(self, old_named_entity_groups: list[NamedEntityGroup]):
        new_named_entity_groups = []
        for old_group in old_named_entity_groups:
            group_exists, new_group = self.group_exists_in_database(old_group)
            new_named_entity_groups.append(new_group)
            if not group_exists:
                self.save_group(new_group)

        return new_named_entity_groups

    def get_groups_persistence(self) -> list[NamedEntityGroup]:
        return self.saved_groups

    def load_groups_persistence(self):
        self.cursor.execute(
            """
            SELECT g.id, g.name, g.type, e.entity_text
            FROM groups g
            LEFT JOIN entities e ON g.id = e.group_id
        """
        )
        rows = self.cursor.fetchall()

        groups_dict = {}
        for group_id, name, group_type, entity_text in rows:
            if group_id not in groups_dict:
                groups_dict[group_id] = GroupPersistence(
                    name=name, type=group_type, entities_names=[]
                ).to_named_entity_group()
            if entity_text:
                groups_dict[group_id].named_entities.append(NamedEntity(text=entity_text, type=NamedEntityType(group_type)))

        return list(groups_dict.values())
