import json
from typing import List
from ollama import Client

from ner_in_docker.drivers.benchmarks.EntityExtractor import EntityExtractor
from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity


class QwenExtractor(EntityExtractor):

    def __init__(self, model_name: str = "qwen3:14b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.client = Client(host=host)

    def get_name(self) -> str:
        return f"Qwen LLM ({self.model_name})"

    def extract(self, text: str) -> List[ExtractedEntity]:

        prompt = f"""You are a Named Entity Recognition system. Extract ALL entities from the text and return ONLY a JSON array.

Task: Extract entities of these types:
- PERSON: Names of people
- ORGANIZATION: Companies, institutions, agencies
- LOCATION: Cities, countries, geographic locations

Instructions:
1. Find ALL entity mentions in the text
2. Return ONLY a valid JSON array
3. Each entity must have: text, type
4. Do NOT include markdown, explanations, or extra text

Example output format:
[
{{"text": "John Doe", "type": "PERSON"}},
{{"text": "New York", "type": "LOCATION"}}
]

Text to analyze:
{text}

Output (JSON array only):"""

        response = self.client.chat(model=self.model_name, messages=[{"role": "user", "content": prompt}])

        response_text = response["message"]["content"].strip()

        entities = self._parse_response(response_text, text)
        return entities

    def _parse_response(self, response_text: str, original_text: str) -> List[ExtractedEntity]:
        try:
            response_text = response_text.strip()
            if "<think>" in response_text and "</think>" in response_text:
                think_end = response_text.index("</think>")
                response_text = response_text[think_end + len("</think>") :].strip()

            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]

            if response_text.endswith("```"):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            entities_data = json.loads(response_text)

            if isinstance(entities_data, dict) and "entities" in entities_data:
                entities_data = entities_data["entities"]

            if not isinstance(entities_data, list):
                print(f"Warning: Expected list, got {type(entities_data)}")
                return []

            extracted_entities = []
            for entity in entities_data:
                entity_text = entity.get("text", entity.get("source_text", ""))
                entity_type = entity.get("type", entity.get("entity_type", "")).upper()

                if not entity_text or not entity_type:
                    continue

                start = entity.get("start", entity.get("character_start", -1))
                end = entity.get("end", entity.get("character_end", -1))

                if start == -1 or end == -1:
                    position = self.find_entity_position_fuzzy(entity_text, original_text)
                    if position:
                        start, end = position
                    else:
                        continue

                actual_text = original_text[start:end]

                extracted_entities.append(
                    ExtractedEntity(text=actual_text, type=entity_type, character_start=start, character_end=end)
                )

            return extracted_entities

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response_text[:200]}")
            return []
        except Exception as e:
            print(f"Error parsing response: {e}")
            return []


if __name__ == "__main__":
    extractor = QwenExtractor()
    sample_text = "Barack Obama was born in Hawaii and served as the 44th President of the United States."
    entities = extractor.extract(sample_text)
    for entity in entities:
        print(f"Entity: {entity.text}, Type: {entity.type}, Start: {entity.character_start}, End: {entity.character_end}")
