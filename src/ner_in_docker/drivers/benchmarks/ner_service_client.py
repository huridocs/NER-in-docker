import requests
from typing import List, Dict


class NERServiceClient:

    def __init__(self, service_url: str = "http://localhost:5070/"):
        self.service_url = service_url

    def extract_entities(self, text: str, namespace: str = "benchmark") -> List[Dict]:
        try:
            response = requests.post(
                self.service_url, files={"text": (None, text), "namespace": (None, namespace)}, timeout=30
            )
            response.raise_for_status()

            result = response.json()

            if "entities" in result:
                return result["entities"]
            else:
                return []

        except Exception as e:
            print(f"Error calling NER service: {e}")
            return []
