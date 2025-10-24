import requests
from typing import List

from ner_in_docker.drivers.benchmarks.EntityExtractor import EntityExtractor
from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity


class NerServiceExtractor(EntityExtractor):
    def __init__(self, service_url: str = "http://localhost:5070/", namespace: str = "benchmark"):
        self.service_url = service_url
        self.namespace = namespace

    def get_name(self) -> str:
        return f"REST API ({self.service_url})"

    def extract(self, text: str) -> List[ExtractedEntity]:
        try:
            response = requests.post(
                self.service_url, files={"text": (None, text), "namespace": (None, self.namespace)}, timeout=30
            )
            response.raise_for_status()

            result = response.json()

            predicted_entities = result.get("entities", [])

            standardized = []
            for entity in predicted_entities:
                standardized.append(
                    ExtractedEntity(
                        text=entity.get("text", ""),
                        type=entity.get("type", "").upper(),
                        character_start=entity.get("character_start", -1),
                        character_end=entity.get("character_end", -1),
                    )
                )

            return standardized

        except Exception as e:
            print(f"Error calling NER service: {e}")
            return []
