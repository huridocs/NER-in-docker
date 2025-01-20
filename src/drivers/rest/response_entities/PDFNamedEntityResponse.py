from pydantic import BaseModel

from domain.NamedEntityType import NamedEntityType
from domain.PDFNamedEntity import PDFNamedEntity
from drivers.rest.response_entities.SegmentResponse import SegmentResponse


class PDFNamedEntityResponse(BaseModel):
    group_name: str
    type: NamedEntityType
    text: str
    page_number: int
    segment: SegmentResponse

    @staticmethod
    def from_pdf_named_entity(pdf_named_entity: PDFNamedEntity, group_name: str):
        return PDFNamedEntityResponse(
            group_name=group_name,
            type=pdf_named_entity.type,
            text=pdf_named_entity.text,
            page_number=pdf_named_entity.segment.page_number,
            segment=SegmentResponse.from_pdf_named_entity(pdf_named_entity),
        )
