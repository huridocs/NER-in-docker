import requests
from pathlib import Path

from pdf_features.PdfWord import PdfWord

from ner_in_docker.configuration import PDF_ANALYSIS_SERVICE_URL
from ner_in_docker.domain.Segment import Segment
from ner_in_docker.ports.PDFToSegmentsRepository import PDFToSegmentsRepository


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

    @staticmethod
    def get_word_positions(pdf_path: Path) -> list[PdfWord]:
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": pdf_file}
            response = requests.post(PDF_ANALYSIS_SERVICE_URL + "/word_positions", files=files)
            response.raise_for_status()
            pdf_words = response.json()
            return [PdfWord(**segment_box) for segment_box in pdf_words]
