from domain.NamedEntity import NamedEntity
from use_cases.GetFlairEntitiesUseCase import GetFlairEntitiesUseCase
from use_cases.GetGLiNEREntitiesUseCase import GetGLiNEREntitiesUseCase


class NamedEntitiesFromTextUseCase:
    def __init__(self):
        self.date_extractor = GetGLiNEREntitiesUseCase()
        self.entity_extractor = GetFlairEntitiesUseCase()

    def get_entities(self, text: str) -> list[NamedEntity]:
        entities = []
        entities.extend(self.date_extractor.extract_dates(text))
        entities.extend(self.entity_extractor.get_entities(text))
        return sorted(entities, key=lambda x: x.character_start)
