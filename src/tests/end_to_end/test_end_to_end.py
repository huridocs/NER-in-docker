from pathlib import Path
from unittest import TestCase
import requests

from configuration import ROOT_PATH
from drivers.rest.GroupResponse import GroupResponse
from drivers.rest.NamedEntityResponse import NamedEntityResponse
from drivers.rest.PDFNamedEntityResponse import PDFNamedEntityResponse


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
        self.assertEqual("LOCATION", GroupResponse(**groups_dict[0]).type)
        self.assertEqual(1, len(GroupResponse(**groups_dict[0]).entities_ids))
        self.assertEqual(1, len(GroupResponse(**groups_dict[0]).entities_text))
        self.assertEqual("Tokyo", GroupResponse(**groups_dict[0]).entities_text[0])
        self.assertEqual(0, GroupResponse(**groups_dict[0]).entities_ids[0])

        self.assertEqual("2025-06-12", GroupResponse(**groups_dict[1]).group_name)
        self.assertEqual("DATE", GroupResponse(**groups_dict[1]).type)
        self.assertEqual(2, len(GroupResponse(**groups_dict[1]).entities_ids))
        self.assertEqual(2, len(GroupResponse(**groups_dict[1]).entities_text))
        self.assertEqual("12 June 2025", GroupResponse(**groups_dict[1]).entities_text[0])
        self.assertEqual(1, GroupResponse(**groups_dict[1]).entities_ids[0])
        self.assertEqual("twelve of June 2025", GroupResponse(**groups_dict[1]).entities_text[1])
        self.assertEqual(5, GroupResponse(**groups_dict[1]).entities_ids[1])

        self.assertEqual("Maria Rodriguez", GroupResponse(**groups_dict[2]).group_name)
        self.assertEqual("PERSON", GroupResponse(**groups_dict[2]).type)
        self.assertEqual(1, len(GroupResponse(**groups_dict[2]).entities_ids))
        self.assertEqual(1, len(GroupResponse(**groups_dict[2]).entities_text))
        self.assertEqual("Maria Rodriguez", GroupResponse(**groups_dict[2]).entities_text[0])
        self.assertEqual(2, GroupResponse(**groups_dict[2]).entities_ids[0])

        self.assertEqual("Senate", GroupResponse(**groups_dict[3]).group_name)
        self.assertEqual("ORGANIZATION", GroupResponse(**groups_dict[3]).type)
        self.assertEqual(1, len(GroupResponse(**groups_dict[3]).entities_ids))
        self.assertEqual(1, len(GroupResponse(**groups_dict[3]).entities_text))
        self.assertEqual("Senate", GroupResponse(**groups_dict[3]).entities_text[0])
        self.assertEqual(3, GroupResponse(**groups_dict[3]).entities_ids[0])

        self.assertEqual("Resolution No. 122", GroupResponse(**groups_dict[4]).group_name)
        self.assertEqual("LAW", GroupResponse(**groups_dict[4]).type)
        self.assertEqual(1, len(GroupResponse(**groups_dict[4]).entities_ids))
        self.assertEqual(1, len(GroupResponse(**groups_dict[4]).entities_text))
        self.assertEqual("Resolution No. 122", GroupResponse(**groups_dict[4]).entities_text[0])
        self.assertEqual(4, GroupResponse(**groups_dict[4]).entities_ids[0])

    def test_text_extraction_for_dates(self):
        text = "Today is 13th of January 2024. One month later it will be 13th of February. "
        text += "My birthday this year is January 13th of 2024."
        data = {"text": text}
        result = requests.post(f"{self.service_url}", data=data)

        entities_dict = result.json()["entities"]
        groups_dict = result.json()["groups"]
        entity_1 = NamedEntityResponse(**entities_dict[0])
        entity_2 = NamedEntityResponse(**entities_dict[1])
        entity_3 = NamedEntityResponse(**entities_dict[2])

        group_1 = GroupResponse(**groups_dict[0])
        group_2 = GroupResponse(**groups_dict[1])

        self.assertEqual(200, result.status_code)

        self.assertEqual(3, len(entities_dict))

        self.assertEqual("13th of January 2024", entity_1.text)
        self.assertEqual("DATE", entity_1.type)
        self.assertEqual("2024-01-13", entity_1.group_name)
        self.assertEqual(9, entity_1.character_start)
        self.assertEqual(29, entity_1.character_end)

        self.assertEqual("13th of February", entity_2.text)
        self.assertEqual("DATE", entity_2.type)
        self.assertEqual("13th of February", entity_2.group_name)
        self.assertEqual(58, entity_2.character_start)
        self.assertEqual(74, entity_2.character_end)

        self.assertEqual("January 13th of 2024", entity_3.text)
        self.assertEqual("DATE", entity_3.type)
        self.assertEqual("2024-01-13", entity_3.group_name)
        self.assertEqual(101, entity_3.character_start)
        self.assertEqual(121, entity_3.character_end)

        self.assertEqual(2, len(groups_dict))

        self.assertEqual("2024-01-13", group_1.group_name)
        self.assertEqual("DATE", group_1.type)
        self.assertEqual(2, len(group_1.entities_ids))
        self.assertEqual(2, len(group_1.entities_text))
        self.assertEqual("13th of January 2024", group_1.entities_text[0])
        self.assertEqual("January 13th of 2024", group_1.entities_text[1])
        self.assertEqual(0, group_1.entities_ids[0])
        self.assertEqual(2, group_1.entities_ids[1])

        self.assertEqual("13th of February", group_2.group_name)
        self.assertEqual("DATE", group_2.type)
        self.assertEqual(1, len(group_2.entities_ids))
        self.assertEqual(1, len(group_2.entities_text))
        self.assertEqual("13th of February", group_2.entities_text[0])
        self.assertEqual(1, group_2.entities_ids[0])

    def test_pdf_extraction(self):
        pdf_path: Path = Path(ROOT_PATH, "src", "tests", "end_to_end", "test_pdfs", "test_document.pdf")
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            response = requests.post(f"{self.service_url}/pdf", files=files)

        entities_dict = response.json()["entities"]
        groups_dict = response.json()["groups"]

        entity_0 = PDFNamedEntityResponse(**entities_dict[0])
        entity_9 = PDFNamedEntityResponse(**entities_dict[9])
        group_0 = GroupResponse(**groups_dict[0])
        group_7 = GroupResponse(**groups_dict[7])

        self.assertEqual(200, response.status_code)

        self.assertEqual(10, len(entities_dict))

        self.assertEqual("Maria Diaz Rodriguez", entity_0.group_name)
        self.assertEqual("PERSON", entity_0.type)
        self.assertEqual("Maria Rodriguez", entity_0.text)
        segment_text: str = "Maria Rodriguez visited the Louvre Museum in Paris, France, on Wednesday, July 12, 2023."
        self.assertEqual(segment_text, entity_0.segment.text)
        self.assertEqual(1, entity_0.segment.page_number)
        self.assertEqual(1, entity_0.segment.segment_number)
        self.assertEqual(0, entity_0.segment.character_start)
        self.assertEqual(15, entity_0.segment.character_end)
        self.assertEqual(72, entity_0.segment.bounding_box.left)
        self.assertEqual(74, entity_0.segment.bounding_box.top)
        self.assertEqual(430, entity_0.segment.bounding_box.width)
        self.assertEqual(34, entity_0.segment.bounding_box.height)

        self.assertEqual("Resolution No. 122", entity_9.text)
        self.assertEqual("LAW", entity_9.type)
        self.assertEqual("Resolution No. 122", entity_9.group_name)
        segment_text: str = "The Senate passed Resolution No. 122, establishing a set of rules for the impeachment trial."
        self.assertEqual(segment_text, entity_9.segment.text)
        self.assertEqual(1, entity_9.segment.page_number)
        self.assertEqual(5, entity_9.segment.segment_number)
        self.assertEqual(18, entity_9.segment.character_start)
        self.assertEqual(36, entity_9.segment.character_end)
        self.assertEqual(72, entity_9.segment.bounding_box.left)
        self.assertEqual(351, entity_9.segment.bounding_box.top)
        self.assertEqual(440, entity_9.segment.bounding_box.width)
        self.assertEqual(35, entity_9.segment.bounding_box.height)

        self.assertEqual(8, len(groups_dict))

        self.assertEqual("Maria Diaz Rodriguez", group_0.group_name)
        self.assertEqual("PERSON", group_0.type)
        self.assertEqual(3, len(group_0.entities_ids))
        self.assertEqual(3, len(group_0.entities_text))
        self.assertEqual([0, 5, 6], group_0.entities_ids)
        self.assertEqual(["Maria Rodriguez", "Maria Diaz Rodriguez", "M.D. Rodriguez"], group_0.entities_text)

        self.assertEqual("Resolution No. 122", group_7.group_name)
        self.assertEqual("LAW", group_7.type)
        self.assertEqual(1, len(group_7.entities_ids))
        self.assertEqual(1, len(group_7.entities_text))
        self.assertEqual(["Resolution No. 122"], group_7.entities_text)
        self.assertEqual([9], group_7.entities_ids)
