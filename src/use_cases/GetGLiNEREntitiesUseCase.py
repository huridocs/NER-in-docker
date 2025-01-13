import dateparser
from dateparser.search import search_dates
from gliner import GLiNER
from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType

classifier = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")


class GetGLiNEREntitiesUseCase:

    WINDOW_SIZE = 20
    SLIDE_SIZE = 10

    def __init__(self):
        self.entities: list[NamedEntity] = []

    @staticmethod
    def remove_overlapping_entities(entities: list[NamedEntity]):
        sorted_entities = sorted(entities, key=lambda x: (x.start, -len(x.text)))

        result = []
        last_end = -1

        for entity in sorted_entities:
            if entity.start >= last_end:
                result.append(entity)
                last_end = entity.end

        return result

    @staticmethod
    def convert_to_named_entity_type(window_entities: list[dict]):
        result = []
        for entity in window_entities:
            result.append(
                NamedEntity(
                    type=NamedEntityType.DATE,
                    text=entity["text"],
                    normalized_text=dateparser.parse(entity["text"]).strftime("%Y-%m-%d"),
                    start=entity["start"],
                    end=entity["end"],
                )
            )
        return result

    def iterate_through_windows(self, words):
        last_slide_end_index = 0
        for i in range(0, len(words), self.SLIDE_SIZE):
            window_words = words[i : i + self.WINDOW_SIZE]
            window_text = " ".join(window_words)
            window_entities = classifier.predict_entities(window_text, ["date"])
            window_entities = self.convert_to_named_entity_type(window_entities)

            for entity in window_entities:
                entity.start += last_slide_end_index
                entity.end += last_slide_end_index

            slide_words = words[i : i + self.SLIDE_SIZE]
            slide_text = " ".join(slide_words)
            last_slide_end_index += len(slide_text) + 1
            self.entities.extend(window_entities)

    def extract_dates(self, text: str):
        words = text.split()
        self.iterate_through_windows(words)
        self.entities = [e for e in self.entities if search_dates(e.text)]
        self.entities = self.remove_overlapping_entities(self.entities)
        return [entity for entity in self.entities if search_dates(entity.text)]
