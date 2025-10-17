from pdf_features import Rectangle
from pydantic import BaseModel


class BoundingBoxResponse(BaseModel):
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0

    @staticmethod
    def from_rectangle(rectangle: Rectangle):
        return BoundingBoxResponse(
            left=int(rectangle.left),
            top=int(rectangle.top),
            width=int(rectangle.width),
            height=int(rectangle.height),
        )
