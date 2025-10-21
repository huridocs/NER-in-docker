import re
from typing import List

from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.NamedEntityType import NamedEntityType


UN_CODE_REGEX = r"^(A|S|E|T|ST)/([A-Z]+\.\d+|[A-Z]{2,}|\d{1,4})(/([A-Z]+\.\d+|[A-Z]{2,}|\d{1,4}))*(/(Rev|Add|Corr)\.\d+)*$"


class GetDocumentCodeUseCase:
    def __init__(self):
        self.pattern = re.compile(UN_CODE_REGEX)

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

    def find_un_codes(self, text: str) -> List[str]:
        words = re.split(r"\s+|,|\(|\)|\[|\]", text)

        found_codes = []
        for word in words:
            clean_word = word.strip(";:.").upper()

            if self.pattern.fullmatch(clean_word):
                found_codes.append(clean_word)

        return found_codes

    def extract_document_codes(self, text: str) -> list[NamedEntity]:
        entities: list[NamedEntity] = []
        codes = self.find_un_codes(text)

        for code in codes:
            start_index = text.upper().find(code)
            if start_index == -1:
                continue

            end_index = start_index + len(code)

            named_entity = NamedEntity(
                type=NamedEntityType.DOCUMENT_CODE,
                text=text[start_index:end_index],
                character_start=start_index,
                character_end=end_index,
            )

            try:
                named_entity = named_entity.get_with_normalize_entity_text()
                entities.append(named_entity)
            except Exception:
                pass

        entities = self.remove_overlapping_entities(entities)
        return entities
