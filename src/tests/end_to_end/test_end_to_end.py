from unittest import TestCase
import requests

from drivers.rest.GroupResponse import GroupResponse
from drivers.rest.NamedEntityResponse import NamedEntityResponse


class TestEndToEnd(TestCase):
    service_url = "http://localhost:5070"

    def test_text_extraction(self):
        text = "The International Space Station past above Tokyo on 12 June 2025. "
        text += "Maria Rodriguez was in the Senate when Resolution No. 122 passed on twelve of June 2025."

        data = {"text": text}
        result = requests.post(f"{self.service_url}", data=data)

        entities_dict = result.json()["entities"]
        groups_dict = result.json()["groups"]

        self.assertEqual(200, result.status_code)

        self.assertEqual(6, len(entities_dict))

        self.assertEqual("Tokyo", NamedEntityResponse(**entities_dict[0]).text)
        self.assertEqual("LOCATION", NamedEntityResponse(**entities_dict[0]).type)
        self.assertEqual("Tokyo", NamedEntityResponse(**entities_dict[0]).group_name)
        self.assertEqual(43, NamedEntityResponse(**entities_dict[0]).character_start)
        self.assertEqual(48, NamedEntityResponse(**entities_dict[0]).character_end)

        self.assertEqual("12 June 2025", NamedEntityResponse(**entities_dict[1]).text)
        self.assertEqual("DATE", NamedEntityResponse(**entities_dict[1]).type)
        self.assertEqual("2025-06-12", NamedEntityResponse(**entities_dict[1]).group_name)
        self.assertEqual(52, NamedEntityResponse(**entities_dict[1]).character_start)
        self.assertEqual(64, NamedEntityResponse(**entities_dict[1]).character_end)

        self.assertEqual("Maria Rodriguez", NamedEntityResponse(**entities_dict[2]).text)
        self.assertEqual("PERSON", NamedEntityResponse(**entities_dict[2]).type)
        self.assertEqual("Maria Rodriguez", NamedEntityResponse(**entities_dict[2]).group_name)
        self.assertEqual(66, NamedEntityResponse(**entities_dict[2]).character_start)
        self.assertEqual(81, NamedEntityResponse(**entities_dict[2]).character_end)

        self.assertEqual("Senate", NamedEntityResponse(**entities_dict[3]).text)
        self.assertEqual("Senate", NamedEntityResponse(**entities_dict[3]).group_name)
        self.assertEqual("ORGANIZATION", NamedEntityResponse(**entities_dict[3]).type)
        self.assertEqual(93, NamedEntityResponse(**entities_dict[3]).character_start)
        self.assertEqual(99, NamedEntityResponse(**entities_dict[3]).character_end)

        self.assertEqual("Resolution No. 122", NamedEntityResponse(**entities_dict[4]).text)
        self.assertEqual("Resolution No. 122", NamedEntityResponse(**entities_dict[4]).group_name)
        self.assertEqual("LAW", NamedEntityResponse(**entities_dict[4]).type)
        self.assertEqual(105, NamedEntityResponse(**entities_dict[4]).character_start)
        self.assertEqual(123, NamedEntityResponse(**entities_dict[4]).character_end)

        self.assertEqual("twelve of June 2025", NamedEntityResponse(**entities_dict[5]).text)
        self.assertEqual("DATE", NamedEntityResponse(**entities_dict[5]).type)
        self.assertEqual("2025-06-12", NamedEntityResponse(**entities_dict[5]).group_name)

        self.assertEqual(5, len(groups_dict))

        self.assertEqual("Tokyo", GroupResponse(**groups_dict[0]).group_name)
        self.assertEqual(1, len(GroupResponse(**groups_dict[0]).entities_ids))
        self.assertEqual(1, len(GroupResponse(**groups_dict[0]).entities_text))
        self.assertEqual("Tokyo", GroupResponse(**groups_dict[0]).entities_text[0])
        self.assertEqual(0, GroupResponse(**groups_dict[0]).entities_ids[0])

        self.assertEqual("2025-06-12", GroupResponse(**groups_dict[1]).group_name)
        self.assertEqual(2, len(GroupResponse(**groups_dict[1]).entities_ids))
        self.assertEqual(2, len(GroupResponse(**groups_dict[1]).entities_text))
        self.assertEqual("12 June 2025", GroupResponse(**groups_dict[1]).entities_text[0])
        self.assertEqual(1, GroupResponse(**groups_dict[1]).entities_ids[0])
        self.assertEqual("twelve of June 2025", GroupResponse(**groups_dict[1]).entities_text[1])
        self.assertEqual(5, GroupResponse(**groups_dict[1]).entities_ids[1])

        self.assertEqual("Maria Rodriguez", GroupResponse(**groups_dict[2]).group_name)
        self.assertEqual(1, len(GroupResponse(**groups_dict[2]).entities_ids))
        self.assertEqual(1, len(GroupResponse(**groups_dict[2]).entities_text))
        self.assertEqual("Maria Rodriguez", GroupResponse(**groups_dict[2]).entities_text[0])
        self.assertEqual(2, GroupResponse(**groups_dict[2]).entities_ids[0])

        self.assertEqual("Senate", GroupResponse(**groups_dict[3]).group_name)
        self.assertEqual(1, len(GroupResponse(**groups_dict[3]).entities_ids))
        self.assertEqual(1, len(GroupResponse(**groups_dict[3]).entities_text))
        self.assertEqual("Senate", GroupResponse(**groups_dict[3]).entities_text[0])
        self.assertEqual(3, GroupResponse(**groups_dict[3]).entities_ids[0])

        self.assertEqual("Resolution No. 122", GroupResponse(**groups_dict[4]).group_name)
        self.assertEqual(1, len(GroupResponse(**groups_dict[4]).entities_ids))
        self.assertEqual(1, len(GroupResponse(**groups_dict[4]).entities_text))
        self.assertEqual("Resolution No. 122", GroupResponse(**groups_dict[4]).entities_text[0])
        self.assertEqual(4, GroupResponse(**groups_dict[4]).entities_ids[0])

    def test_text_extraction_for_dates(self):
        text = "Today is 13th January 2024. It should be Wednesday"
        data = {"text": text}
        result = requests.post(f"{self.service_url}", data=data)

        entities_dict = result.json()
        entity = NamedEntityResponse(**entities_dict[0])

        self.assertEqual(200, result.status_code)

        self.assertEqual(1, len(entities_dict))

        self.assertEqual("13th January 2024", entity.text)
        self.assertEqual("DATE", entity.type)
        self.assertEqual("2024-01-13", entity.group_name)
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
