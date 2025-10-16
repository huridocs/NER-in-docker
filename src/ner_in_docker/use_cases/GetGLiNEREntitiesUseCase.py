from pathlib import Path

import dateparser
from dateparser.search import search_dates
from gliner import GLiNER
from ner_in_docker.configuration import MODELS_PATH
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.NamedEntityType import NamedEntityType

gliner_path = Path(MODELS_PATH, "gliner")
classifier = GLiNER.from_pretrained(gliner_path) if gliner_path.exists() else None


class GetGLiNEREntitiesUseCase:

    WINDOW_SIZE = 20
    SLIDE_SIZE = 10

    def __init__(self):
        self.entities: list[NamedEntity] = list()

    @staticmethod
    def remove_overlapping_entities(entities: list[NamedEntity]):
        sorted_entities = sorted(entities, key=lambda x: (x.character_start, -len(x.text)))

        result = []
        last_end = -1

        for entity in sorted_entities:
            if entity.character_start >= last_end:
                result.append(entity)
                last_end = entity.character_end

        return result

    @staticmethod
    def convert_to_named_entity_type(window_entities: list[dict]):
        result = []
        for entity in window_entities:
            named_entity = NamedEntity(
                type=NamedEntityType.DATE, text=entity["text"], character_start=entity["start"], character_end=entity["end"]
            )
            try:
                named_entity = named_entity.get_with_normalize_entity_text()
                result.append(named_entity)
            except Exception:
                pass
        return result

    def iterate_through_windows(self, words):
        last_slide_end_index = 0
        for i in range(0, len(words), self.SLIDE_SIZE):
            window_words = words[i : i + self.WINDOW_SIZE]
            window_text = " ".join(window_words)
            window_entities = classifier.predict_entities(window_text, ["date"])
            window_entities = self.convert_to_named_entity_type(window_entities)

            for entity in window_entities:
                entity.character_start += last_slide_end_index
                entity.character_end += last_slide_end_index

            slide_words = words[i : i + self.SLIDE_SIZE]
            slide_text = " ".join(slide_words)
            last_slide_end_index += len(slide_text) + 1
            self.entities.extend(window_entities)

    @staticmethod
    def remove_uncompleted_dates(entities):
        result = list()
        for entity in entities:
            if len(entity.text.split()) < 3:
                continue
            result.append(entity)

        return result

    def extract_dates(self, text: str):
        self.entities: list[NamedEntity] = list()
        words = text.split()
        self.iterate_through_windows(words)
        self.entities = [e for e in self.entities if search_dates(e.text)]
        self.entities = self.remove_overlapping_entities(self.entities)
        self.entities = self.remove_uncompleted_dates(self.entities)
        return self.entities
