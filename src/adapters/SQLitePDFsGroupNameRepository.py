import sqlite3
from pathlib import Path

from adapters.EntityPersistence import EntityPersistence
from adapters.PersistenceReferenceDestination import PersistenceReferenceDestination
from configuration import ROOT_PATH
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity
from domain.PDFSegment import PDFSegment
from ports.PDFsGroupNameRepository import PDFsGroupNameRepository


class SQLitePDFsGroupNameRepository(PDFsGroupNameRepository):

    def __init__(self, database_name: str = "named_entities.db"):
        self.database_name = database_name
        self.database_path = Path(ROOT_PATH, "data", database_name)
        self.groups_in_database: list[NamedEntityGroup] = self.load_groups_from_database()

    def get_connection(self):
        connection = sqlite3.connect(self.database_path)
        cursor = connection.cursor()
        return connection, cursor

    def exists_database(self) -> bool:
        return self.database_path.exists()

    def create_database(self):
        if self.exists_database():
            return

        connection, cursor = self.get_connection()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_text TEXT NOT NULL
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reference_destinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                segment_number INTEGER NOT NULL,
                pdf_name TEXT NOT NULL,
                bounding_box_x1 REAL NOT NULL,
                bounding_box_y1 REAL NOT NULL,
                bounding_box_x2 REAL NOT NULL,
                bounding_box_y2 REAL NOT NULL
            )
        """
        )

        connection.commit()
        connection.close()

    def delete_database(self):
        Path(ROOT_PATH, "data", self.database_name).unlink(missing_ok=True)

    def save_group(self, group: NamedEntityGroup):
        self.create_database()
        connection, cursor = self.get_connection()
        for entity in group.named_entities:
            cursor.execute(
                """INSERT INTO entities (group_name, entity_type, entity_text) VALUES (?, ?, ?)""",
                (group.name, str(entity.type), entity.text),
            )
        connection.commit()
        self.groups_in_database.append(group)

    def group_exists_in_database(self, group: NamedEntityGroup) -> tuple[bool, NamedEntityGroup]:
        for group_in_database in self.groups_in_database:
            if group_in_database.is_same_group(group):
                group.name = group_in_database.name
                return True, group

        return False, group

    def update_groups_by_old_groups(self, old_named_entity_groups: list[NamedEntityGroup]):
        new_named_entity_groups = []
        for old_group in old_named_entity_groups:
            group_exists, new_group = self.group_exists_in_database(old_group)
            new_named_entity_groups.append(new_group)
            if not group_exists:
                self.save_group(new_group)

        return new_named_entity_groups

    def get_groups_persistence(self) -> list[NamedEntityGroup]:
        return self.groups_in_database

    def load_groups_from_database(self) -> list[NamedEntityGroup]:
        self.create_database()

        connection, cursor = self.get_connection()

        cursor.execute("SELECT * FROM entities")
        rows = cursor.fetchall()
        entity_persistence = [EntityPersistence.from_row(row) for row in rows]
        groups = {}

        for persistence_entity in entity_persistence:
            groups.setdefault(
                persistence_entity.group_name,
                NamedEntityGroup(
                    name=persistence_entity.group_name,
                    type=NamedEntityType(persistence_entity.entity_type),
                    named_entities=[],
                ),
            )
            groups[persistence_entity.group_name].named_entities.append(persistence_entity.to_named_entity())

        return list(groups.values())

    def get_reference_destinations(self) -> list[NamedEntityGroup]:
        connection, cursor = self.get_connection()
        cursor.execute("SELECT * FROM reference_destinations")
        rows = cursor.fetchall()
        reference_groups = []
        for row in rows:
            persistence_reference_destination = PersistenceReferenceDestination.from_row(row)
            group = NamedEntityGroup(
                name=persistence_reference_destination.title,
                type=NamedEntityType.REFERENCE_DESTINATION,
                named_entities=[],
                pdf_segment=persistence_reference_destination.get_pdf_segment()
            )
            reference_groups.append(group)
        return reference_groups
