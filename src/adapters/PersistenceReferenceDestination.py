from dataclasses import dataclass

from domain.BoundingBox import BoundingBox
from domain.PDFSegment import PDFSegment


@dataclass
class PersistenceReferenceDestination:
    id: int
    title: str
    page_number: int
    segment_number: int
    pdf_name: str
    left: int
    top: int
    width: int
    height: int

    @staticmethod
    def from_row(row):
        return PersistenceReferenceDestination(
            id=row[0],
            title=row[1],
            page_number=row[2],
            segment_number=row[3],
            pdf_name=row[4],
            left=row[5],
            top=row[6],
            width=row[7],
            height=row[8],
        )

    def get_pdf_segment(self) -> PDFSegment:
        bounding_box = BoundingBox(left=self.left, top=self.top, width=self.width, height=self.height)
        return PDFSegment(
            text=self.title,
            page_number=self.page_number,
            bounding_box=bounding_box,
            pdf_name=self.pdf_name,
            segment_number=self.segment_number,
        )
