from domain.NamedEntity import NamedEntity
from use_cases.GetFlairEntitiesUseCase import GetFlairEntitiesUseCase
from use_cases.GetGLiNEREntitiesUseCase import GetGLiNEREntitiesUseCase


class NamedEntitiesFromTextUseCase:
    def __init__(self, text: str):
        self.text = text
        self.date_extractor = GetGLiNEREntitiesUseCase()
        self.entity_extractor = GetFlairEntitiesUseCase()

    def get_entities(self) -> list[NamedEntity]:
        entities = []
        entities.extend(self.date_extractor.extract_dates(self.text))
        entities.extend(self.entity_extractor.get_entities(self.text))
        return sorted(entities, key=lambda x: x.start)
