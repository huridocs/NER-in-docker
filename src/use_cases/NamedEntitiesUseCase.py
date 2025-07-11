from domain.NamedEntity import NamedEntity
from domain.Segment import Segment
from use_cases.GetFlairEntitiesUseCase import GetFlairEntitiesUseCase
from use_cases.GetGLiNEREntitiesUseCase import GetGLiNEREntitiesUseCase


class NamedEntitiesUseCase:
    def __init__(self):
        self.date_extractor = GetGLiNEREntitiesUseCase()
        self.entity_extractor = GetFlairEntitiesUseCase()

    def get_entities_from_text(self, text: str) -> list[NamedEntity]:
        entities = []
        entities.extend(self.date_extractor.extract_dates(text))
        entities.extend(self.entity_extractor.get_entities(text))
        return sorted(entities, key=lambda x: x.character_start)

    def get_entities_from_segments(self, segments: list[Segment]) -> list[NamedEntity]:
        entities: list[NamedEntity] = []
        for segment in segments:
            named_entities: list[NamedEntity] = self.get_entities_from_text(segment.text)
            pdf_named_entities = [NamedEntity.from_segment(named_entity, segment) for named_entity in named_entities]
            entities.extend(pdf_named_entities)
        return entities
