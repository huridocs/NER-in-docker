from abc import ABC, abstractmethod
import re
from typing import List, Optional, Tuple

from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity


class EntityExtractor(ABC):

    @abstractmethod
    def extract(self, text: str) -> List[ExtractedEntity]:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    def warmup(self, sample_text: str = "John Doe works at OpenAI in San Francisco."):
        try:
            self.extract(sample_text)
        except Exception as e:
            print(f"Warning: Warmup failed for {self.get_name()}: {e}")

    def find_entity_position_fuzzy(self, entity_text: str, original_text: str) -> Optional[Tuple[int, int]]:
        start = original_text.find(entity_text)
        if start != -1:
            return (start, start + len(entity_text))

        start = original_text.lower().find(entity_text.lower())
        if start != -1:
            return (start, start + len(entity_text))

        entity_normalized = entity_text.replace("'s", "").replace("'s", "").strip()
        entity_normalized = re.sub(r"\s*-\s*", "-", entity_normalized)
        entity_normalized = re.sub(r"\s+", " ", entity_normalized)

        entity_tokens = entity_normalized.replace("-", " ").split()
        if not entity_tokens:
            return None

        pattern_parts = []
        for i, token in enumerate(entity_tokens):
            escaped_token = re.escape(token)
            pattern_parts.append(escaped_token)
            if i < len(entity_tokens) - 1:
                pattern_parts.append(r"\s*-?\s*")

        pattern = "".join(pattern_parts) + r"(?:\s*'s?)?"

        try:
            match = re.search(pattern, original_text, re.IGNORECASE)
            if match:
                return (match.start(), match.end())
        except re.error:
            pass

        return None
