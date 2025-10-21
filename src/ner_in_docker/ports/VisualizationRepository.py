from abc import ABC, abstractmethod
from pathlib import Path

from ner_in_docker.domain.NamedEntity import NamedEntity


class VisualizationRepository(ABC):
    @abstractmethod
    def create_pdf_with_annotations(self, pdf_path: Path, named_entities: list[NamedEntity]) -> Path:
        pass
