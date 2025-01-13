from flair.nn import Classifier
from domain.NamedEntity import NamedEntity
from flair.data import Sentence, Span
from domain.NamedEntityType import NamedEntityType

flair_model = Classifier.load("ner-ontonotes-large")


class GetFlairEntitiesUseCase:

    @staticmethod
    def remove_overlapping_entities(entities: list[NamedEntity]) -> list[NamedEntity]:
        sorted_entities = sorted(entities, key=lambda x: (x.start, -len(x.text)))
        result = []
        last_end = -1
        for entity in sorted_entities:
            if entity.start >= last_end:
                result.append(entity)
                last_end = entity.end
        return result

    @staticmethod
    def convert_to_named_entity_type(flair_raw_result: list[Span]) -> list[NamedEntity]:
        result = []
        for entity in flair_raw_result:
            if entity.tag not in {"ORG", "PERSON", "LAW", "GPE"}:
                continue
            result.append(
                NamedEntity(
                    type=NamedEntityType.from_flair_type(entity.tag),
                    text=entity.text,
                    normalized_text=entity.text,
                    start=entity.start_position,
                    end=entity.end_position,
                )
            )
        return result

    def get_entities(self, text: str) -> list[NamedEntity]:
        sentence = Sentence(text)
        flair_model.predict(sentence)
        flair_raw_result: list[Span] = sentence.get_spans("ner")
        entities = self.convert_to_named_entity_type(flair_raw_result)
        return self.remove_overlapping_entities(entities)
