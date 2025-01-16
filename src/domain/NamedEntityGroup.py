from pydantic import BaseModel

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from rapidfuzz import fuzz


class NamedEntityGroup(BaseModel):
    type: NamedEntityType
    name: str
    named_entities: list[NamedEntity] = list()

    def is_same_type(self, named_entity: NamedEntity) -> bool:
        return self.type == named_entity.type

    def is_exact_match(self, named_entity: NamedEntity) -> bool:
        return self.name == named_entity.normalized_text

    def is_similar_entity(self, named_entity: NamedEntity) -> bool:
        normalized_entity = named_entity.normalize_entity_text()
        entity_normalized_text = normalized_entity.normalized_text

        for each_normalized_text in [x.normalized_text for x in self.named_entities]:
            if self.equal_but_less_words(entity_normalized_text, each_normalized_text):
                return True

            if self.similar_text(each_normalized_text, entity_normalized_text):
                return True

            if self.is_abbreviation(each_normalized_text, entity_normalized_text):
                return True

        return False

    @staticmethod
    def equal_but_less_words(text: str, other_text: str) -> bool:
        if len(text) < 4 or len(other_text) < 4:
            return False

        text_words = text.split()
        other_text_words = other_text.split()

        words_in_both = [x for x in text_words if x in other_text_words]

        if len(words_in_both) < 2:
            return False

        shorter_name_words = text_words if len(text_words) < len(other_text_words) else other_text_words
        longer_name_words = other_text_words if shorter_name_words == text_words else text_words

        for word in shorter_name_words:
            if word not in longer_name_words:
                return False

        return True

    @staticmethod
    def is_abbreviation(text: str, other_text: str) -> bool:
        if len(text) < 4 or len(other_text) < 4:
            return False

        text_words = text.split()
        other_text_words = other_text.split()

        text_one_letter_words = [x for x in text_words if len(x) == 1]
        other_text_one_letter_words = [x for x in other_text_words if len(x) == 1]

        if not text_one_letter_words and not other_text_one_letter_words:
            return False

        text_first_letters = "".join([x[0] for x in text_words])
        other_text_first_letters = "".join([x[0] for x in other_text_words])

        if text_first_letters != other_text_first_letters:
            return False

        for text_word, other_text_word in zip(text_words, other_text_words):
            if len(text_word) == 1 or len(other_text_word) == 1:
                continue

            if text_word != other_text_word:
                return False

        return True

    @staticmethod
    def similar_text(text: str, other_text: str):
        if abs(len(text) - len(other_text)) > 1:
            return False

        length = max(len(text), len(other_text))
        threshold = 100 * (length - 1) / length if length > 10 else 100
        return fuzz.ratio(text, other_text) >= threshold

    def belongs_to_group(self, named_entity: NamedEntity) -> bool:
        if not self.is_same_type(named_entity):
            return False

        if self.is_exact_match(named_entity):
            return True

        return self.is_similar_entity(named_entity)

    def add_named_entity(self, named_entity: NamedEntity):
        if self.type == NamedEntityType.DATE and named_entity.normalized_text:
            self.name = named_entity.normalized_text
            self.named_entities.append(named_entity.normalize_entity_text())
            return

        if len(named_entity.text) > len(self.name):
            self.name = named_entity.text

        self.named_entities.append(named_entity.normalize_entity_text())
