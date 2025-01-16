from pydantic import BaseModel

from domain.NamedEntityType import NamedEntityType
from drivers.rest.SegmentResponse import SegmentResponse


class NamedEntityResponse(BaseModel):
    type: NamedEntityType
    text: str
    character_start: int = 0
    character_end: int = 0
    segment: SegmentResponse = None
    page_number: int = 1
