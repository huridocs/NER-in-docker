from pdf_features import Rectangle
from pydantic import BaseModel


class Segment(BaseModel):
    text: str
    page_number: int
    segment_number: int
    type: str = "Text"
    source_id: str = ""
    bounding_box: Rectangle

    @staticmethod
    def from_segment_box(segment_box_dict: dict, source_id: str, segment_number: int):
        return Segment(
            text=segment_box_dict["text"],
            page_number=segment_box_dict["page_number"],
            type=segment_box_dict.get("type", "Text"),
            segment_number=segment_number,
            source_id=source_id,
            bounding_box=Rectangle.from_width_height(
                left=int(segment_box_dict["left"]),
                top=int(segment_box_dict["top"]),
                width=int(segment_box_dict["width"]),
                height=int(segment_box_dict["height"]),
            ),
        )

    @staticmethod
    def from_text(text: str, source_id: str = None):
        return Segment(
            text=text,
            page_number=0,
            segment_number=0,
            type="Text",
            source_id=source_id if source_id else "default",
            bounding_box=Rectangle.from_width_height(left=0, top=0, width=0, height=0),
        )
