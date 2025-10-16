from pathlib import Path

from ner_in_docker.domain.BoundingBox import BoundingBox
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.PdfWord import PdfWord
from ner_in_docker.ports.PDFToSegmentsRepository import PDFToSegmentsRepository


class GetPositionsUseCase:
    def __init__(self, pdf_to_segments_repository: PDFToSegmentsRepository, pdf_path: Path):
        self.pdf_to_segments_repository = pdf_to_segments_repository
        self.pdf_words = self.pdf_to_segments_repository.get_word_positions(pdf_path)

    def add_positions(self, named_entities: list[NamedEntity]) -> list:
        for entity in named_entities:
            if not entity.segment:
                continue
            words = self.get_bounding_boxes(entity.text, entity.segment.bounding_box, entity.segment.page_number)
            entity.add_positions_from_pdf_words(words)

        return named_entities

    def get_bounding_boxes(self, text: str, search_bounding_box: BoundingBox, page_number: int) -> list[PdfWord]:
        filtered_words = [
            word
            for word in self.pdf_words
            if word.page_number == page_number and search_bounding_box.get_intersection_percentage(word.bounding_box) > 0
        ]

        if not filtered_words:
            return []

        search_text = text.strip()
        search_words = search_text.split()

        if not search_words:
            return []

        matches = []

        for start_idx in range(len(filtered_words)):
            match_result = self._find_match_from_position(filtered_words, start_idx, search_words)

            if match_result:
                matched_words, score = match_result
                matches.append((matched_words, score, start_idx))

        if not matches:
            return []

        sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)

        unique_matches = []
        used_indices = set()

        for matched_words, score, start_idx in sorted_matches:
            word_indices = set(range(start_idx, start_idx + len(matched_words)))

            if not word_indices.intersection(used_indices):
                unique_matches.append(matched_words)
                used_indices.update(word_indices)

        result = []
        for matched_words in unique_matches:
            merged_word = self._merge_adjacent_words(matched_words)
            result.append(merged_word)

        return result

    def _find_match_from_position(
        self, words: list[PdfWord], start_idx: int, search_words: list[str]
    ) -> tuple[list[PdfWord], float] | None:
        if start_idx >= len(words):
            return None

        best_match = None
        best_score = 0

        max_search_length = min(len(search_words) * 3, len(words) - start_idx)

        for end_idx in range(start_idx + 1, start_idx + max_search_length + 1):
            candidate_words = words[start_idx:end_idx]
            candidate_text = " ".join(word.text for word in candidate_words)

            score = self._calculate_match_score(candidate_text, search_words)

            if score > best_score:
                best_score = score
                best_match = candidate_words

        if best_score > 0.6:
            return (best_match, best_score)

        return None

    def _calculate_match_score(self, candidate_text: str, search_words: list[str]) -> float:
        search_text = " ".join(search_words)

        if candidate_text == search_text:
            return 1.0

        if search_text in candidate_text:
            length_penalty = len(search_text) / max(len(candidate_text), 1)
            return 0.95 * length_penalty

        candidate_words = candidate_text.split()

        if len(candidate_words) == 0:
            return 0.0

        matched_words = 0
        search_idx = 0

        for candidate_word in candidate_words:
            if search_idx >= len(search_words):
                break

            if candidate_word == search_words[search_idx]:
                matched_words += 1
                search_idx += 1

        word_match_ratio = matched_words / len(search_words)

        length_ratio = min(len(candidate_words), len(search_words)) / max(len(candidate_words), len(search_words))

        score = word_match_ratio * 0.7 + length_ratio * 0.3

        return score

    def _merge_adjacent_words(self, words: list[PdfWord]) -> PdfWord:
        if not words:
            raise ValueError("Cannot merge empty list of words")

        if len(words) == 1:
            return words[0]

        merged_text = " ".join(word.text for word in words)
        merged_bbox = BoundingBox.merge_rectangles([word.bounding_box for word in words])

        return PdfWord(text=merged_text, bounding_box=merged_bbox, page_number=words[0].page_number)
