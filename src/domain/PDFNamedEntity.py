from domain.NamedEntity import NamedEntity
from domain.PDFSegment import PDFSegment


class PDFNamedEntity(NamedEntity):
    segment: PDFSegment = None

    @staticmethod
    def from_pdf_segment(pdf_segment: PDFSegment, named_entity: NamedEntity) -> "PDFNamedEntity":
        pdf_named_entity: PDFNamedEntity = PDFNamedEntity(**named_entity.model_dump())
        pdf_named_entity.segment = pdf_segment
        return pdf_named_entity
