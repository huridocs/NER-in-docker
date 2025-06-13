from pydantic import BaseModel
from domain.BoundingBox import BoundingBox


class PDFSegment(BaseModel):
    text: str
    page_number: int
    segment_number: int
    type: str = "Text"
    pdf_name: str
    bounding_box: BoundingBox

    @staticmethod
    def from_segment_box(segment_box_dict: dict, pdf_name: str, segment_number: int):
        return PDFSegment(
            text=segment_box_dict["text"],
            page_number=segment_box_dict["page_number"],
            type=segment_box_dict.get("type", "Text"),
            segment_number=segment_number,
            pdf_name=pdf_name,
            bounding_box=BoundingBox(
                left=int(segment_box_dict["left"]),
                top=int(segment_box_dict["top"]),
                width=int(segment_box_dict["width"]),
                height=int(segment_box_dict["height"]),
            ),
        )

    @staticmethod
    def from_text(text: str):
        return PDFSegment(
            text=text,
            page_number=0,
            segment_number=0,
            type="Text",
            pdf_name="pdf_name",
            bounding_box=BoundingBox(left=0, top=0, width=0, height=0),
        )
