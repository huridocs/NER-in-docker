from pathlib import Path
from domain.PDFSegment import PDFSegment
from ports.PDFToSegmentsRepository import PDFToSegmentsRepository


class PDFLayoutAnalysisRepository(PDFToSegmentsRepository):
    @staticmethod
    def get_segments(pdf_path: Path) -> list[PDFSegment]:
        pass
