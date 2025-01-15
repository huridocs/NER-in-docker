from pydantic import BaseModel


class BoundingBox(BaseModel):
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0
