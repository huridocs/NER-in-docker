from unittest import TestCase

from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType
from use_cases.ReferenceEntitiesFromPDFUseCase import ReferenceEntitiesFromPDFUseCase
from domain.PDFSegment import PDFSegment


class TestReferenceEntitiesFromPDFUseCase(TestCase):
    def test_reference_when_no_groups(self):
        pdf_segment = PDFSegment.from_text(text="Sample text with no references.")
        reference_entities_use_case = ReferenceEntitiesFromPDFUseCase()
        entities = reference_entities_use_case.get_entities(pdf_segment)
        self.assertEqual([], entities)

    def test_reference_when_same_text(self):
        segment_destination = PDFSegment.from_text(text="Section 1")
        reference_destinations_groups = [
            NamedEntityGroup(name="Section 1", type=NamedEntityType.REFERENCE_DESTINATION, pdf_segment=segment_destination)
        ]
        reference_entities_use_case = ReferenceEntitiesFromPDFUseCase(reference_destinations_groups)

        segment_pointer = PDFSegment.from_text(text="Section 1")
        entities = reference_entities_use_case.get_entities(segment_pointer)

        self.assertEqual(1, len(entities))
        self.assertEqual("Section 1", entities[0].text)
        self.assertEqual(NamedEntityType.REFERENCE_POINTER, entities[0].type)
        self.assertEqual(0, entities[0].character_start)
        self.assertEqual(9, entities[0].character_end)
        self.assertEqual(0, entities[0].pdf_segment.page_number)
        self.assertEqual(0, entities[0].pdf_segment.bounding_box.left)
        self.assertEqual("Section 1", entities[0].pdf_segment.text)

    def test_reference_when_title_in_text(self):
        segment_destination = PDFSegment.from_text(text="Section 1")
        reference_destinations_groups = [
            NamedEntityGroup(name="Section 1", type=NamedEntityType.REFERENCE_DESTINATION, pdf_segment=segment_destination)
        ]
        reference_entities_use_case = ReferenceEntitiesFromPDFUseCase(reference_destinations_groups)

        segment_pointer = PDFSegment.from_text(text="referencing the Section 1")
        segment_pointer.bounding_box.left = 10
        segment_pointer.page_number = 11
        entities = reference_entities_use_case.get_entities(segment_pointer)

        self.assertEqual(1, len(entities))
        self.assertEqual("Section 1", entities[0].text)
        self.assertEqual(NamedEntityType.REFERENCE_POINTER, entities[0].type)
        self.assertEqual(16, entities[0].character_start)
        self.assertEqual(25, entities[0].character_end)
        self.assertEqual(11, entities[0].pdf_segment.page_number)
        self.assertEqual(10, entities[0].pdf_segment.bounding_box.left)
        self.assertEqual("referencing the Section 1", entities[0].pdf_segment.text)

    def test_two_references_in_one_segment(self):
        segment_destination1 = PDFSegment.from_text(text="Section 1")
        segment_destination2 = PDFSegment.from_text(text="Section 2")
        reference_destinations_groups = [
            NamedEntityGroup(name="Section 1", type=NamedEntityType.REFERENCE_DESTINATION, pdf_segment=segment_destination1),
            NamedEntityGroup(name="Section 2", type=NamedEntityType.REFERENCE_DESTINATION, pdf_segment=segment_destination2),
        ]
        reference_entities_use_case = ReferenceEntitiesFromPDFUseCase(reference_destinations_groups)

        segment_pointer = PDFSegment.from_text(text="referencing Section 1 and Section 2")
        segment_pointer.bounding_box.left = 20
        segment_pointer.page_number = 22
        entities = reference_entities_use_case.get_entities(segment_pointer)

        self.assertEqual(2, len(entities))

        # Check first entity
        self.assertEqual("Section 1", entities[0].text)
        self.assertEqual(NamedEntityType.REFERENCE_POINTER, entities[0].type)
        self.assertEqual(12, entities[0].character_start)
        self.assertEqual(21, entities[0].character_end)
        self.assertEqual(22, entities[0].pdf_segment.page_number)
        self.assertEqual(20, entities[0].pdf_segment.bounding_box.left)
        self.assertEqual("referencing Section 1 and Section 2", entities[0].pdf_segment.text)

        # Check second entity
        self.assertEqual("Section 2", entities[1].text)
        self.assertEqual(NamedEntityType.REFERENCE_POINTER, entities[1].type)
        self.assertEqual(26, entities[1].character_start)
        self.assertEqual(35, entities[1].character_end)
        self.assertEqual(22, entities[1].pdf_segment.page_number)
        self.assertEqual(20, entities[1].pdf_segment.bounding_box.left)
        self.assertEqual("referencing Section 1 and Section 2", entities[1].pdf_segment.text)
