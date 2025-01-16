from pydantic import BaseModel

from domain.BoundingBox import BoundingBox


class SegmentResponse(BaseModel):
    text: str
    page_number: int
    segment_number: int
    character_start: int
    character_end: int
    bounding_box: BoundingBox
