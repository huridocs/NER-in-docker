from abc import ABC, abstractmethod
from pathlib import Path
from domain.PDFSegment import PDFSegment


class PDFToSegmentsRepository(ABC):

    @staticmethod
    @abstractmethod
    def get_segments(pdf_path: Path) -> list[PDFSegment]:
        pass
