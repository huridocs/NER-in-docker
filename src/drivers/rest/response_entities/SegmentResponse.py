from pydantic import BaseModel

from domain.BoundingBox import BoundingBox
from domain.PDFNamedEntity import PDFNamedEntity


class SegmentResponse(BaseModel):
    text: str
    page_number: int
    segment_number: int
    character_start: int
    character_end: int
    bounding_box: BoundingBox

    @staticmethod
    def from_pdf_named_entity(pdf_named_entity: PDFNamedEntity) -> "SegmentResponse":
        return SegmentResponse(
            text=pdf_named_entity.pdf_segment.text,
            page_number=pdf_named_entity.pdf_segment.page_number,
            segment_number=pdf_named_entity.pdf_segment.segment_number,
            character_start=pdf_named_entity.character_start,
            character_end=pdf_named_entity.character_end,
            bounding_box=pdf_named_entity.pdf_segment.bounding_box,
        )
