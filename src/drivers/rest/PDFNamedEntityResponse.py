from drivers.rest.NamedEntityResponse import NamedEntityResponse
from drivers.rest.SegmentResponse import SegmentResponse


class PDFNamedEntityResponse(NamedEntityResponse):
    page_number: int
    segment: SegmentResponse
