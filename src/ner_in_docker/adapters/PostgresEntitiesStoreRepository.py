import psycopg2
from ner_in_docker.adapters.EntityPersistence import EntityPersistence
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.Segment import Segment
from ner_in_docker.ports.EntitiesStoreRepository import EntitiesStoreRepository
import os


class PostgresEntitiesStoreRepository(EntitiesStoreRepository):
    def __init__(self, schema_name: str = "public", language: str = "en"):
        self.language = language
        self.schema_name = f"{schema_name}_{language}"
        self.host = os.environ.get("POSTGRES_HOST", "postgres")
        self.port = os.environ.get("POSTGRES_PORT", "5432")
        self.dbname = os.environ.get("POSTGRES_DB", "ner_db")
        self.user = os.environ.get("POSTGRES_USER", "postgres")
        self.password = os.environ.get("POSTGRES_PASSWORD", "postgres")

    def get_connection(self):
        connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )
        cursor = connection.cursor()
        return connection, cursor

    def exists_schema(self) -> bool:
        try:
            connection, cursor = self.get_connection()
            cursor.execute(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
                (self.schema_name,),
            )
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
            CREATE TABLE IF NOT EXISTS {self.schema_name}.named_entities_group (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
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
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.schema_name}.named_entities (
                id SERIAL PRIMARY KEY,
                type TEXT NOT NULL,
                text TEXT,
                normalized_text TEXT,
                character_start INTEGER,
                character_end INTEGER,
                group_id INTEGER REFERENCES {self.schema_name}.named_entities_group(id),
                segment_id INTEGER REFERENCES {self.schema_name}.segments(id),
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
            source_ids = set(entity.segment.source_id for entity in named_entities if entity.segment is not None)
            if source_ids:
                format_strings = ",".join(["%s"] * len(source_ids))
                cursor.execute(
                    f"""DELETE FROM {self.schema_name}.named_entities 
                    WHERE segment_id IN (SELECT id FROM {self.schema_name}.segments WHERE source_id IN ({format_strings}))""",
                    tuple(source_ids),
                )
                connection.commit()

            for entity in named_entities:
                persistence = EntityPersistence.from_named_entity(entity)

                segment_id = None
                if entity.segment and entity.segment.source_id:
                    cursor.execute(
                        f"SELECT id FROM {self.schema_name}.segments WHERE source_id = %s",
                        (entity.segment.source_id,),
                    )
                    seg_row = cursor.fetchone()
                    if seg_row:
                        segment_id = seg_row[0]

                cursor.execute(
                    f"""
                    INSERT INTO {self.schema_name}.named_entities (
                        type, text, normalized_text, character_start, character_end, group_id,
                        segment_id,
                        appearance_count, percentage_to_segment_text, first_type_appearance, last_type_appearance, relevance_percentage
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(persistence.type),
                        persistence.text,
                        persistence.normalized_text,
                        persistence.character_start,
                        persistence.character_end,
                        None,
                        segment_id,
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
                f"INSERT INTO {self.schema_name}.identifiers (identifier) VALUES (%s) ON CONFLICT DO NOTHING",
                (identifier,),
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
            cursor.execute(
                f"SELECT 1 FROM {self.schema_name}.identifiers WHERE identifier = %s",
                (identifier,),
            )
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
                    f"DELETE FROM {self.schema_name}.segments WHERE source_id IN ({format_strings})",
                    tuple(source_ids),
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

            for source_id in source_ids:
                cursor.execute(
                    f"INSERT INTO {self.schema_name}.identifiers (identifier) VALUES (%s) ON CONFLICT DO NOTHING",
                    (source_id,),
                )

            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Error saving segments: {e}")
            return False

    def get_segments(self, identifier: str) -> list[Segment]:
        if not self.exists_schema():
            return []

        try:
            connection, cursor = self.get_connection()
            cursor.execute(
                f"SELECT * FROM {self.schema_name}.segments WHERE source_id = %s",
                (identifier,),
            )
            rows = cursor.fetchall()
            connection.close()

            segments = []
            for row in rows:
                from pdf_features import Rectangle

                segments.append(
                    Segment(
                        text=row[1],
                        page_number=row[2],
                        segment_number=row[3],
                        type=row[4],
                        source_id=row[5],
                        bounding_box=Rectangle.from_width_height(left=row[6], top=row[7], width=row[8], height=row[9]),
                        page_width=row[10],
                        page_height=row[11],
                    )
                )
            return segments
        except Exception as e:
            print(f"Error getting segments: {e}")
            return []

    def get_identifiers(self) -> list[str]:
        if not self.exists_schema():
            return []

        try:
            connection, cursor = self.get_connection()
            cursor.execute(f"SELECT identifier FROM {self.schema_name}.identifiers")
            rows = cursor.fetchall()
            connection.close()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Error getting identifiers: {e}")
            return []

    def save_reference(self, segment_id: int | None, reference_text: str, to_text: str) -> bool:
        self.create_database()

        try:
            connection, cursor = self.get_connection()

            # Insert destination group if not exists
            cursor.execute(
                f"""
                INSERT INTO {self.schema_name}.named_entities_group (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
                RETURNING id
                """,
                (to_text,),
            )
            result = cursor.fetchone()
            if result is not None:
                destination_id = result[0]
            else:
                cursor.execute(
                    f"SELECT id FROM {self.schema_name}.named_entities_group WHERE name = %s",
                    (to_text,),
                )
                row = cursor.fetchone()
                destination_id = row[0] if row is not None else None

            # Get segment details - now we just use segment_id directly

            cursor.execute(
                f"""
                INSERT INTO {self.schema_name}.named_entities (
                    type, text, normalized_text, character_start, character_end, group_id,
                    segment_id,
                    appearance_count, percentage_to_segment_text, first_type_appearance, last_type_appearance, relevance_percentage
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    "Reference",
                    reference_text,
                    reference_text,
                    0,
                    0,
                    destination_id,
                    segment_id,
                    0,
                    0,
                    False,
                    False,
                    0,
                ),
            )
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Error saving reference: {e}")
            return False

    def get_references(self) -> list:
        if not self.exists_schema():
            return []

        try:
            connection, cursor = self.get_connection()
            # Fetch destinations
            cursor.execute(f"SELECT id, name FROM {self.schema_name}.named_entities_group ORDER BY id")
            destinations = cursor.fetchall()

            groups = []
            from ner_in_docker.domain.NamedEntityGroup import NamedEntityGroup
            from ner_in_docker.domain.NamedEntity import NamedEntity
            from ner_in_docker.domain.NamedEntityType import NamedEntityType
            from pdf_features import Rectangle
            from ner_in_docker.domain.Segment import Segment

            for dest_id, dest_name in destinations:
                group = NamedEntityGroup(
                    type=NamedEntityType.REFERENCE,
                    name=dest_name,
                    segment=None,
                    named_entities=[],
                )

                cursor.execute(
                    f"""
                    SELECT ne.id, ne.text, s.text, s.page_number, s.segment_number, s.type, s.source_id, s.bounding_box_left, s.bounding_box_top, s.bounding_box_width, s.bounding_box_height
                    FROM {self.schema_name}.named_entities ne
                    LEFT JOIN {self.schema_name}.segments s ON ne.segment_id = s.id
                    WHERE ne.group_id = %s AND ne.type = 'Reference'
                    ORDER BY ne.id
                    """,
                    (dest_id,),
                )

                refs = cursor.fetchall()
                for ref in refs:
                    ref_id, ref_text = ref[0], ref[1]
                    (
                        segment_text,
                        segment_page_number,
                        segment_segment_number,
                        segment_type,
                        segment_source_id,
                        segment_bounding_box_left,
                        segment_bounding_box_top,
                        segment_bounding_box_width,
                        segment_bounding_box_height,
                    ) = (
                        ref[2],
                        ref[3],
                        ref[4],
                        ref[5],
                        ref[6],
                        ref[7],
                        ref[8],
                        ref[9],
                        ref[10],
                    )

                    segment = None
                    if segment_text is not None or segment_source_id is not None:
                        segment = Segment(
                            text=segment_text if segment_text else "",
                            page_number=(segment_page_number if segment_page_number else 0),
                            segment_number=(segment_segment_number if segment_segment_number else 0),
                            type=segment_type if segment_type else "Text",
                            source_id=segment_source_id if segment_source_id else "",
                            bounding_box=Rectangle.from_width_height(
                                left=(segment_bounding_box_left if segment_bounding_box_left else 0),
                                top=(segment_bounding_box_top if segment_bounding_box_top else 0),
                                width=(segment_bounding_box_width if segment_bounding_box_width else 0),
                                height=(segment_bounding_box_height if segment_bounding_box_height else 0),
                            ),
                        )

                    entity = NamedEntity(type=NamedEntityType.REFERENCE, text=ref_text, segment=segment)
                    group.named_entities.append(entity)

                groups.append(group.model_dump())

            connection.close()
            return groups
        except Exception as e:
            print(f"Error getting references: {e}")
            return []

    def delete_reference(self, reference_id: int) -> bool:
        if not self.exists_schema():
            return False

        try:
            connection, cursor = self.get_connection()
            cursor.execute(
                f"DELETE FROM {self.schema_name}.named_entities WHERE id = %s AND type = 'Reference'",
                (reference_id,),
            )
            cursor.execute(
                f"""
                DELETE FROM {self.schema_name}.named_entities_group
                WHERE id NOT IN (SELECT DISTINCT group_id FROM {self.schema_name}.named_entities WHERE type = 'Reference' AND group_id IS NOT NULL)
            """
            )
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(f"Error deleting reference: {e}")
            return False
