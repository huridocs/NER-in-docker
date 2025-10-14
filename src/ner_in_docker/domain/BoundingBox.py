from pydantic import BaseModel


class BoundingBox(BaseModel):
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0

    @staticmethod
    def from_coordinates(left: int = 0, top: int = 0, width: int = 0, height: int = 0) -> "BoundingBox":
        return BoundingBox(left=left, top=top, width=width, height=height)
