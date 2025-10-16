from abc import ABC, abstractmethod
from pathlib import Path

from ner_in_docker.domain.PdfWord import PdfWord
from ner_in_docker.domain.Segment import Segment


class PDFToSegmentsRepository(ABC):

    @staticmethod
    @abstractmethod
    def get_segments(pdf_path: Path, fast: bool) -> list[Segment]:
        pass

    @staticmethod
    @abstractmethod
    def get_word_positions(pdf_path: Path) -> list[PdfWord]:
        pass
