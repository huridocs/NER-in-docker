from domain.NamedEntity import NamedEntity
from domain.PDFSegment import PDFSegment


class PDFNamedEntity(NamedEntity):
    pdf_segment: PDFSegment = None

    @staticmethod
    def from_pdf_segment(named_entity: NamedEntity, pdf_segment: PDFSegment) -> "PDFNamedEntity":
        pdf_named_entity: PDFNamedEntity = PDFNamedEntity(**named_entity.model_dump())
        pdf_named_entity.pdf_segment = pdf_segment
        return pdf_named_entity
