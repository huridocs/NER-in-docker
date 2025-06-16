import os
from unittest import TestCase
from pathlib import Path

from configuration import ROOT_PATH
from domain.BoundingBox import BoundingBox
from domain.NamedEntityType import NamedEntityType
from domain.PDFSegment import PDFSegment
from adapters.SQLitePDFsGroupNameRepository import SQLiteGroupsStoreRepository
from ports.PDFToSegmentsRepository import PDFToSegmentsRepository
from use_cases.NamedEntitiesFromPDFUseCase import NamedEntitiesFromPDFUseCase

TEST_DATABASE_NAME = "test_pdf_use_case.db"
TEST_DATABASE_PATH = Path(ROOT_PATH, "data", TEST_DATABASE_NAME)


class MockPDFToSegmentsRepository(PDFToSegmentsRepository):
    @staticmethod
    def get_segments(pdf_path, fast) -> list[PDFSegment]:
        return [
            PDFSegment(
                text="Test Title",
                type="Title",
                page_number=1,
                segment_number=0,
                pdf_name="test.pdf",
                bounding_box=BoundingBox.from_coordinates(1, 2, 3, 4),
            ),
            PDFSegment(
                text="Reference to Test Title",
                type="Text",
                page_number=1,
                segment_number=1,
                pdf_name="test.pdf",
                bounding_box=BoundingBox.from_coordinates(5, 6, 7, 8),
            ),
        ]


class TestNamedEntitiesFromPDFUseCase(TestCase):
    def tearDown(self):
        if TEST_DATABASE_PATH.exists():
            os.remove(TEST_DATABASE_PATH)

    def test_get_reference_groups_with_title_and_reference(self):
        groups_store_repository = SQLiteGroupsStoreRepository(database_name=TEST_DATABASE_NAME)
        pdf_to_segments_repository = MockPDFToSegmentsRepository()
        named_entities_from_pdf_use_case = NamedEntitiesFromPDFUseCase(
            pdf_to_segments_repository=pdf_to_segments_repository, groups_store_repository=groups_store_repository
        )
        pdf_path = Path("test.pdf")
        groups = named_entities_from_pdf_use_case.get_reference_groups(pdf_path)
        self.assertEqual(len(groups), 1)
        group = groups[0]
        self.assertEqual(group.name, "Test Title")
        self.assertEqual(group.type, NamedEntityType.REFERENCE_DESTINATION)
        self.assertIsNotNone(group.pdf_segment)
        self.assertEqual(group.pdf_segment.text, "Test Title")
        self.assertEqual(group.pdf_segment.page_number, 1)
        self.assertEqual(group.pdf_segment.bounding_box.left, 1)
        self.assertEqual(group.pdf_segment.bounding_box.top, 2)
        self.assertEqual(group.pdf_segment.bounding_box.width, 3)
        self.assertEqual(group.pdf_segment.bounding_box.height, 4)
        reference = group.named_entities[0]
        self.assertEqual(reference.text, "Test Title")
        self.assertEqual(reference.type, NamedEntityType.REFERENCE_POINTER)
        self.assertEqual(reference.pdf_segment.text, "Reference to Test Title")
        self.assertEqual(reference.pdf_segment.page_number, 1)
        self.assertEqual(reference.pdf_segment.bounding_box.left, 5)
        self.assertEqual(reference.pdf_segment.bounding_box.top, 6)
        self.assertEqual(reference.pdf_segment.bounding_box.width, 7)
        self.assertEqual(reference.pdf_segment.bounding_box.height, 8)
