from pydantic import BaseModel

from drivers.rest import NamedEntityResponse
from drivers.rest.GroupResponse import GroupResponse
from drivers.rest.PDFNamedEntityResponse import PDFNamedEntityResponse


class NamedEntitiesResponse(BaseModel):
    entities: list[PDFNamedEntityResponse | NamedEntityResponse]
    groups: list[GroupResponse]
