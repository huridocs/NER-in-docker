from pydantic import BaseModel
from drivers.rest.GroupResponse import GroupResponse
from drivers.rest.PDFNamedEntityResponse import PDFNamedEntityResponse


class PDFNamedEntitiesResponse(BaseModel):
    entities: list[PDFNamedEntityResponse]
    groups: list[GroupResponse]
