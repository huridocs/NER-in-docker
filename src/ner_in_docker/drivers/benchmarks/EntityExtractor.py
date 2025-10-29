from abc import ABC, abstractmethod
from typing import List

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
