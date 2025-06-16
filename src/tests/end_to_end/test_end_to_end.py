from pathlib import Path
from unittest import TestCase
import requests

from configuration import ROOT_PATH
from domain.NamedEntityType import NamedEntityType
from drivers.rest.response_entities.GroupResponse import GroupResponse
from drivers.rest.response_entities.NamedEntityResponse import NamedEntityResponse
from drivers.rest.response_entities.PDFNamedEntityResponse import PDFNamedEntityResponse


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
        pdf_path: Path = Path(ROOT_PATH, "src", "tests", "end_to_end", "test_pdfs", "not_a_pdf.pdf")

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

        entities_dict = result.json()["entities"]
        groups_dict = result.json()["groups"]

        self.assertEqual(200, result.status_code)
        self.assertEqual(6, len(entities_dict))

        expected_entities = [
            ("Tokyo", "LOCATION", "Tokyo", 43, 48),
            ("12 June 2025", "DATE", "2025-06-12", 52, 64),
            ("Maria Rodriguez", "PERSON", "Maria Rodriguez", 66, 81),
            ("Senate", "ORGANIZATION", "Senate", 93, 99),
            ("Resolution No. 122", "LAW", "Resolution No. 122", 105, 123),
            ("twelve of June 2025", "DATE", "2025-06-12", None, None),
        ]

        for i, (text, type_, group_name, start, end) in enumerate(expected_entities):
            entity = NamedEntityResponse(**entities_dict[i])
            self.assertEqual(text, entity.text)
            self.assertEqual(type_, entity.type)
            self.assertEqual(group_name, entity.group_name)
            if start is not None and end is not None:
                self.assertEqual(start, entity.character_start)
                self.assertEqual(end, entity.character_end)

        self.assertEqual(5, len(groups_dict))

        expected_groups = [
            ("Tokyo", "LOCATION", [0], ["Tokyo"]),
            ("2025-06-12", "DATE", [1, 5], ["12 June 2025", "twelve of June 2025"]),
            ("Maria Rodriguez", "PERSON", [2], ["Maria Rodriguez"]),
            ("Senate", "ORGANIZATION", [3], ["Senate"]),
            ("Resolution No. 122", "LAW", [4], ["Resolution No. 122"]),
        ]

        for i, (group_name, type_, ids, texts) in enumerate(expected_groups):
            group = GroupResponse(**groups_dict[i])
            self.assertEqual(group_name, group.group_name)
            self.assertEqual(type_, group.type)
            self.assertEqual(ids, group.entities_ids)
            self.assertEqual(texts, group.entities_text)

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
            NamedEntityResponse(
                text="13th of January 2024",
                type=NamedEntityType.DATE,
                group_name="2024-01-13",
                character_start=9,
                character_end=29,
            ),
            NamedEntityResponse(
                text="13th of February",
                type=NamedEntityType.DATE,
                group_name="13th of February",
                character_start=58,
                character_end=74,
            ),
            NamedEntityResponse(
                text="January 13th of 2024",
                type=NamedEntityType.DATE,
                group_name="2024-01-13",
                character_start=101,
                character_end=121,
            ),
        ]

        for i, expected_entity in enumerate(expected_entities):
            self.assertEqual(expected_entity, NamedEntityResponse(**entities_dict[i]))

        self.assertEqual(2, len(groups_dict))

        expected_groups = [
            GroupResponse(
                group_name="2024-01-13",
                type=NamedEntityType.DATE,
                entities_ids=[0, 2],
                entities_text=["13th of January 2024", "January 13th of 2024"],
            ),
            GroupResponse(
                group_name="13th of February",
                type=NamedEntityType.DATE,
                entities_ids=[1],
                entities_text=["13th of February"],
            ),
        ]

        for i, expected_group in enumerate(expected_groups):
            self.assertEqual(expected_group, GroupResponse(**groups_dict[i]))

    def test_pdf_extraction(self):
        pdf_path: Path = Path(ROOT_PATH, "src", "tests", "end_to_end", "test_pdfs", "test_document.pdf")
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            result = requests.post(self.service_url, files=files)

        self.assertEqual(200, result.status_code)

        entities_dict = result.json()["entities"]
        groups_dict = result.json()["groups"]
        self.assertEqual(10, len(entities_dict))

        expected_entities = [
            {
                "group_name": "Maria Diaz Rodriguez",
                "type": "PERSON",
                "text": "Maria Rodriguez",
                "segment_text": "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023.",
                "page_number": 1,
                "segment_number": 1,
                "character_start": 0,
                "character_end": 15,
                "bounding_box": (72, 74, 430, 34),
            },
            {
                "group_name": "Resolution No. 122",
                "type": "LAW",
                "text": "Resolution No. 122",
                "segment_text": "The Senate passed Resolution No. 122, establishing a set of rules for the impeachment trial.",
                "page_number": 1,
                "segment_number": 5,
                "character_start": 18,
                "character_end": 36,
                "bounding_box": (72, 351, 440, 35),
            },
        ]

        for i, expected in enumerate(expected_entities):
            entity = PDFNamedEntityResponse(**entities_dict[i * 9])
            self.assertEqual(expected["group_name"], entity.group_name)
            self.assertEqual(expected["type"], entity.type)
            self.assertEqual(expected["text"], entity.text)
            self.assertEqual(expected["segment_text"], entity.segment.text)
            self.assertEqual(expected["page_number"], entity.segment.page_number)
            self.assertEqual(expected["segment_number"], entity.segment.segment_number)
            self.assertEqual(expected["character_start"], entity.segment.character_start)
            self.assertEqual(expected["character_end"], entity.segment.character_end)
            self.assertIn(expected["bounding_box"][0], self.similar_value(entity.segment.bounding_box.left))
            self.assertIn(expected["bounding_box"][1], self.similar_value(entity.segment.bounding_box.top))
            self.assertIn(expected["bounding_box"][2], self.similar_value(entity.segment.bounding_box.width))
            self.assertIn(expected["bounding_box"][3], self.similar_value(entity.segment.bounding_box.height))

        self.assertEqual(8, len(groups_dict))

        expected_groups = [
            {
                "group_name": "Maria Diaz Rodriguez",
                "type": "PERSON",
                "entities_ids": [0, 5, 6],
                "entities_text": ["Maria Rodriguez", "Maria Diaz Rodriguez", "M.D. Rodriguez"],
            },
            {
                "group_name": "Resolution No. 122",
                "type": "LAW",
                "entities_ids": [9],
                "entities_text": ["Resolution No. 122"],
            },
        ]

        for i, expected in enumerate(expected_groups):
            group = GroupResponse(**groups_dict[i * 7])
            self.assertEqual(expected["group_name"], group.group_name)
            self.assertEqual(expected["type"], group.type)
            self.assertEqual(expected["entities_ids"], group.entities_ids)
            self.assertEqual(expected["entities_text"], group.entities_text)

    def test_pdf_references(self):
        for document in ["document_1.pdf", "document_2.pdf", "document_3.pdf"]:
            pdf_path: Path = ROOT_PATH / "src" / "tests" / "end_to_end" / "test_pdfs" / document
            with open(pdf_path, "rb") as pdf_file:
                files = {"file": pdf_file}
                result = requests.post(self.service_url, files=files)

        self.assertEqual(200, result.status_code)

        entities_dict = result.json()["entities"]
        groups_dict = result.json()["groups"]

        self.assertEqual(10, len(entities_dict))

        expected_entities = [
            {
                "group_name": "4. Results Interpretation",
                "type": "REFERENCE",
                "text": "Results Interpretation",
                "segment_text": 'These granular results expand upon the "Results Interpretation" presented in Document 1.',
                "page_number": 1,
                "segment_number": 4,
                "character_start": 0,
                "character_end": 0,
                "bounding_box": (0, 0, 0, 0),
            },
        ]

        for i, expected in enumerate(expected_entities):
            entity = PDFNamedEntityResponse(**entities_dict[i * 9])
            self.assertEqual(expected["group_name"], entity.group_name)
            self.assertEqual(expected["type"], entity.type)
            self.assertEqual(expected["text"], entity.text)
            self.assertEqual(expected["segment_text"], entity.segment.text)
            self.assertEqual(expected["page_number"], entity.segment.page_number)
            self.assertEqual(expected["segment_number"], entity.segment.segment_number)
            self.assertEqual(expected["character_start"], entity.segment.character_start)
            self.assertEqual(expected["character_end"], entity.segment.character_end)
            self.assertIn(expected["bounding_box"][0], self.similar_value(entity.segment.bounding_box.left))
            self.assertIn(expected["bounding_box"][1], self.similar_value(entity.segment.bounding_box.top))
            self.assertIn(expected["bounding_box"][2], self.similar_value(entity.segment.bounding_box.width))
            self.assertIn(expected["bounding_box"][3], self.similar_value(entity.segment.bounding_box.height))

        self.assertEqual(8, len(groups_dict))

        expected_groups = [
            {
                "group_name": "4. Results Interpretation",
                "type": "REFERENCE",
                "entities_ids": [0],
                "entities_text": ["Results Interpretation"],
            },
        ]

        for i, expected in enumerate(expected_groups):
            group = GroupResponse(**groups_dict[i * 7])
            self.assertEqual(expected["group_name"], group.group_name)
            self.assertEqual(expected["type"], group.type)
            self.assertEqual(expected["entities_ids"], group.entities_ids)
            self.assertEqual(expected["entities_text"], group.entities_text)
