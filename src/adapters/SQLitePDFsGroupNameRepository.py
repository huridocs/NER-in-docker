import sqlite3
from pathlib import Path

from adapters.EntityPersistence import EntityPersistence
from adapters.PersistenceReferenceDestination import PersistenceReferenceDestination
from configuration import ROOT_PATH
from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from ports.GroupsStoreRepository import GroupsStoreRepository


class SQLiteGroupsStoreRepository(GroupsStoreRepository):

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
                left INTEGER NOT NULL,
                top INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL
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

    @staticmethod
    def _fetch_existing_reference_groups(cursor) -> list[NamedEntityGroup]:
        cursor.execute("SELECT * FROM reference_destinations")
        rows = cursor.fetchall()
        existing_reference_groups = []
        for row in rows:
            persistence_reference_destination = PersistenceReferenceDestination.from_row(row)
            group = NamedEntityGroup(
                name=persistence_reference_destination.title,
                type=NamedEntityType.REFERENCE_DESTINATION,
                named_entities=[],
                pdf_segment=persistence_reference_destination.get_pdf_segment(),
            )
            existing_reference_groups.append(group)
        return existing_reference_groups

    @staticmethod
    def _insert_new_reference_destinations(cursor, new_groups_destinations: list[NamedEntityGroup]):
        for group in new_groups_destinations:
            if group.pdf_segment:
                cursor.execute(
                    """
                    INSERT INTO reference_destinations (title, page_number, segment_number, pdf_name, left, top, width, height)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        group.name,
                        group.pdf_segment.page_number,
                        group.pdf_segment.segment_number,
                        group.pdf_segment.pdf_name,
                        group.pdf_segment.bounding_box.left,
                        group.pdf_segment.bounding_box.top,
                        group.pdf_segment.bounding_box.width,
                        group.pdf_segment.bounding_box.height,
                    ),
                )

    def update_reference_destinations(self, new_groups_destinations: list[NamedEntityGroup]) -> list[NamedEntityGroup]:
        connection, cursor = self.get_connection()
        existing_reference_groups = self._fetch_existing_reference_groups(cursor)

        group_names = {group.name for group in existing_reference_groups}
        pdf_names = {group.pdf_segment.pdf_name for group in existing_reference_groups if group.pdf_segment}
        new_groups_destinations = [
            group
            for group in new_groups_destinations
            if group.name not in group_names and group.pdf_segment.pdf_name not in pdf_names
        ]

        if not new_groups_destinations:
            return existing_reference_groups

        self._insert_new_reference_destinations(cursor, new_groups_destinations)
        connection.commit()
        combined_groups = existing_reference_groups + new_groups_destinations
        return combined_groups
