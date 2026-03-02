import psycopg2
from ner_in_docker.adapters.EntityPersistence import EntityPersistence
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.Segment import Segment
from ner_in_docker.ports.EntitiesStoreRepository import EntitiesStoreRepository
import os


class PostgresEntitiesStoreRepository(EntitiesStoreRepository):
    def __init__(self, schema_name: str = "public", language: str = "en"):
        self.language = language
        self.schema_name = schema_name
        self.host = os.environ.get("POSTGRES_HOST", "postgres")
        self.port = os.environ.get("POSTGRES_PORT", "5432")
        self.dbname = os.environ.get("POSTGRES_DB", "ner_db")
        self.user = os.environ.get("POSTGRES_USER", "postgres")
        self.password = os.environ.get("POSTGRES_PASSWORD", "postgres")

    def get_connection(self):
        connection = psycopg2.connect(
            host=self.host, port=self.port, dbname=self.dbname, user=self.user, password=self.password
        )
        cursor = connection.cursor()
        return connection, cursor

    def exists_schema(self) -> bool:
        try:
            connection, cursor = self.get_connection()
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", (self.schema_name,))
            exists = cursor.fetchone() is not None
            connection.close()
            return exists
        except Exception:
            return False

    def create_database(self):
        connection, cursor = self.get_connection()

        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema_name}")

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.schema_name}.named_entities (
                id SERIAL PRIMARY KEY,
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
            f"""
            CREATE TABLE IF NOT EXISTS {self.schema_name}.identifiers (
                id SERIAL PRIMARY KEY,
                identifier TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        connection.commit()
        connection.close()

    def get_entities(self) -> list[NamedEntity]:
        if not self.exists_schema():
            return []

        self.create_database()
        connection, cursor = self.get_connection()

        cursor.execute(f"SELECT * FROM {self.schema_name}.named_entities")
        rows = cursor.fetchall()
        entities = [EntityPersistence.from_row(row).to_named_entity() for row in rows]

        connection.close()
        return entities

    def save_entities(self, named_entities: list[NamedEntity]) -> bool:
        if not self.exists_schema():
            self.create_database()
        try:
            connection, cursor = self.get_connection()
            source_ids = set(entity.segment.source_id for entity in named_entities)
            if source_ids:
                format_strings = ",".join(["%s"] * len(source_ids))
                cursor.execute(
                    f"DELETE FROM {self.schema_name}.named_entities WHERE segment_source_id IN ({format_strings})",
                    tuple(source_ids),
                )
                connection.commit()

            for entity in named_entities:
                persistence = EntityPersistence.from_named_entity(entity)
                cursor.execute(
                    f"""
                    INSERT INTO {self.schema_name}.named_entities (
                        type, text, normalized_text, character_start, character_end, group_name,
                        segment_text, segment_page_number, segment_segment_number, segment_type, segment_source_id,
                        segment_bounding_box_left, segment_bounding_box_top, segment_bounding_box_width, segment_bounding_box_height,
                        appearance_count, percentage_to_segment_text, first_type_appearance, last_type_appearance, relevance_percentage
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                        persistence.first_type_appearance,
                        persistence.last_type_appearance,
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
        try:
            connection, cursor = self.get_connection()
            cursor.execute(f"DROP SCHEMA IF EXISTS {self.schema_name} CASCADE")
            connection.commit()
            connection.close()
        except Exception as e:
            print(f"Error deleting database schema: {e}")

    def save_identifier(self, identifier: str) -> bool:
        if not identifier:
            return False

        if not self.exists_schema():
            self.create_database()

        try:
            connection, cursor = self.get_connection()
            cursor.execute(
                f"INSERT INTO {self.schema_name}.identifiers (identifier) VALUES (%s) ON CONFLICT DO NOTHING", (identifier,)
            )
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Error saving identifier: {e}")
            return False

    def is_processed(self, identifier: str) -> bool:
        if not identifier or not self.exists_schema():
            return False

        try:
            connection, cursor = self.get_connection()
            cursor.execute(f"SELECT 1 FROM {self.schema_name}.identifiers WHERE identifier = %s", (identifier,))
            result = cursor.fetchone() is not None
            connection.close()
            return result
        except Exception:
            return False

    def save_segments(self, segments: list[Segment]) -> bool:
        if not self.exists_schema():
            self.create_database()

        try:
            connection, cursor = self.get_connection()

            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.schema_name}.segments (
                    id SERIAL PRIMARY KEY,
                    text TEXT,
                    page_number INTEGER,
                    segment_number INTEGER,
                    type TEXT,
                    source_id TEXT,
                    bounding_box_left INTEGER,
                    bounding_box_top INTEGER,
                    bounding_box_width INTEGER,
                    bounding_box_height INTEGER,
                    page_width INTEGER,
                    page_height INTEGER
                )
            """
            )

            source_ids = set(seg.source_id for seg in segments)
            if source_ids:
                format_strings = ",".join(["%s"] * len(source_ids))
                cursor.execute(
                    f"DELETE FROM {self.schema_name}.segments WHERE source_id IN ({format_strings})", tuple(source_ids)
                )

            for segment in segments:
                cursor.execute(
                    f"""
                    INSERT INTO {self.schema_name}.segments (
                        text, page_number, segment_number, type, source_id,
                        bounding_box_left, bounding_box_top, bounding_box_width, bounding_box_height,
                        page_width, page_height
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        segment.text,
                        segment.page_number,
                        segment.segment_number,
                        segment.type,
                        segment.source_id,
                        segment.bounding_box.left,
                        segment.bounding_box.top,
                        segment.bounding_box.width,
                        segment.bounding_box.height,
                        segment.page_width,
                        segment.page_height,
                    ),
                )

            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Error saving segments: {e}")
            return False
