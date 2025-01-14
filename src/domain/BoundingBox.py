from pydantic import BaseModel


class BoundingBox(BaseModel):
    left: int = 0
    top: int = 0
    right: int = 0
    bottom: int = 0
