from pydantic import BaseModel

from domain.NamedEntityType import NamedEntityType
from drivers.rest.SegmentResponse import SegmentResponse


class NamedEntityResponse(BaseModel):
    group_name: str
    type: NamedEntityType
    text: str
