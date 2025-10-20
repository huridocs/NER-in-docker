from pathlib import Path

from pdf_features.PdfTextPosition import PdfTextPosition

from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.ports.PDFToSegmentsRepository import PDFToSegmentsRepository


class GetPositionsUseCase:
    def __init__(self, pdf_to_segments_repository: PDFToSegmentsRepository, pdf_path: Path):
        self.pdf_to_segments_repository = pdf_to_segments_repository
        self.pdf_words = self.pdf_to_segments_repository.get_word_positions(pdf_path)
        self.pdf_text_position = PdfTextPosition(self.pdf_words)

    def add_positions(self, named_entities: list[NamedEntity]) -> list:
        for entity in named_entities:
            if not entity.segment:
                continue

            words = self.pdf_text_position.get_bounding_boxes(
                entity.text, entity.segment.bounding_box, entity.segment.page_number
            )
            entity.add_positions_from_pdf_words(words)

        return named_entities
