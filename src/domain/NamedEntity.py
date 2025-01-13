from pydantic import BaseModel
from unidecode import unidecode

from domain.NamedEntityType import NamedEntityType


class NamedEntity(BaseModel):
    type: NamedEntityType
    text: str
    normalized_text: str = ""
    start: int = 0
    end: int = 0
    context: str = "default"

    def normalize_text(self):
        if self.type == NamedEntityType.PERSON:
            normalized_text = self.text.lower().strip()
            normalized_text = normalized_text.replace(",", " ")
            normalized_text = normalized_text.replace(".", " ")
            normalized_text = " ".join(sorted(normalized_text.split()))
            self.normalized_text = unidecode(normalized_text)
        return self
