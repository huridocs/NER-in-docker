from pydantic import BaseModel

from domain.BoundingBox import BoundingBox


class SegmentResponse(BaseModel):
    segment_text: str = ""
    segment_number: int = 1
    bounding_box: BoundingBox = None
