import json
from typing import List
from ollama import Client
from rapidfuzz import fuzz

from ner_in_docker.configuration import OLLAMA_HOST, OLLAMA_MODEL
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.NamedEntityType import NamedEntityType


class GetLLMEntitiesUseCase:

    def __init__(self, model_name: str = None, host: str = None):
        self.model_name = model_name or OLLAMA_MODEL
        self.host = host or OLLAMA_HOST
        self.client = Client(host=self.host)

    @staticmethod
    def remove_overlapping_entities(entities: list[NamedEntity]) -> list[NamedEntity]:
        sorted_entities = sorted(entities, key=lambda x: (x.character_start, -len(x.text)))
        result = []
        last_end = -1
        for entity in sorted_entities:
            if entity.character_start >= last_end:
                result.append(entity)
                last_end = entity.character_end
        return result

    def _build_prompt(self, text: str) -> str:
        return f"""Extract all named entities from the text below. Return ONLY a valid JSON array with no additional text, markdown, or explanations.

Entity types to extract:
- PERSON: Names of people
- ORGANIZATION: Companies, institutions, government agencies
- LOCATION: Cities, countries, geographic locations
- LAW: Legal documents, acts, regulations

Requirements:
1. Extract ALL entity mentions from the text
2. For each entity, provide the exact text as it appears in the original
3. Return ONLY a JSON array
4. Each entity must have: "text" (exact match from original), "type" (one of the types above)

Output format:
[
  {{"text": "Barack Obama", "type": "PERSON"}},
  {{"text": "United Nations", "type": "ORGANIZATION"}},
  {{"text": "Paris", "type": "LOCATION"}},
  {{"text": "Civil Rights Act", "type": "LAW"}}
]

Text to analyze:
{text}

JSON array:"""

    def _find_entity_position(self, entity_text: str, original_text: str, start_search: int = 0) -> tuple[int, int] | None:
        pos = original_text.find(entity_text, start_search)
        if pos != -1:
            return (pos, pos + len(entity_text))

        entity_lower = entity_text.lower()
        original_lower = original_text.lower()
        pos = original_lower.find(entity_lower, start_search)
        if pos != -1:
            return (pos, pos + len(entity_text))

        words = entity_text.split()
        for i in range(len(original_text) - len(entity_text) + 1):
            substring = original_text[i : i + len(entity_text)]
            if fuzz.ratio(entity_text, substring) > 90:
                return (i, i + len(entity_text))

        return None

    def _parse_response(self, response_text: str, original_text: str) -> List[NamedEntity]:
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
                return []

            extracted_entities = []
            used_positions = []

            for entity in entities_data:
                entity_text = entity.get("text", "")
                entity_type = entity.get("type", "").upper()

                if not entity_text or not entity_type:
                    continue

                if entity_type not in {"PERSON", "ORGANIZATION", "LOCATION", "LAW"}:
                    continue

                start_search = 0
                position = None

                while True:
                    temp_position = self._find_entity_position(entity_text, original_text, start_search)
                    if temp_position is None:
                        break

                    is_overlapping = False
                    for used_start, used_end in used_positions:
                        if not (temp_position[1] <= used_start or temp_position[0] >= used_end):
                            is_overlapping = True
                            break

                    if not is_overlapping:
                        position = temp_position
                        break

                    start_search = temp_position[1]

                if position is None:
                    continue

                start, end = position
                used_positions.append((start, end))
                actual_text = original_text[start:end]

                entity_type_enum = {
                    "PERSON": NamedEntityType.PERSON,
                    "ORGANIZATION": NamedEntityType.ORGANIZATION,
                    "LOCATION": NamedEntityType.LOCATION,
                    "LAW": NamedEntityType.LAW,
                }[entity_type]

                extracted_entities.append(
                    NamedEntity(
                        type=entity_type_enum,
                        text=actual_text,
                        normalized_text=actual_text,
                        character_start=start,
                        character_end=end,
                    )
                )

            return extracted_entities

        except json.JSONDecodeError:
            return []
        except Exception:
            return []

    def get_entities(self, text: str) -> list[NamedEntity]:
        prompt = self._build_prompt(text)

        response = self.client.chat(
            model=self.model_name, messages=[{"role": "user", "content": prompt}], options={"temperature": 0.1}
        )

        response_text = response["message"]["content"].strip()
        entities = self._parse_response(response_text, text)
        entities = self.remove_overlapping_entities(entities)

        return entities
