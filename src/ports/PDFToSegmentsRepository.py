from abc import ABC, abstractmethod
from pathlib import Path
from domain.Segment import Segment


class PDFToSegmentsRepository(ABC):

    @staticmethod
    @abstractmethod
    def get_segments(pdf_path: Path, fast: bool) -> list[Segment]:
        pass
