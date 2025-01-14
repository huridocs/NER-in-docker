from unittest import TestCase

import requests

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
