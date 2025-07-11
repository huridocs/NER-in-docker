from pathlib import Path
from unittest import TestCase
import requests

from configuration import ROOT_PATH, SRC_PATH
from domain.NamedEntityType import NamedEntityType
from drivers.rest.response_entities.GroupResponse import GroupResponse
from drivers.rest.response_entities.NamedEntityResponse import NamedEntityResponse
from drivers.rest.response_entities.NamedEntityResponse import NamedEntityResponse


class TestEndToEnd(TestCase):
    service_url = "http://localhost:5070"

    @staticmethod
    def similar_value(value: int):
        return [value - 1, value, value + 1]

    def test_empty_query(self):
        result = requests.post(self.service_url)

        self.assertEqual(400, result.status_code)
        self.assertEqual("No file or text provided", result.json()["detail"])

    def test_empty_text_query(self):
        data = {"text": ""}
        result = requests.post(self.service_url, data=data)

        self.assertEqual(200, result.status_code)
        self.assertEqual([], result.json()["entities"])
        self.assertEqual([], result.json()["groups"])

    def test_wrong_pdf(self):
        pdf_path = Path(SRC_PATH) / "tests" / "end_to_end" / "test_pdfs" / "not_a_pdf.pdf"

        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            result = requests.post(self.service_url, files=files)

        self.assertEqual(400, result.status_code)
        self.assertEqual("Unprocessable PDF file", result.json()["detail"])

    def test_text_extraction(self):
        text = (
            "The International Space Station past above Tokyo on 12 June 2025. "
            "Maria Rodriguez was in the Senate when Resolution No. 122 passed on twelve of June 2025."
        )
        data = {"text": text}
        result = requests.post(self.service_url, data=data)

        response_data = result.json()
        entities = response_data["entities"]
        groups = response_data["groups"]

        self.assertEqual(200, result.status_code)
        self.assertEqual(6, len(entities))

        expected_entities = [
            {"text": "Tokyo", "type": "LOCATION", "group_name": "Tokyo"},
            {"text": "12 June 2025", "type": "DATE", "group_name": "2025-06-12"},
            {"text": "Maria Rodriguez", "type": "PERSON", "group_name": "Maria Rodriguez"},
            {"text": "Senate", "type": "ORGANIZATION", "group_name": "Senate"},
            {"text": "Resolution No. 122", "type": "LAW", "group_name": "Resolution No. 122"},
            {"text": "twelve of June 2025", "type": "DATE", "group_name": "2025-06-12"},
        ]

        for i, expected in enumerate(expected_entities):
            entity = entities[i]
            self.assertIn("text", entity)
            self.assertIn("type", entity)
            self.assertIn("group_name", entity)
            self.assertIn("segment", entity)
            self.assertIn("relevance_percentage", entity)
            self.assertIn("source_id", entity)
            self.assertIn("page_number", entity["segment"])
            self.assertIn("segment_number", entity["segment"])
            self.assertIn("character_start", entity["segment"])
            self.assertIn("character_end", entity["segment"])
            self.assertEqual(expected["text"], entity["text"])
            self.assertEqual(expected["type"], entity["type"])
            self.assertEqual(expected["group_name"], entity["group_name"])

        self.assertEqual(5, len(groups))

        expected_groups = [
            {"group_name": "Tokyo", "type": "LOCATION", "entities_count": 1},
            {"group_name": "2025-06-12", "type": "DATE", "entities_count": 2},
            {"group_name": "Maria Rodriguez", "type": "PERSON", "entities_count": 1},
            {"group_name": "Senate", "type": "ORGANIZATION", "entities_count": 1},
            {"group_name": "Resolution No. 122", "type": "LAW", "entities_count": 1},
        ]

        for i, expected_group in enumerate(expected_groups):
            group = groups[i]
            self.assertIn("group_name", group)
            self.assertIn("type", group)
            self.assertIn("entities", group)
            self.assertIn("top_score_entity", group)
            self.assertIsInstance(group["entities"], list)
            self.assertEqual(expected_group["group_name"], group["group_name"])
            self.assertEqual(expected_group["type"], group["type"])
            self.assertEqual(expected_group["entities_count"], len(group["entities"]))

    def test_text_extraction_for_dates(self):
        text = "Today is 13th of January 2024. One month later it will be 13th of February. "
        text += "My birthday this year is January 13th of 2024."
        data = {"text": text}
        result = requests.post(f"{self.service_url}", data=data)

        entities_dict = result.json()["entities"]
        groups_dict = result.json()["groups"]

        self.assertEqual(200, result.status_code)
        self.assertEqual(3, len(entities_dict))

        expected_entities = [
            {"text": "13th of January 2024", "type": "DATE", "group_name": "2024-01-13"},
            {"text": "13th of February", "type": "DATE", "group_name": "13th of February"},
            {"text": "January 13th of 2024", "type": "DATE", "group_name": "2024-01-13"},
        ]

        for i, expected_entity in enumerate(expected_entities):
            entity = entities_dict[i]
            self.assertEqual(expected_entity["text"], entity["text"])
            self.assertEqual(expected_entity["type"], entity["type"])
            self.assertEqual(expected_entity["group_name"], entity["group_name"])

        self.assertEqual(2, len(groups_dict))

        expected_groups = [
            {"group_name": "2024-01-13", "type": "DATE", "entities_count": 2},
            {"group_name": "13th of February", "type": "DATE", "entities_count": 1},
        ]

        for i, expected_group in enumerate(expected_groups):
            group = groups_dict[i]
            self.assertEqual(expected_group["group_name"], group["group_name"])
            self.assertEqual(expected_group["type"], group["type"])
            self.assertEqual(expected_group["entities_count"], len(group["entities"]))
            self.assertIn("top_score_entity", group)

    def test_pdf_extraction(self):
        pdf_path: Path = Path(SRC_PATH, "tests", "end_to_end", "test_pdfs", "test_document.pdf")
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            result = requests.post(self.service_url, files=files)

        self.assertEqual(200, result.status_code)

        entities = result.json()["entities"]
        groups = result.json()["groups"]

        expected_entities = [
            {
                "character_end": 15,
                "character_start": 0,
                "group_name": "Maria Diaz Rodriguez",
                "relevance_percentage": 31,
                "segment": {
                    "bounding_box": {"height": 34, "left": 72, "top": 74, "width": 429},
                    "character_end": 15,
                    "character_start": 0,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 1,
                    "text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                },
                "source_id": "test_document.pdf",
                "text": "Maria Rodriguez",
                "type": "PERSON",
            },
            {
                "character_end": 41,
                "character_start": 24,
                "group_name": "the Louvre Museum",
                "relevance_percentage": 31,
                "segment": {
                    "bounding_box": {"height": 34, "left": 72, "top": 74, "width": 429},
                    "character_end": 41,
                    "character_start": 24,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 1,
                    "text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                },
                "source_id": "test_document.pdf",
                "text": "the Louvre Museum",
                "type": "ORGANIZATION",
            },
            {
                "character_end": 50,
                "character_start": 45,
                "group_name": "Paris",
                "relevance_percentage": 30,
                "segment": {
                    "bounding_box": {"height": 34, "left": 72, "top": 74, "width": 429},
                    "character_end": 50,
                    "character_start": 45,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 1,
                    "text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                },
                "source_id": "test_document.pdf",
                "text": "Paris",
                "type": "LOCATION",
            },
            {
                "character_end": 58,
                "character_start": 52,
                "group_name": "France",
                "relevance_percentage": 30,
                "segment": {
                    "bounding_box": {"height": 34, "left": 72, "top": 74, "width": 429},
                    "character_end": 58,
                    "character_start": 52,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 1,
                    "text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                },
                "source_id": "test_document.pdf",
                "text": "France",
                "type": "LOCATION",
            },
            {
                "character_end": 87,
                "character_start": 74,
                "group_name": "2023-07-12",
                "relevance_percentage": 46,
                "segment": {
                    "bounding_box": {"height": 34, "left": 72, "top": 74, "width": 429},
                    "character_end": 87,
                    "character_start": 74,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 1,
                    "text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                },
                "source_id": "test_document.pdf",
                "text": "July 12, 2023",
                "type": "DATE",
            },
            {
                "character_end": 52,
                "character_start": 32,
                "group_name": "Maria Diaz Rodriguez",
                "relevance_percentage": 18,
                "segment": {
                    "bounding_box": {"height": 14, "left": 73, "top": 153, "width": 350},
                    "character_end": 52,
                    "character_start": 32,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 2,
                    "text": "The full name of this person is Maria Diaz Rodriguez.",
                },
                "source_id": "test_document.pdf",
                "text": "Maria Diaz Rodriguez",
                "type": "PERSON",
            },
            {
                "character_end": 40,
                "character_start": 26,
                "group_name": "Maria Diaz Rodriguez",
                "relevance_percentage": 33,
                "segment": {
                    "bounding_box": {"height": 14, "left": 72, "top": 213, "width": 269},
                    "character_end": 40,
                    "character_start": 26,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 3,
                    "text": "It can also be written as M.D. Rodriguez.",
                },
                "source_id": "test_document.pdf",
                "text": "M.D. Rodriguez",
                "type": "PERSON",
            },
            {
                "character_end": 49,
                "character_start": 41,
                "group_name": "HURIDOCS",
                "relevance_percentage": 16,
                "segment": {
                    "bounding_box": {"height": 15, "left": 72, "top": 292, "width": 352},
                    "character_end": 49,
                    "character_start": 41,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 4,
                    "text": "She is working in an organization called HURIDOCS.",
                },
                "source_id": "test_document.pdf",
                "text": "HURIDOCS",
                "type": "ORGANIZATION",
            },
            {
                "character_end": 10,
                "character_start": 4,
                "group_name": "Senate",
                "relevance_percentage": 30,
                "segment": {
                    "bounding_box": {"height": 34, "left": 72, "top": 351, "width": 440},
                    "character_end": 10,
                    "character_start": 4,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 5,
                    "text": "The Senate passed Resolution No. 122, establishing a set of rules for the impeachment trial.",
                },
                "source_id": "test_document.pdf",
                "text": "Senate",
                "type": "ORGANIZATION",
            },
            {
                "character_end": 36,
                "character_start": 18,
                "group_name": "Resolution No. 122",
                "relevance_percentage": 46,
                "segment": {
                    "bounding_box": {"height": 34, "left": 72, "top": 351, "width": 440},
                    "character_end": 36,
                    "character_start": 18,
                    "page_number": 1,
                    "pdf_name": "test_document.pdf",
                    "segment_number": 5,
                    "text": "The Senate passed Resolution No. 122, establishing a set of rules for the impeachment trial.",
                },
                "source_id": "test_document.pdf",
                "text": "Resolution No. 122",
                "type": "LAW",
            },
        ]

        expected_groups = [
            {
                "entities": [
                    {"index": 6, "text": "M.D. Rodriguez"},
                    {"index": 0, "text": "Maria Rodriguez"},
                    {"index": 5, "text": "Maria Diaz Rodriguez"},
                ],
                "group_name": "Maria Diaz Rodriguez",
                "top_score_entity": {
                    "character_end": 40,
                    "character_start": 26,
                    "group_name": "Maria Diaz Rodriguez",
                    "relevance_percentage": 33,
                    "segment": {
                        "bounding_box": {"height": 14, "left": 72, "top": 213, "width": 269},
                        "character_end": 40,
                        "character_start": 26,
                        "page_number": 1,
                        "pdf_name": "test_document.pdf",
                        "segment_number": 3,
                        "text": "It can also be written as M.D. Rodriguez.",
                    },
                    "source_id": "test_document.pdf",
                    "text": "M.D. Rodriguez",
                    "type": "PERSON",
                },
                "type": "PERSON",
            },
            {
                "entities": [{"index": 1, "text": "the Louvre Museum"}],
                "group_name": "the Louvre Museum",
                "top_score_entity": {
                    "character_end": 41,
                    "character_start": 24,
                    "group_name": "the Louvre Museum",
                    "relevance_percentage": 31,
                    "segment": {
                        "bounding_box": {"height": 34, "left": 72, "top": 74, "width": 429},
                        "character_end": 41,
                        "character_start": 24,
                        "page_number": 1,
                        "pdf_name": "test_document.pdf",
                        "segment_number": 1,
                        "text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                    },
                    "source_id": "test_document.pdf",
                    "text": "the Louvre Museum",
                    "type": "ORGANIZATION",
                },
                "type": "ORGANIZATION",
            },
            {
                "entities": [{"index": 2, "text": "Paris"}],
                "group_name": "Paris",
                "top_score_entity": {
                    "character_end": 50,
                    "character_start": 45,
                    "group_name": "Paris",
                    "relevance_percentage": 30,
                    "segment": {
                        "bounding_box": {"height": 34, "left": 72, "top": 74, "width": 429},
                        "character_end": 50,
                        "character_start": 45,
                        "page_number": 1,
                        "pdf_name": "test_document.pdf",
                        "segment_number": 1,
                        "text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                    },
                    "source_id": "test_document.pdf",
                    "text": "Paris",
                    "type": "LOCATION",
                },
                "type": "LOCATION",
            },
            {
                "entities": [{"index": 3, "text": "France"}],
                "group_name": "France",
                "top_score_entity": {
                    "character_end": 58,
                    "character_start": 52,
                    "group_name": "France",
                    "relevance_percentage": 30,
                    "segment": {
                        "bounding_box": {"height": 34, "left": 72, "top": 74, "width": 429},
                        "character_end": 58,
                        "character_start": 52,
                        "page_number": 1,
                        "pdf_name": "test_document.pdf",
                        "segment_number": 1,
                        "text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                    },
                    "source_id": "test_document.pdf",
                    "text": "France",
                    "type": "LOCATION",
                },
                "type": "LOCATION",
            },
            {
                "entities": [{"index": 4, "text": "July 12, 2023"}],
                "group_name": "2023-07-12",
                "top_score_entity": {
                    "character_end": 87,
                    "character_start": 74,
                    "group_name": "2023-07-12",
                    "relevance_percentage": 46,
                    "segment": {
                        "bounding_box": {"height": 34, "left": 72, "top": 74, "width": 429},
                        "character_end": 87,
                        "character_start": 74,
                        "page_number": 1,
                        "pdf_name": "test_document.pdf",
                        "segment_number": 1,
                        "text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                    },
                    "source_id": "test_document.pdf",
                    "text": "July 12, 2023",
                    "type": "DATE",
                },
                "type": "DATE",
            },
            {
                "entities": [{"index": 7, "text": "HURIDOCS"}],
                "group_name": "HURIDOCS",
                "top_score_entity": {
                    "character_end": 49,
                    "character_start": 41,
                    "group_name": "HURIDOCS",
                    "relevance_percentage": 16,
                    "segment": {
                        "bounding_box": {"height": 15, "left": 72, "top": 292, "width": 352},
                        "character_end": 49,
                        "character_start": 41,
                        "page_number": 1,
                        "pdf_name": "test_document.pdf",
                        "segment_number": 4,
                        "text": "She is working in an organization called HURIDOCS.",
                    },
                    "source_id": "test_document.pdf",
                    "text": "HURIDOCS",
                    "type": "ORGANIZATION",
                },
                "type": "ORGANIZATION",
            },
            {
                "entities": [{"index": 8, "text": "Senate"}],
                "group_name": "Senate",
                "top_score_entity": {
                    "character_end": 10,
                    "character_start": 4,
                    "group_name": "Senate",
                    "relevance_percentage": 30,
                    "segment": {
                        "bounding_box": {"height": 34, "left": 72, "top": 351, "width": 440},
                        "character_end": 10,
                        "character_start": 4,
                        "page_number": 1,
                        "pdf_name": "test_document.pdf",
                        "segment_number": 5,
                        "text": "The Senate passed Resolution No. 122, establishing a set of rules for the impeachment trial.",
                    },
                    "source_id": "test_document.pdf",
                    "text": "Senate",
                    "type": "ORGANIZATION",
                },
                "type": "ORGANIZATION",
            },
            {
                "entities": [{"index": 9, "text": "Resolution No. 122"}],
                "group_name": "Resolution No. 122",
                "top_score_entity": {
                    "character_end": 36,
                    "character_start": 18,
                    "group_name": "Resolution No. 122",
                    "relevance_percentage": 46,
                    "segment": {
                        "bounding_box": {"height": 34, "left": 72, "top": 351, "width": 440},
                        "character_end": 36,
                        "character_start": 18,
                        "page_number": 1,
                        "pdf_name": "test_document.pdf",
                        "segment_number": 5,
                        "text": "The Senate passed Resolution No. 122, establishing a set of rules for the impeachment trial.",
                    },
                    "source_id": "test_document.pdf",
                    "text": "Resolution No. 122",
                    "type": "LAW",
                },
                "type": "LAW",
            },
        ]

        self.assertIsInstance(entities, list)
        self.assertEqual(len(entities), len(expected_entities))
        self.assertIsInstance(groups, list)
        self.assertEqual(len(groups), len(expected_groups))

        # Assert all expected entity fields and values
        for i, expected in enumerate(expected_entities):
            entity = entities[i]
            self.assertEqual(expected["text"], entity["text"])
            self.assertEqual(expected["type"], entity["type"])
            self.assertEqual(expected["group_name"], entity["group_name"])
            self.assertIn("segment", entity)
            segment = entity["segment"]
            self.assertEqual(expected["segment"]["text"], segment["text"])
            self.assertEqual(expected["segment"]["page_number"], segment["page_number"])
            self.assertEqual(expected["segment"]["segment_number"], segment["segment_number"])
            self.assertEqual(expected["segment"]["character_start"], segment["character_start"])
            self.assertEqual(expected["segment"]["character_end"], segment["character_end"])
            self.assertIn("bounding_box", segment)
            for box_field in ["left", "top", "width", "height"]:
                self.assertEqual(expected["segment"]["bounding_box"][box_field], segment["bounding_box"][box_field])

        # Assert all expected group fields and values
        for i, expected in enumerate(expected_groups):
            group = groups[i]
            self.assertEqual(expected["group_name"], group["group_name"])
            self.assertEqual(expected["type"], group["type"])
            self.assertIn("entities", group)
            self.assertEqual(len(group["entities"]), len(expected["entities"]))
            for j, expected_entity in enumerate(expected["entities"]):
                entity_text = group["entities"][j]
                self.assertEqual(expected_entity["index"], entity_text["index"])
                self.assertEqual(expected_entity["text"], entity_text["text"])
            self.assertIn("top_score_entity", group)
            self.assertEqual(expected["top_score_entity"]["index"], group["top_score_entity"]["index"])
            self.assertEqual(expected["top_score_entity"]["text"], group["top_score_entity"]["text"])
            if "entities_ids" in expected:
                self.assertIn("entities_ids", group)
                self.assertEqual(expected["entities_ids"], group["entities_ids"])
            if "entities_text" in expected:
                self.assertIn("entities_text", group)
                self.assertEqual(expected["entities_text"], group["entities_text"])

    def test_pdf_references(self):
        for document in ["document_1.pdf", "document_2.pdf", "document_3.pdf"]:
            pdf_path: Path = ROOT_PATH / "src" / "tests" / "end_to_end" / "test_pdfs" / document
            with open(pdf_path, "rb") as pdf_file:
                files = {"file": pdf_file}

                result = requests.post(self.service_url, files=files)

        self.assertEqual(200, result.status_code)

        entities_dict = [x for x in result.json()["entities"] if "REFERENCE" in x["type"]]
        groups_dict = [x for x in result.json()["groups"] if "REFERENCE" in x["type"]]

        expected_entities = [
            {
                "group_name": "4. Results Interpretation",
                "page_number": 1,
                "segment": {
                    "bounding_box": {"height": 11, "left": 72, "top": 234, "width": 436},
                    "character_end": 63,
                    "character_start": 39,
                    "page_number": 1,
                    "pdf_name": "document_3.pdf",
                    "segment_number": 4,
                    "text": 'These granular results expand upon the "Results Interpretation" presented in Document 1.',
                },
                "text": '"Results Interpretation"',
                "type": "REFERENCE_POINTER",
            },
            {
                "group_name": "3. Phase 2: Analysis",
                "page_number": 1,
                "segment": {
                    "bounding_box": {"height": 26, "left": 72, "top": 357, "width": 444},
                    "character_end": 68,
                    "character_start": 59,
                    "page_number": 1,
                    "pdf_name": "document_3.pdf",
                    "segment_number": 7,
                    "text": 'The capabilities of these algorithms build directly on the "Analysis Techniques" discussed in Document 2.',
                },
                "text": '"Analysis',
                "type": "REFERENCE_POINTER",
            },
            {
                "group_name": "3. Analysis Techniques",
                "page_number": 1,
                "segment": {
                    "bounding_box": {"height": 26, "left": 72, "top": 357, "width": 444},
                    "character_end": 80,
                    "character_start": 59,
                    "page_number": 1,
                    "pdf_name": "document_3.pdf",
                    "segment_number": 7,
                    "text": 'The capabilities of these algorithms build directly on the "Analysis Techniques" discussed in Document 2.',
                },
                "text": '"Analysis Techniques"',
                "type": "REFERENCE_POINTER",
            },
            {
                "group_name": "Document 1: Project Overview",
                "page_number": 1,
                "segment": {
                    "bounding_box": {"height": 41, "left": 72, "top": 494, "width": 439},
                    "character_end": 72,
                    "character_start": 54,
                    "page_number": 1,
                    "pdf_name": "document_3.pdf",
                    "segment_number": 10,
                    "text": 'The overall context for this work can be found in the "Project Overview" (Document 1). The findings presented in "Detailed Findings" within this document will guide our subsequent research directions.',
                },
                "text": '"Project Overview"',
                "type": "REFERENCE_POINTER",
            },
            {
                "group_name": "Document 1: Project Overview",
                "page_number": 1,
                "segment": {
                    "bounding_box": {"height": 41, "left": 72, "top": 494, "width": 439},
                    "character_end": 84,
                    "character_start": 74,
                    "page_number": 1,
                    "pdf_name": "document_3.pdf",
                    "segment_number": 10,
                    "text": 'The overall context for this work can be found in the "Project Overview" (Document 1). The findings presented in "Detailed Findings" within this document will guide our subsequent research directions.',
                },
                "text": "Document 1",
                "type": "REFERENCE_POINTER",
            },
            {
                "group_name": "1. Detailed Findings",
                "page_number": 1,
                "segment": {
                    "bounding_box": {"height": 41, "left": 72, "top": 494, "width": 439},
                    "character_end": 132,
                    "character_start": 113,
                    "page_number": 1,
                    "pdf_name": "document_3.pdf",
                    "segment_number": 10,
                    "text": 'The overall context for this work can be found in the "Project Overview" (Document 1). The findings presented in "Detailed Findings" within this document will guide our subsequent research directions.',
                },
                "text": '"Detailed Findings"',
                "type": "REFERENCE_POINTER",
            },
        ]

        for i, expected in enumerate(expected_entities):
            entity = entities_dict[i]
            self.assertEqual(expected["group_name"], entity["group_name"])
            self.assertEqual(expected["page_number"], entity["page_number"])
            self.assertEqual(expected["text"], entity["text"])
            self.assertEqual(expected["type"], entity["type"])
            # Segment checks
            self.assertEqual(expected["segment"]["text"], entity["segment"]["text"])
            self.assertEqual(expected["segment"]["page_number"], entity["segment"]["page_number"])
            self.assertEqual(expected["segment"]["segment_number"], entity["segment"]["segment_number"])
            self.assertEqual(expected["segment"]["character_start"], entity["segment"]["character_start"])
            self.assertEqual(expected["segment"]["character_end"], entity["segment"]["character_end"])
            self.assertEqual(expected["segment"]["pdf_name"], entity["segment"]["pdf_name"])
            # Bounding box checks
            for key in ["left", "top", "width", "height"]:
                self.assertEqual(expected["segment"]["bounding_box"][key], entity["segment"]["bounding_box"][key])

        expected_groups = [
            {
                "entities_ids": [5, 6],
                "entities_text": ['"Project Overview"', "Document 1"],
                "group_name": "Document 1: Project Overview",
                "segment": {
                    "bounding_box": {"height": 25, "left": 72, "top": 97, "width": 333},
                    "character_end": 28,
                    "character_start": 0,
                    "page_number": 1,
                    "pdf_name": "document_1.pdf",
                    "segment_number": 1,
                    "text": "Document 1: Project Overview",
                },
                "type": "REFERENCE_DESTINATION",
            },
            {
                "entities_ids": [2],
                "entities_text": ['"Analysis'],
                "group_name": "3. Phase 2: Analysis",
                "segment": {
                    "bounding_box": {"height": 17, "left": 72, "top": 406, "width": 162},
                    "character_end": 20,
                    "character_start": 0,
                    "page_number": 1,
                    "pdf_name": "document_1.pdf",
                    "segment_number": 8,
                    "text": "3. Phase 2: Analysis",
                },
                "type": "REFERENCE_DESTINATION",
            },
            {
                "entities_ids": [1],
                "entities_text": ['"Results Interpretation"'],
                "group_name": "4. Results Interpretation",
                "segment": {
                    "bounding_box": {"height": 17, "left": 71, "top": 557, "width": 195},
                    "character_end": 25,
                    "character_start": 0,
                    "page_number": 1,
                    "pdf_name": "document_1.pdf",
                    "segment_number": 11,
                    "text": "4. Results Interpretation",
                },
                "type": "REFERENCE_DESTINATION",
            },
            {
                "entities_ids": [3],
                "entities_text": ['"Analysis Techniques"'],
                "group_name": "3. Analysis Techniques",
                "segment": {
                    "bounding_box": {"height": 17, "left": 71, "top": 406, "width": 186},
                    "character_end": 22,
                    "character_start": 0,
                    "page_number": 1,
                    "pdf_name": "document_2.pdf",
                    "segment_number": 8,
                    "text": "3. Analysis Techniques",
                },
                "type": "REFERENCE_DESTINATION",
            },
            {
                "entities_ids": [7],
                "entities_text": ['"Detailed Findings"'],
                "group_name": "1. Detailed Findings",
                "segment": {
                    "bounding_box": {"height": 18, "left": 71, "top": 145, "width": 160},
                    "character_end": 20,
                    "character_start": 0,
                    "page_number": 1,
                    "pdf_name": "document_3.pdf",
                    "segment_number": 2,
                    "text": "1. Detailed Findings",
                },
                "type": "REFERENCE_DESTINATION",
            },
        ]

        self.assertEqual(len(expected_groups), len(groups_dict))
        for i, expected in enumerate(expected_groups):
            group = groups_dict[i]
            self.assertEqual(expected["group_name"], group["group_name"])
            self.assertEqual(expected["type"], group["type"])
            self.assertEqual(expected["entities_ids"], group["entities_ids"])
            self.assertEqual(expected["entities_text"], group["entities_text"])
            # Segment checks
            self.assertEqual(expected["segment"]["text"], group["segment"]["text"])
            self.assertEqual(expected["segment"]["page_number"], group["segment"]["page_number"])
            self.assertEqual(expected["segment"]["segment_number"], group["segment"]["segment_number"])
            self.assertEqual(expected["segment"]["character_start"], group["segment"]["character_start"])
            self.assertEqual(expected["segment"]["character_end"], group["segment"]["character_end"])
            self.assertEqual(expected["segment"]["pdf_name"], group["segment"]["pdf_name"])
            # Bounding box checks
            for key in ["left", "top", "width", "height"]:
                self.assertEqual(expected["segment"]["bounding_box"][key], group["segment"]["bounding_box"][key])
