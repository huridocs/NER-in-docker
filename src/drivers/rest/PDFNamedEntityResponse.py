from domain.PDFNamedEntity import PDFNamedEntity
from drivers.rest.NamedEntityResponse import NamedEntityResponse
from drivers.rest.SegmentResponse import SegmentResponse


class PDFNamedEntityResponse(NamedEntityResponse):
    page_number: int
    segment: SegmentResponse

    @staticmethod
    def from_pdf_named_entity(pdf_named_entity: PDFNamedEntity, group_name: str):
        return PDFNamedEntityResponse(
            group_name=group_name,
            type=pdf_named_entity.type,
            text=pdf_named_entity.text,
            character_start=pdf_named_entity.character_start,
            character_end=pdf_named_entity.character_end,
            page_number=pdf_named_entity.segment.page_number,
            segment=SegmentResponse.from_pdf_named_entity(pdf_named_entity),
        )
