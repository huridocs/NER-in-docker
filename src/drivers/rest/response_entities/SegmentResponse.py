from pydantic import BaseModel

from domain.BoundingBox import BoundingBox
from domain.NamedEntityGroup import NamedEntityGroup
from domain.PDFNamedEntity import PDFNamedEntity


class SegmentResponse(BaseModel):
    text: str
    page_number: int
    segment_number: int
    character_start: int
    character_end: int
    bounding_box: BoundingBox
    pdf_name: str = ""

    @staticmethod
    def from_pdf_named_entity(pdf_named_entity: PDFNamedEntity) -> "SegmentResponse":
        return SegmentResponse(
            text=pdf_named_entity.pdf_segment.text,
            page_number=pdf_named_entity.pdf_segment.page_number,
            segment_number=pdf_named_entity.pdf_segment.segment_number,
            character_start=pdf_named_entity.character_start,
            character_end=pdf_named_entity.character_end,
            bounding_box=pdf_named_entity.pdf_segment.bounding_box,
            pdf_name=pdf_named_entity.pdf_segment.pdf_name if pdf_named_entity.pdf_segment else "",
        )

    @staticmethod
    def from_named_entity_group(named_entity_group: NamedEntityGroup) -> "SegmentResponse | None":
        if not named_entity_group.pdf_segment:
            return None

        if named_entity_group.name in named_entity_group.pdf_segment.text:
            character_start = named_entity_group.pdf_segment.text.index(named_entity_group.name)
            character_end = character_start + len(named_entity_group.name)
        else:
            character_start = 0
            character_end = 0

        return SegmentResponse(
            text=named_entity_group.pdf_segment.text,
            page_number=named_entity_group.pdf_segment.page_number,
            segment_number=named_entity_group.pdf_segment.segment_number,
            character_start=character_start,
            character_end=character_end,
            bounding_box=named_entity_group.pdf_segment.bounding_box,
            pdf_name=named_entity_group.pdf_segment.pdf_name,
        )
