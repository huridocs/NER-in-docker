from unittest import TestCase

from domain.NamedEntityGroup import NamedEntityGroup
from domain.NamedEntityType import NamedEntityType


class TestNamedEntityGroup(TestCase):
    def test_exact_reference_match(self):
        group = NamedEntityGroup(name="Test reference", type=NamedEntityType.REFERENCE_DESTINATION)
        matches = group.get_references_in_text("Test reference")
        self.assertTrue(len(matches) > 0)
        self.assertEqual((0, 14), matches[0])

    def test_no_reference_for_non_reference_destination_type(self):
        group = NamedEntityGroup(name="Test Section", type=NamedEntityType.PERSON)
        matches = group.get_references_in_text("Some text mentioning Test Section")
        self.assertEqual(matches, [])

    def test_reference_found_when_name_in_text(self):
        group = NamedEntityGroup(name="Section 1.1", type=NamedEntityType.REFERENCE_DESTINATION)
        text = "This document refers to Section 1.1 for more details."
        matches = group.get_references_in_text(text)
        self.assertTrue(len(matches) > 0)
        self.assertEqual((text.find("Section 1.1"), text.find("Section 1.1") + len("Section 1.1")), matches[0])

    def test_no_reference_when_name_not_in_text(self):
        group = NamedEntityGroup(name="Chapter 5", type=NamedEntityType.REFERENCE_DESTINATION)
        matches = group.get_references_in_text("This is a completely unrelated text.")
        self.assertEqual(matches, [])

    def test_no_reference_when_name_is_substring_of_other(self):
        group = NamedEntityGroup(name="Section 1", type=NamedEntityType.REFERENCE_DESTINATION)
        text = "Please see Section 1.1 for details."
        matches = group.get_references_in_text(text)
        self.assertEqual(matches, [])

    def test_no_reference_with_empty_text(self):
        group = NamedEntityGroup(name="Appendix A", type=NamedEntityType.REFERENCE_DESTINATION)
        matches = group.get_references_in_text("")
        self.assertEqual(matches, [])

    def test_no_reference_when_text_too_short(self):
        group = NamedEntityGroup(name="Appendix A", type=NamedEntityType.REFERENCE_DESTINATION)
        matches = group.get_references_in_text(" A")
        self.assertEqual(matches, [])

    def test_reference_with_colon_title_and_partial_reference(self):
        group = NamedEntityGroup(name="Document 3: Advanced Research", type=NamedEntityType.REFERENCE_DESTINATION)
        text = 'These granular results expand upon the "Advanced Research" presented in Document 3'
        matches = group.get_references_in_text(text)
        self.assertTrue(len(matches) > 0)

    def test_reference_with_colon_title_and_first_part_only(self):
        group = NamedEntityGroup(name="Document 3: Advanced Research", type=NamedEntityType.REFERENCE_DESTINATION)
        text = 'These granular results expand upon the presented in Document 3'
        matches = group.get_references_in_text(text)
        self.assertTrue(len(matches) > 0)

    def test_no_reference_for_numbered_title_with_only_partial_word(self):
        group = NamedEntityGroup(name="4. Results Interpretation", type=NamedEntityType.REFERENCE_DESTINATION)
        text = (
            "The analysis yielded several significant findings, indicating both expected outcomes and some "
            "surprising correlations within the data. Interpretation and it findings will inform our strategic decisions moving "
            "forward."
        )
        matches = group.get_references_in_text(text)
        self.assertEqual(matches, [])

    def test_reference_for_numbered_title_with_full_title(self):
        group = NamedEntityGroup(name="4. Results Interpretation", type=NamedEntityType.REFERENCE_DESTINATION)
        text = (
            "The analysis yielded several significant findings, indicating both expected outcomes and some "
            "surprising correlations within the data. Results Interpretation and it findings will inform our strategic decisions moving "
            "forward."
        )
        matches = group.get_references_in_text(text)
        self.assertTrue(len(matches) > 0)

    def test_multiple_references_to_same_title(self):
        group = NamedEntityGroup(name="Section 2.1", type=NamedEntityType.REFERENCE_DESTINATION)
        text = "Section 2.1 is important. See also Section 2.1 for more details."
        matches = group.get_references_in_text(text)
        self.assertEqual(2, len(matches))
        self.assertEqual((0, 11), matches[0])
        self.assertEqual((35, 46), matches[1])
