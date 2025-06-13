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
    bounding_box_x1: int
    bounding_box_y1: int
    bounding_box_x2: int
    bounding_box_y2: int

    @staticmethod
    def from_row(row):
        return PersistenceReferenceDestination(
            id=row[0],
            title=row[1],
            page_number=row[2],
            segment_number=row[3],
            pdf_name=row[4],
            bounding_box_x1=row[5],
            bounding_box_y1=row[6],
            bounding_box_x2=row[7],
            bounding_box_y2=row[8],
        )

    def get_pdf_segment(self) -> PDFSegment:
        return PDFSegment(
            text=self.title,
            page_number=self.page_number,
            segment_number=self.segment_number,
            pdf_name=self.pdf_name,
            bounding_box = BoundingBox(
                left=self.bounding_box_x1,
                top=self.bounding_box_y1,
                width=self.bounding_box_x2 - self.bounding_box_x1,
                height=self.bounding_box_y2 - self.bounding_box_y1
            ))
