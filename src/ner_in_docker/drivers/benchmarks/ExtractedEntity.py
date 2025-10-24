from pydantic import BaseModel, Field


class ExtractedEntity(BaseModel):
    text: str = Field(..., description="The text of the entity")
    type: str = Field(..., description="The entity type (e.g., PERSON, LOCATION, ORGANIZATION)")
    character_start: int = Field(..., description="Starting character position in the text")
    character_end: int = Field(..., description="Ending character position in the text")

    class Config:
        frozen = True
