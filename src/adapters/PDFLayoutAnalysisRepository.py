import requests
from pathlib import Path
from configuration import PDF_ANALYSIS_SERVICE_URL
from domain.PDFSegment import PDFSegment
from ports.PDFToSegmentsRepository import PDFToSegmentsRepository


class PDFLayoutAnalysisRepository(PDFToSegmentsRepository):
    @staticmethod
    def get_segments(pdf_path: Path) -> list[PDFSegment]:
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            response = requests.post(f"{PDF_ANALYSIS_SERVICE_URL}", files=files)
            response.raise_for_status()
            segment_boxes = response.json()
            return [
                PDFSegment.from_segment_box(segment_box, pdf_path.name, index + 1)
                for index, segment_box in enumerate(segment_boxes)
            ]
