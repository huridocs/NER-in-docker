from pathlib import Path
from unittest import TestCase
from domain.BoundingBox import BoundingBox
from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity
from domain.PDFSegment import PDFSegment
from ports.PDFToSegmentsRepository import PDFToSegmentsRepository
from use_cases.NamedEntitiesFromPDFUseCase import NamedEntitiesFromPDFUseCase


class DummyPDFToSegmentsRepository(PDFToSegmentsRepository):
    @staticmethod
    def get_segments(pdf_path: Path) -> list[PDFSegment]:
        return [
            PDFSegment(
                text="Maria Rodriguez visited the Louvre Museum.",
                page_number=1,
                segment_number=1,
                pdf_name=pdf_path.name,
                bounding_box=BoundingBox(left=0, top=0, width=0, height=0),
            ),
            PDFSegment(
                text="The Senate passed Resolution No. 122, establishing a set of rules for the impeachment trial.",
                page_number=2,
                segment_number=2,
                pdf_name=pdf_path.name,
                bounding_box=BoundingBox(left=1, top=1, width=1, height=1),
            ),
        ]


class TestNamedEntitiesFromPDFUseCase(TestCase):
    def test_get_entities(self):
        pdf_path: Path = Path("../end_to_end/test_pdfs/test_document.pdf")
        dummy_pdf_to_segment_repository = DummyPDFToSegmentsRepository()
        entities: list[PDFNamedEntity] = NamedEntitiesFromPDFUseCase(dummy_pdf_to_segment_repository).get_entities(pdf_path)

        self.assertEqual(3, len(entities))
        self.assertEqual("Maria Rodriguez", entities[0].text)
        self.assertEqual("Maria Rodriguez", entities[0].normalized_text)
        self.assertEqual(NamedEntityType.PERSON, entities[0].type)
        self.assertEqual(0, entities[0].character_start)
        self.assertEqual(15, entities[0].character_end)
        self.assertEqual(1, entities[0].page_number)
        self.assertEqual(1, entities[0].segment_number)
        self.assertEqual(pdf_path.name, entities[0].pdf_name)
        self.assertEqual(0, entities[0].bounding_box.left)
        self.assertEqual(0, entities[0].bounding_box.top)
        self.assertEqual(0, entities[0].bounding_box.width)
        self.assertEqual(0, entities[0].bounding_box.height)

        self.assertEqual("Resolution No. 122", entities[-1].text)
        self.assertEqual("Resolution No. 122", entities[-1].normalized_text)
        self.assertEqual(NamedEntityType.LAW, entities[-1].type)
        self.assertEqual(18, entities[-1].character_start)
        self.assertEqual(36, entities[-1].character_end)
        self.assertEqual(2, entities[-1].page_number)
        self.assertEqual(2, entities[-1].segment_number)
        self.assertEqual(pdf_path.name, entities[-1].pdf_name)
        self.assertEqual(1, entities[-1].bounding_box.left)
        self.assertEqual(1, entities[-1].bounding_box.top)
        self.assertEqual(1, entities[-1].bounding_box.width)
        self.assertEqual(1, entities[-1].bounding_box.height)
