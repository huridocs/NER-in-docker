import sqlite3
from pathlib import Path

from adapters.EntityPersistence import EntityPersistence
from configuration import ROOT_PATH
from domain.NamedEntity import NamedEntity
from ports.EntitiesStoreRepository import EntitiesStoreRepository


class SQLiteEntitiesStoreRepository(EntitiesStoreRepository):
    def __init__(self, database_name: str = None):
        self.database_name = database_name if database_name else "named_entities.db"
        self.database_path = Path(ROOT_PATH, "data", database_name)

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
            CREATE TABLE IF NOT EXISTS named_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                text TEXT,
                normalized_text TEXT,
                character_start INTEGER,
                character_end INTEGER,
                group_name TEXT,
                segment_text TEXT,
                segment_page_number INTEGER,
                segment_segment_number INTEGER,
                segment_type TEXT,
                segment_source_id TEXT,
                segment_bounding_box_left INTEGER,
                segment_bounding_box_top INTEGER,
                segment_bounding_box_width INTEGER,
                segment_bounding_box_height INTEGER,
                appearance_count INTEGER,
                percentage_to_segment_text INTEGER,
                first_type_appearance BOOLEAN,
                last_type_appearance BOOLEAN,
                relevance_percentage INTEGER
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS identifiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
        connection.close()

    def get_entities(self) -> list[NamedEntity]:
        if not self.exists_database():
            return []

        self.create_database()
        connection, cursor = self.get_connection()

        cursor.execute("SELECT * FROM named_entities")
        rows = cursor.fetchall()
        entities = [EntityPersistence.from_row(row).to_named_entity() for row in rows]

        connection.close()
        return entities

    def save_entities(self, named_entities: list[NamedEntity]) -> bool:
        if not self.exists_database():
            self.create_database()
        try:
            connection, cursor = self.get_connection()
            source_ids = set(entity.segment.source_id for entity in named_entities)
            cursor.execute(
                "DELETE FROM named_entities WHERE segment_source_id IN ({})".format(", ".join("?" for _ in source_ids)),
                tuple(source_ids),
            )
            connection.commit()

            for entity in named_entities:
                persistence = EntityPersistence.from_named_entity(entity)
                cursor.execute(
                    """
                    INSERT INTO named_entities (
                        type, text, normalized_text, character_start, character_end, group_name,
                        segment_text, segment_page_number, segment_segment_number, segment_type, segment_source_id,
                        segment_bounding_box_left, segment_bounding_box_top, segment_bounding_box_width, segment_bounding_box_height,
                        appearance_count, percentage_to_segment_text, first_type_appearance, last_type_appearance, relevance_percentage
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(persistence.type),
                        persistence.text,
                        persistence.normalized_text,
                        persistence.character_start,
                        persistence.character_end,
                        persistence.group_name,
                        persistence.segment_text,
                        persistence.segment_page_number,
                        persistence.segment_segment_number,
                        persistence.segment_type,
                        persistence.segment_source_id,
                        persistence.segment_bounding_box_left,
                        persistence.segment_bounding_box_top,
                        persistence.segment_bounding_box_width,
                        persistence.segment_bounding_box_height,
                        persistence.appearance_count,
                        persistence.percentage_to_segment_text,
                        int(persistence.first_type_appearance),
                        int(persistence.last_type_appearance),
                        persistence.relevance_percentage,
                    ),
                )
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Error saving entities: {e}")
            return False

    def delete_database(self):
        Path(ROOT_PATH, "data", self.database_name).unlink(missing_ok=True)

    def save_identifier(self, identifier: str) -> bool:
        if not identifier:
            return False

        if not self.exists_database():
            self.create_database()

        try:
            connection, cursor = self.get_connection()
            cursor.execute("INSERT OR IGNORE INTO identifiers (identifier) VALUES (?)", (identifier,))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Error saving identifier: {e}")
            return False

    def is_processed(self, identifier: str) -> bool:
        if not identifier or not self.exists_database():
            return False

        connection, cursor = self.get_connection()
        cursor.execute("SELECT 1 FROM identifiers WHERE identifier = ?", (identifier,))
        result = cursor.fetchone() is not None
        connection.close()
        return result
