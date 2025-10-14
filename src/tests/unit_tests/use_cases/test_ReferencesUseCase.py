from unittest import TestCase
from pathlib import Path

from ner_in_docker.configuration import ROOT_PATH
from ner_in_docker.domain.BoundingBox import BoundingBox
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.NamedEntityType import NamedEntityType
from ner_in_docker.domain.Segment import Segment
from ner_in_docker.domain.TokenType import TokenType
from ner_in_docker.use_cases.ReferencesUseCase import ReferencesUseCase

TEST_DATABASE_NAME = "test_pdf_use_case.db"
TEST_DATABASE_PATH = Path(ROOT_PATH, "data", TEST_DATABASE_NAME)


class TestReferencesUseCase(TestCase):
    def test_reference_when_no_entities(self):
        segment = Segment.from_text(text="Sample text with no references.")
        reference_entities_use_case = ReferencesUseCase([])
        entities = reference_entities_use_case.get_entities_from_segments([segment])
        self.assertEqual([], entities)

    def test_return_title_entities(self):
        segments = [
            Segment(
                text="Test Title",
                type="Title",
                page_number=1,
                segment_number=0,
                source_id="test.pdf",
                bounding_box=BoundingBox.from_coordinates(1, 2, 3, 4),
            ),
            Segment(
                text="Reference to Test Title",
                type="Text",
                page_number=1,
                segment_number=1,
                source_id="test.pdf",
                bounding_box=BoundingBox.from_coordinates(5, 6, 7, 8),
            ),
        ]
        references_use_case = ReferencesUseCase()
        named_entities = references_use_case.get_entities_from_segments(segments)
        self.assertEqual(2, len(named_entities))
        # Assert the title entity
        title_entity = next(e for e in named_entities if e.segment.text == "Test Title")
        self.assertEqual(title_entity.text, "Test Title")
        self.assertEqual(title_entity.type, NamedEntityType.REFERENCE)
        self.assertEqual(title_entity.segment.page_number, 1)
        self.assertEqual(title_entity.segment.bounding_box.left, 1)
        self.assertEqual(title_entity.segment.bounding_box.top, 2)
        self.assertEqual(title_entity.segment.bounding_box.width, 3)
        self.assertEqual(title_entity.segment.bounding_box.height, 4)
        self.assertEqual(title_entity.character_start, 0)
        self.assertEqual(title_entity.character_end, len("Test Title"))
        # Assert the reference entity
        ref_entity = next(e for e in named_entities if e.segment.text == "Reference to Test Title")
        self.assertEqual(ref_entity.text, "Test Title")
        self.assertEqual(ref_entity.type, NamedEntityType.REFERENCE)
        self.assertEqual(ref_entity.segment.page_number, 1)
        self.assertEqual(ref_entity.segment.bounding_box.left, 5)
        self.assertEqual(ref_entity.segment.bounding_box.top, 6)
        self.assertEqual(ref_entity.segment.bounding_box.width, 7)
        self.assertEqual(ref_entity.segment.bounding_box.height, 8)
        self.assertEqual(ref_entity.character_start, 13)
        self.assertEqual(ref_entity.character_end, 23)

    def test_reference_when_same_text(self):
        segment_destination = Segment.from_text(text="Section 1")
        reference_destinations_entities = [
            NamedEntity(
                type=NamedEntityType.REFERENCE,
                text="Section 1",
                character_start=0,
                character_end=9,
                segment=segment_destination,
                relevance_percentage=100,
            )
        ]
        reference_entities_use_case = ReferencesUseCase(reference_destinations_entities)
        segment_pointer = Segment.from_text(text="Section 1")
        entities = reference_entities_use_case.get_entities_from_segments([segment_pointer])
        self.assertEqual(1, len(entities))
        self.assertEqual("Section 1", entities[0].text)
        self.assertEqual(NamedEntityType.REFERENCE, entities[0].type)
        self.assertEqual(0, entities[0].character_start)
        self.assertEqual(9, entities[0].character_end)
        self.assertEqual("Section 1", entities[0].segment.text)

    def test_reference_when_title_in_text(self):
        segment_destination = Segment.from_text(text="Section 1")
        reference_destinations_entities = [
            NamedEntity(
                type=NamedEntityType.REFERENCE,
                text="Section 1",
                character_start=0,
                character_end=9,
                segment=segment_destination,
                relevance_percentage=100,
            )
        ]
        reference_entities_use_case = ReferencesUseCase(reference_destinations_entities)
        segment_pointer = Segment.from_text(text="referencing the Section 1")
        segment_pointer.bounding_box.left = 10
        segment_pointer.page_number = 11
        entities = reference_entities_use_case.get_entities_from_segments([segment_pointer])
        self.assertEqual(1, len(entities))
        self.assertEqual("Section 1", entities[0].text)
        self.assertEqual(NamedEntityType.REFERENCE, entities[0].type)
        self.assertEqual(16, entities[0].character_start)
        self.assertEqual(25, entities[0].character_end)
        self.assertEqual(11, entities[0].segment.page_number)
        self.assertEqual(10, entities[0].segment.bounding_box.left)
        self.assertEqual("referencing the Section 1", entities[0].segment.text)

    def test_two_references_in_one_segment(self):
        segment_destination1 = Segment.from_text(text="Section 1")
        segment_destination2 = Segment.from_text(text="Section 2")
        reference_destinations_entities = [
            NamedEntity(
                type=NamedEntityType.REFERENCE,
                text="Section 1",
                character_start=0,
                character_end=9,
                segment=segment_destination1,
                relevance_percentage=100,
            ),
            NamedEntity(
                type=NamedEntityType.REFERENCE,
                text="Section 2",
                character_start=0,
                character_end=9,
                segment=segment_destination2,
                relevance_percentage=100,
            ),
        ]
        reference_entities_use_case = ReferencesUseCase(reference_destinations_entities)
        segment_pointer = Segment.from_text(text="referencing Section 1 and Section 2")
        segment_pointer.bounding_box.left = 20
        segment_pointer.page_number = 22
        entities = reference_entities_use_case.get_entities_from_segments([segment_pointer])
        self.assertEqual(2, len(entities))
        # Check first entity
        self.assertEqual("Section 1", entities[0].text)
        self.assertEqual(NamedEntityType.REFERENCE, entities[0].type)
        self.assertEqual(12, entities[0].character_start)
        self.assertEqual(21, entities[0].character_end)
        self.assertEqual(22, entities[0].segment.page_number)
        self.assertEqual(20, entities[0].segment.bounding_box.left)
        self.assertEqual("referencing Section 1 and Section 2", entities[0].segment.text)

        # Check second entity
        self.assertEqual("Section 2", entities[1].text)
        self.assertEqual(NamedEntityType.REFERENCE, entities[1].type)
        self.assertEqual(26, entities[1].character_start)
        self.assertEqual(35, entities[1].character_end)
        self.assertEqual(22, entities[1].segment.page_number)
        self.assertEqual(20, entities[1].segment.bounding_box.left)
        self.assertEqual("referencing Section 1 and Section 2", entities[1].segment.text)

    def test_avoid_same_word_two_references(self):
        text = 'The capabilities of these algorithms build directly on the "Analysis Techniques" discussed'
        named_entities_destination = [
            NamedEntity(
                type=NamedEntityType.REFERENCE,
                text="3. Phase 2: Analysis",
                character_start=0,
                character_end=len("Analysis Techniques"),
                segment=Segment.from_text(text=text),
                relevance_percentage=100,
                segment_type=TokenType.TITLE,
            ),
            NamedEntity(
                type=NamedEntityType.REFERENCE,
                text="3. Analysis Techniques",
                character_start=0,
                character_end=len("Analysis"),
                segment=Segment.from_text(text=text),
                relevance_percentage=100,
                segment_type=TokenType.TITLE,
            ),
        ]
        entities = ReferencesUseCase(named_entities_destination).get_entities(Segment.from_text(text=text))
        self.assertEqual(1, len(entities))
        self.assertEqual('"Analysis Techniques"', entities[0].text)
