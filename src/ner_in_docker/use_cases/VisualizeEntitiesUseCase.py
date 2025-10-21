from pathlib import Path

from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.ports.VisualizationRepository import VisualizationRepository


class VisualizeEntitiesUseCase:
    def __init__(self, visualization_repository: VisualizationRepository):
        self.visualization_repository = visualization_repository

    def create_annotated_pdf(self, pdf_path: Path, named_entities: list[NamedEntity]) -> Path:
        return self.visualization_repository.create_pdf_with_annotations(pdf_path, named_entities)
