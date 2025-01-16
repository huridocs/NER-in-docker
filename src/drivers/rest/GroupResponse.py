from pydantic import BaseModel


class GroupResponse(BaseModel):
    group_name: str
    entities_ids: list[int]
    entities_text: list[str]
