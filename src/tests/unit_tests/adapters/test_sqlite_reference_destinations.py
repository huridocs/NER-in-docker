import os
from pathlib import Path
from unittest import TestCase

from adapters.SQLitePDFsGroupNameRepository import SQLiteGroupsStoreRepository
from configuration import ROOT_PATH

TEST_DATABASE_NAME = "test_reference_destinations.db"
TEST_DATABASE_PATH = Path(ROOT_PATH, "data", TEST_DATABASE_NAME)


class TestSQLiteReferenceDestinations(TestCase):
    def setUp(self):
        if TEST_DATABASE_PATH.exists():
            os.remove(TEST_DATABASE_PATH)
        self.repo = SQLiteGroupsStoreRepository(TEST_DATABASE_NAME)
        self.repo.create_database()

    def tearDown(self):
        if TEST_DATABASE_PATH.exists():
            os.remove(TEST_DATABASE_PATH)

    def test_get_reference_destinations(self):
        connection, cursor = self.repo.get_connection()
        cursor.execute(
            """
            INSERT INTO reference_destinations (title, page_number, segment_number, pdf_name, left, top, width, height)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("Section 1", 1, 0, "test.pdf", 10, 20, 30, 40),
        )
        connection.commit()
        groups = self.repo.update_reference_destinations([])
        self.assertEqual(len(groups), 1)
        group = groups[0]
        self.assertEqual(group.name, "Section 1")
        self.assertEqual(group.type.name, "REFERENCE_DESTINATION")
        self.assertIsNotNone(group.pdf_segment)
        self.assertEqual(group.pdf_segment.page_number, 1)
        self.assertEqual(group.pdf_segment.bounding_box.left, 10)
        self.assertEqual(group.pdf_segment.bounding_box.top, 20)
        self.assertEqual(group.pdf_segment.bounding_box.width, 30)
        self.assertEqual(group.pdf_segment.bounding_box.height, 40)
