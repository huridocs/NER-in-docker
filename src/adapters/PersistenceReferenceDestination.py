from dataclasses import dataclass

from domain.BoundingBox import BoundingBox
from domain.Segment import Segment


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

    def get_segment(self) -> Segment:
        bounding_box = BoundingBox(left=self.left, top=self.top, width=self.width, height=self.height)
        return Segment(
            text=self.title,
            page_number=self.page_number,
            bounding_box=bounding_box,
            source_id=self.pdf_name,
            segment_number=self.segment_number,
        )
