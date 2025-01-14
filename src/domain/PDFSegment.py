from pydantic import BaseModel
from domain.BoundingBox import BoundingBox


class PDFSegment(BaseModel):
    text: str
    page_number: int
    segment_number: int
    pdf_name: str
    bounding_box: BoundingBox
