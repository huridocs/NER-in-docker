from pydantic import BaseModel

from domain.NamedEntity import NamedEntity
from domain.NamedEntityType import NamedEntityType
from rapidfuzz import fuzz

from domain.PDFNamedEntity import PDFNamedEntity
from domain.PDFSegment import PDFSegment
import re


class NamedEntityGroup(BaseModel):
    type: NamedEntityType
    name: str
    named_entities: list[NamedEntity | PDFNamedEntity] = list()
    pdf_segment: PDFSegment = None

    def is_same_type(self, named_entity: NamedEntity) -> bool:
        return self.type == named_entity.type

    def is_exact_match(self, named_entity: NamedEntity) -> bool:
        return self.name == named_entity.normalized_text

    def is_similar_entity(self, named_entity: NamedEntity) -> bool:
        normalized_entity = named_entity.get_with_normalize_entity_text()
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

    def is_same_group(self, other_group: "NamedEntityGroup") -> bool:
        if self.type != other_group.type:
            return False

        for entity in other_group.named_entities:
            if self.belongs_to_group(entity):
                return True

        return False

    def add_named_entity(self, named_entity: NamedEntity):
        if self.type == NamedEntityType.DATE and named_entity.normalized_text:
            self.name = named_entity.normalized_text
            self.named_entities.append(named_entity.get_with_normalize_entity_text())
            return

        if len(named_entity.text) > len(self.name):
            self.name = named_entity.text

        self.named_entities.append(named_entity.get_with_normalize_entity_text())

    def get_references_in_text(self, text: str) -> list[tuple[int, int]]:
        if self.type != NamedEntityType.REFERENCE_DESTINATION:
            return []

        original_name = self.name.strip()
        stripped_text = text.strip()

        if not original_name or not stripped_text:
            return []

        search_patterns = set()
        search_patterns.add(original_name)

        if ": " in original_name:
            parts = original_name.split(": ", 1)
            if len(parts) == 2:
                part_before_colon = parts[0].strip()
                part_after_colon = parts[1].strip()
                if part_before_colon:
                    search_patterns.add(part_before_colon)
                if part_after_colon:
                    search_patterns.add(part_after_colon)

        # Handle titles with a numbered/lettered prefix ending in a dot,
        # e.g., "4. Results Interpretation" -> adds "Results Interpretation"
        # The prefix part is like "1.", "A.1.", "IV.", etc.
        # Regex: ^ (?:non-capturing-prefix-ending-with-dot) \\s+ (capturing-title-part) $
        dot_prefix_match = re.match(r"^(?:[A-Za-z0-9]+(?:[\.\-][A-ZaZ0-9]+)*[\.\-\,;])\s+(.+)$", original_name)
        if dot_prefix_match:
            title_part = dot_prefix_match.group(1).strip()
            if title_part:
                search_patterns.add(title_part)

        matches = []

        for pattern_text in search_patterns:
            if not pattern_text:
                continue

            escaped_pattern = re.escape(pattern_text)
            # Regex explanation:
            # (?<![\w.])   : Negative lookbehind - asserts that the match is not preceded by a word character or a dot.
            # (?:\"|\')?  : Optional non-capturing group for a double or single quote.
            # escaped_pattern : The actual pattern text, with regex special characters escaped.
            # (?:\"|\')?  : Optional non-capturing group for a double or single quote.
            # (?![\w.])    : Negative lookahead - asserts that the match is not followed by a word character or a dot.
            regex_str = r"(?<![\w.])(?:\"|\')?" + escaped_pattern + r"(?:\"|\')?(?![\w.])"

            try:
                for match in re.finditer(regex_str, text):  # Use original text for spans
                    matches.append(match.span())
            except re.error:
                # Should not happen with proper escaping and non-empty patterns
                pass

        if not matches:
            return []

        # Deduplicate and sort matches by their start position
        unique_matches = sorted(list(set(matches)), key=lambda m: m[0])

        return unique_matches
