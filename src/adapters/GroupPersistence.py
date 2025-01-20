from pydantic import BaseModel


class GroupPersistence(BaseModel):
    name: str
    type: str
    entities_names: list[str]
