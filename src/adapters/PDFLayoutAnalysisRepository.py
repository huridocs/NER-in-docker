import requests
from pathlib import Path
from configuration import PDF_ANALYSIS_SERVICE_URL
from domain.Segment import Segment
from ports.PDFToSegmentsRepository import PDFToSegmentsRepository


class PDFLayoutAnalysisRepository(PDFToSegmentsRepository):
    @staticmethod
    def get_segments(pdf_path: Path, fast: bool = False) -> list[Segment]:
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            data = {"fast": fast}
            response = requests.post(PDF_ANALYSIS_SERVICE_URL, files=files, data=data)
            response.raise_for_status()
            segment_boxes = response.json()
            return [
                Segment.from_segment_box(segment_box, pdf_path.name, index + 1)
                for index, segment_box in enumerate(segment_boxes)
            ]
