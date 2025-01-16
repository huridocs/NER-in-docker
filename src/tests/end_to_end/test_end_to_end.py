from pathlib import Path
from unittest import TestCase
import requests
from configuration import ROOT_PATH
from domain.NamedEntity import NamedEntity


class TestEndToEnd(TestCase):
    service_url = "http://localhost:5070"

    def test_text_extraction(self):
        text = "The International Space Station past above Tokyo on 12 June 2025. "
        text += "Maria Rodriguez was in the Senate when Resolution No. 122 passed."

        data = {"text": text}
        result = requests.post(f"{self.service_url}", data=data)

        entities_dict = result.json()

        self.assertEqual(200, result.status_code)

        self.assertEqual(5, len(entities_dict))

        self.assertEqual("Tokyo", NamedEntity(**entities_dict[0]).text)
        self.assertEqual("LOCATION", NamedEntity(**entities_dict[0]).type)
        self.assertEqual("Tokyo", NamedEntity(**entities_dict[0]).normalized_text)
        self.assertEqual(43, NamedEntity(**entities_dict[0]).character_start)
        self.assertEqual(48, NamedEntity(**entities_dict[0]).character_end)

        self.assertEqual("12 June 2025", NamedEntity(**entities_dict[1]).text)
        self.assertEqual("DATE", NamedEntity(**entities_dict[1]).type)
        self.assertEqual("2025-06-12", NamedEntity(**entities_dict[1]).normalized_text)
        self.assertEqual(52, NamedEntity(**entities_dict[1]).character_start)
        self.assertEqual(64, NamedEntity(**entities_dict[1]).character_end)

        self.assertEqual("Maria Rodriguez", NamedEntity(**entities_dict[2]).text)
        self.assertEqual("PERSON", NamedEntity(**entities_dict[2]).type)
        self.assertEqual("Maria Rodriguez", NamedEntity(**entities_dict[2]).normalized_text)
        self.assertEqual(66, NamedEntity(**entities_dict[2]).character_start)
        self.assertEqual(81, NamedEntity(**entities_dict[2]).character_end)

        self.assertEqual("Senate", NamedEntity(**entities_dict[3]).text)
        self.assertEqual("Senate", NamedEntity(**entities_dict[3]).normalized_text)
        self.assertEqual("ORGANIZATION", NamedEntity(**entities_dict[3]).type)
        self.assertEqual(93, NamedEntity(**entities_dict[3]).character_start)
        self.assertEqual(99, NamedEntity(**entities_dict[3]).character_end)

        self.assertEqual("Resolution No. 122", NamedEntity(**entities_dict[4]).text)
        self.assertEqual("Resolution No. 122", NamedEntity(**entities_dict[4]).normalized_text)
        self.assertEqual("LAW", NamedEntity(**entities_dict[4]).type)
        self.assertEqual(105, NamedEntity(**entities_dict[4]).character_start)
        self.assertEqual(123, NamedEntity(**entities_dict[4]).character_end)

    def test_text_extraction_for_dates(self):
        text = "Today is 13th January 2024. It should be Wednesday"
        data = {"text": text}
        result = requests.post(f"{self.service_url}", data=data)

        entities_dict = result.json()
        entity = NamedEntity(**entities_dict[0])

        self.assertEqual(200, result.status_code)

        self.assertEqual(1, len(entities_dict))

        self.assertEqual("13th January 2024", entity.text)
        self.assertEqual("DATE", entity.type)
        self.assertEqual("2024-01-13", entity.normalized_text)
        self.assertEqual(9, entity.character_start)
        self.assertEqual(26, entity.character_end)

    # def test_pdf_extraction(self):
    #     pdf_path: Path = Path(ROOT_PATH, "src", "tests", "end_to_end", "test_pdfs", "test_document.pdf")
    #     with open(pdf_path, "rb") as pdf_file:
    #         files = {"file": pdf_file}
    #         response = requests.post(f"{self.service_url}/pdf", files=files)
    #         response_json = response.json()
    #         self.assertEqual(200, response.status_code)
    #         self.assertEqual(10, len(response_json))
    #         self.assertEqual("PERSON", response_json[0]["type"])
    #         self.assertEqual("Maria Rodriguez", response_json[0]["text"])
    #         self.assertEqual("Maria Rodriguez", response_json[0]["normalized_text"])
    #         self.assertEqual(0, response_json[0]["character_start"])
    #         self.assertEqual(15, response_json[0]["character_end"])
    #         expected_segment_text: str = (
    #             "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023."
    #         )
    #         self.assertEqual(expected_segment_text, response_json[0]["segment_text"])
    #         self.assertEqual(1, response_json[0]["page_number"])
    #         self.assertEqual(1, response_json[0]["segment_number"])
    #         self.assertEqual(72, response_json[0]["bounding_box"]["left"])
    #         self.assertEqual(74, response_json[0]["bounding_box"]["top"])
