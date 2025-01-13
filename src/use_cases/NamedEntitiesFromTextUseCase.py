from domain.NamedEntity import NamedEntity


class NamedEntitiesFromTextUseCase:
    def __init__(self, text: str):
        self.text = text

    def get_entities(self) -> list[NamedEntity]:
        return list()
