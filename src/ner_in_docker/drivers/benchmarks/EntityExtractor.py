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
