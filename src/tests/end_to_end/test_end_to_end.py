from pathlib import Path
from unittest import TestCase
import requests
from configuration import ROOT_PATH
from domain.NamedEntity import NamedEntity


class TestEndToEnd(TestCase):
    service_url = "http://localhost:5070"

    def test_text_extraction(self):
        data = {"text": "The International Space Station past above Tokyo on 12 June 2025."}
        result = requests.post(f"{self.service_url}", data=data)

        self.assertEqual(200, result.status_code)

        entity_1 = NamedEntity(**result.json()[0])
        entity_2 = NamedEntity(**result.json()[1])

        self.assertEqual("Tokyo", entity_1.text)
        self.assertEqual("LOCATION", entity_1.type)
        self.assertEqual("Tokyo", entity_1.normalized_text)
        self.assertEqual(43, entity_1.character_start)
        self.assertEqual(48, entity_1.character_end)

        self.assertEqual("12 June 2025", entity_2.text)
        self.assertEqual("DATE", entity_2.type)
        self.assertEqual("2025-06-12", entity_2.normalized_text)
        self.assertEqual(52, entity_2.character_start)
        self.assertEqual(64, entity_2.character_end)

    def test_pdf_extraction(self):
        pdf_path: Path = Path(ROOT_PATH, "src", "tests", "end_to_end", "test_pdfs", "test_document.pdf")
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            response = requests.post(f"{self.service_url}/pdf", files=files)
            response_json = response.json()
            self.assertEqual(200, response.status_code)
            self.assertEqual(10, len(response_json))
            self.assertEqual("PERSON", response_json[0]["type"])
            self.assertEqual("Maria Rodriguez", response_json[0]["text"])
            self.assertEqual("Maria Rodriguez", response_json[0]["normalized_text"])
            self.assertEqual(0, response_json[0]["character_start"])
            self.assertEqual(15, response_json[0]["character_end"])
            expected_segment_text: str = (
                "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023."
            )
            self.assertEqual(expected_segment_text, response_json[0]["segment_text"])
            self.assertEqual(1, response_json[0]["page_number"])
            self.assertEqual(1, response_json[0]["segment_number"])
            self.assertEqual(72, response_json[0]["bounding_box"]["left"])
            self.assertEqual(74, response_json[0]["bounding_box"]["top"])
            self.assertEqual(429, response_json[0]["bounding_box"]["width"])
            self.assertEqual(34, response_json[0]["bounding_box"]["height"])
