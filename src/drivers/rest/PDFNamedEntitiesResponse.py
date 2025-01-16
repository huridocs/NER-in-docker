from pydantic import BaseModel


class PDFNamedEntitiesResponse(BaseModel):
    entities: list[NamedEntityResponse]
    groups: dict[str, GroupResponse]
