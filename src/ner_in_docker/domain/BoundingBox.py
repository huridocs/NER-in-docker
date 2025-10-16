from pydantic import BaseModel


class BoundingBox(BaseModel):
    left: int = 0
    top: int = 0
    width: int = 0
    height: int = 0

    @staticmethod
    def from_coordinates(left: int = 0, top: int = 0, width: int = 0, height: int = 0) -> "BoundingBox":
        return BoundingBox(left=left, top=top, width=width, height=height)

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    def area(self):
        return self.width * self.height

    def get_intersection_percentage(self, rectangle: "BoundingBox") -> float:
        x1 = max(self.left, rectangle.left)
        y1 = max(self.top, rectangle.top)
        x2 = min(self.right, rectangle.right)
        y2 = min(self.bottom, rectangle.bottom)

        if x2 <= x1 or y2 <= y1:
            return 0

        return 100 * (x2 - x1) * (y2 - y1) / self.area()

    @staticmethod
    def merge_rectangles(rectangles: list["BoundingBox"]) -> "BoundingBox":
        left = min([rectangle.left for rectangle in rectangles])
        top = min([rectangle.top for rectangle in rectangles])
        right = max([rectangle.right for rectangle in rectangles])
        bottom = max([rectangle.bottom for rectangle in rectangles])

        return BoundingBox.from_coordinates(left, top, right - left, bottom - top)
