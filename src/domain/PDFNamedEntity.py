from domain.BoundingBox import BoundingBox
from domain.NamedEntity import NamedEntity
from domain.PDFSegment import PDFSegment


class PDFNamedEntity(NamedEntity):
    segment_text: str = ""
    page_number: int = 1
    segment_number: int = 1
    pdf_name: str = ""
    bounding_box: BoundingBox = None

    @staticmethod
    def from_pdf_segment(pdf_segment: PDFSegment, named_entity: NamedEntity) -> "PDFNamedEntity":
        pdf_named_entity: PDFNamedEntity = PDFNamedEntity(**named_entity.model_dump())
        pdf_named_entity.segment_text = pdf_segment.text
        pdf_named_entity.page_number = pdf_segment.page_number
        pdf_named_entity.segment_number = pdf_segment.segment_number
        pdf_named_entity.pdf_name = pdf_segment.pdf_name
        pdf_named_entity.bounding_box = pdf_segment.bounding_box
        return pdf_named_entity
