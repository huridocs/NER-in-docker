import json
from pathlib import Path
from unittest import TestCase
import requests

from ner_in_docker.configuration import ROOT_PATH, SRC_PATH


class TestEndToEnd(TestCase):
    service_url = "http://localhost:5070"

    @staticmethod
    def similar_value(value: int):
        return [value - 1, value, value + 1]

    def test_empty_query(self):
        result = requests.post(self.service_url)

        self.assertEqual(200, result.status_code)
        self.assertEqual([], result.json()["entities"])
        self.assertEqual([], result.json()["groups"])

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
        self.assertEqual("Unprocessable text or PDF file", result.json()["detail"])

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
            self.assertIn("top_relevance_entity", group)
            self.assertIsInstance(group["entities"], list)
            self.assertEqual(expected_group["group_name"], group["group_name"])
            self.assertEqual(expected_group["type"], group["type"])
            self.assertEqual(expected_group["entities_count"], len(group["entities"]))

    def test_text_extraction_for_dates(self):
        text = "Today is 13th of January 2024. One month later it will be 13th of February. "
        text += "My birthday this year is January 13th of 2024."
        data = {"text": text}
        result = requests.post(f"{self.service_url}", data=data)

        entities = result.json()["entities"]
        groups = result.json()["groups"]

        self.assertEqual(200, result.status_code)
        self.assertEqual(3, len(entities))

        expected_entities = [
            {"text": "13th of January 2024", "type": "DATE", "group_name": "2024-01-13"},
            {"text": "13th of February", "type": "DATE", "group_name": "13th of February"},
            {"text": "January 13th of 2024", "type": "DATE", "group_name": "2024-01-13"},
        ]

        for i, expected_entity in enumerate(expected_entities):
            entity = entities[i]
            self.assertEqual(expected_entity["text"], entity["text"])
            self.assertEqual(expected_entity["type"], entity["type"])
            self.assertEqual(expected_entity["group_name"], entity["group_name"])

        self.assertEqual(2, len(groups))

        expected_groups = [
            {"group_name": "2024-01-13", "type": "DATE", "entities_count": 2},
            {"group_name": "13th of February", "type": "DATE", "entities_count": 1},
        ]

        for i, expected_group in enumerate(expected_groups):
            group = groups[i]
            self.assertEqual(expected_group["group_name"], group["group_name"])
            self.assertEqual(expected_group["type"], group["type"])
            self.assertEqual(expected_group["entities_count"], len(group["entities"]))
            self.assertIn("top_relevance_entity", group)

    def test_pdf_extraction(self):
        pdf_path: Path = Path(SRC_PATH, "tests", "end_to_end", "test_pdfs", "test_document.pdf")
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            result = requests.post(self.service_url, files=files)

        self.assertEqual(200, result.status_code)

        entities = result.json()["entities"]
        groups = result.json()["groups"]

        expected_entities = json.loads((SRC_PATH / "tests" / "end_to_end" / "expected_entities.json").read_text())
        expected_groups = json.loads((SRC_PATH / "tests" / "end_to_end" / "expected_groups.json").read_text())

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
            self.assertIn("top_relevance_entity", group)
            if "entities_ids" in expected:
                self.assertIn("entities_ids", group)
                self.assertEqual(expected["entities_ids"], group["entities_ids"])
            if "entities_text" in expected:
                self.assertIn("entities_text", group)
                self.assertEqual(expected["entities_text"], group["entities_text"])

    def test_pdf_references(self):
        data = {"namespace": "end_to_end_test_references"}
        requests.post(self.service_url + "/delete_namespace", data=data)
        for document in ["document_1.pdf", "document_2.pdf", "document_3.pdf"]:
            pdf_path: Path = ROOT_PATH / "src" / "tests" / "end_to_end" / "test_pdfs" / document
            with open(pdf_path, "rb") as pdf_file:
                files = {"file": pdf_file}
                data = {"namespace": "end_to_end_test_references"}
                result = requests.post(self.service_url, files=files, data=data)

        self.assertEqual(200, result.status_code)

        entities = [x for x in result.json()["entities"] if x["type"] == "REFERENCE"]
        groups = [x for x in result.json()["groups"] if x["type"] == "REFERENCE"]

        expected_entities = json.loads((SRC_PATH / "tests" / "end_to_end" / "expected_references_entities.json").read_text())
        expected_groups = json.loads((SRC_PATH / "tests" / "end_to_end" / "expected_references_groups.json").read_text())
        self.assertEqual(100, groups[0]["top_relevance_entity"]["relevance_percentage"])

        for i, expected in enumerate(expected_entities):
            entity = entities[i]
            self.assertEqual(expected["character_end"], entity["character_end"])
            self.assertEqual(expected["character_start"], entity["character_start"])
            self.assertEqual(expected["group_name"], entity["group_name"])
            self.assertEqual(expected["relevance_percentage"], entity["relevance_percentage"])
            self.assertEqual(expected["source_id"], entity["source_id"])
            self.assertEqual(expected["text"], entity["text"])
            self.assertEqual(expected["type"], entity["type"])

            segment = entity["segment"]
            expected_segment = expected["segment"]
            self.assertEqual(expected_segment["bounding_box"]["height"], segment["bounding_box"]["height"])
            self.assertEqual(expected_segment["bounding_box"]["left"], segment["bounding_box"]["left"])
            self.assertEqual(expected_segment["bounding_box"]["top"], segment["bounding_box"]["top"])
            self.assertEqual(expected_segment["bounding_box"]["width"], segment["bounding_box"]["width"])
            self.assertEqual(expected_segment["character_end"], segment["character_end"])
            self.assertEqual(expected_segment["character_start"], segment["character_start"])
            self.assertEqual(expected_segment["page_number"], segment["page_number"])
            self.assertEqual(expected_segment["pdf_name"], segment["pdf_name"])
            self.assertEqual(expected_segment["segment_number"], segment["segment_number"])
            self.assertEqual(expected_segment["text"], segment["text"])

        for i, expected in enumerate(expected_groups):
            group = groups[i]
            self.assertEqual(expected["group_name"], group["group_name"])
            self.assertEqual(expected["type"], group["type"])
            self.assertEqual(expected["entities"], group["entities"])
            self.assertEqual(
                expected["top_relevance_entity"]["character_end"], group["top_relevance_entity"]["character_end"]
            )
            self.assertEqual(
                expected["top_relevance_entity"]["character_start"], group["top_relevance_entity"]["character_start"]
            )
            self.assertEqual(expected["top_relevance_entity"]["group_name"], group["top_relevance_entity"]["group_name"])
            self.assertEqual(
                expected["top_relevance_entity"]["relevance_percentage"],
                group["top_relevance_entity"]["relevance_percentage"],
            )
            self.assertEqual(expected["top_relevance_entity"]["source_id"], group["top_relevance_entity"]["source_id"])
            self.assertEqual(expected["top_relevance_entity"]["text"], group["top_relevance_entity"]["text"])
            self.assertEqual(expected["top_relevance_entity"]["type"], group["top_relevance_entity"]["type"])

            segment = group["top_relevance_entity"]["segment"]
            expected_segment = expected["top_relevance_entity"]["segment"]
            self.assertEqual(expected_segment["bounding_box"]["height"], segment["bounding_box"]["height"])
            self.assertEqual(expected_segment["bounding_box"]["left"], segment["bounding_box"]["left"])
            self.assertEqual(expected_segment["bounding_box"]["top"], segment["bounding_box"]["top"])
            self.assertEqual(expected_segment["bounding_box"]["width"], segment["bounding_box"]["width"])
            self.assertEqual(expected_segment["character_end"], segment["character_end"])
            self.assertEqual(expected_segment["character_start"], segment["character_start"])
            self.assertEqual(expected_segment["page_number"], segment["page_number"])
            self.assertEqual(expected_segment["pdf_name"], segment["pdf_name"])
            self.assertEqual(expected_segment["segment_number"], segment["segment_number"])
            self.assertEqual(expected_segment["text"], segment["text"])

    def test_is_processed_endpoint(self):
        namespace = "test_is_processed_namespace"
        identifier_1 = "test_identifier_123"
        identifier_2 = "test_identifier_456"

        requests.post(self.service_url + "/delete_namespace", data={"namespace": namespace})

        result = requests.post(self.service_url + "/is_processed", data={"namespace": namespace, "identifier": identifier_1})
        self.assertEqual(200, result.status_code)
        self.assertFalse(result.json())

        text = "Test document with Tokyo and Maria Rodriguez"
        data = {"text": text, "namespace": namespace, "identifier": identifier_1}
        result = requests.post(self.service_url, data=data)
        self.assertEqual(200, result.status_code)

        result = requests.post(self.service_url + "/is_processed", data={"namespace": namespace, "identifier": identifier_1})
        self.assertEqual(200, result.status_code)
        self.assertTrue(result.json())

        result = requests.post(self.service_url + "/is_processed", data={"namespace": namespace, "identifier": identifier_2})
        self.assertEqual(200, result.status_code)
        self.assertFalse(result.json())

        result = requests.post(self.service_url + "/is_processed", data={"namespace": namespace})
        self.assertEqual(200, result.status_code)
        self.assertFalse(result.json())

        result = requests.post(self.service_url + "/is_processed", data={"identifier": identifier_1})
        self.assertEqual(200, result.status_code)
        self.assertFalse(result.json())

        requests.post(self.service_url + "/delete_namespace", data={"namespace": namespace})
