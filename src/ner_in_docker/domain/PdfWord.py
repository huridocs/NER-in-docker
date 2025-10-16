from pydantic import BaseModel

from ner_in_docker.domain.BoundingBox import BoundingBox


class PdfWord(BaseModel):
    text: str
    bounding_box: BoundingBox
    page_number: int
