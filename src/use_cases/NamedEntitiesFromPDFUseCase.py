from domain.NamedEntities import NamedEntitiesGrouped


class NamedEntitiesFromPDFUseCase:
    def __init__(self, text: str):
        self.text = text

    def get_entities(self) -> NamedEntitiesGrouped:
        pass
