from pydantic import BaseModel
from unidecode import unidecode

from domain.NamedEntityType import NamedEntityType
import country_converter as coco


class NamedEntity(BaseModel):
    type: NamedEntityType
    text: str
    normalized_text: str = ""
    start: int = 0
    end: int = 0
    context: str = "default"

    @staticmethod
    def normalize_text(text: str) -> str:
        normalized_text = text.lower().strip()
        normalized_text = normalized_text.replace(",", " ")
        normalized_text = normalized_text.replace(".", " ")
        normalized_text = " ".join(sorted(normalized_text.split()))
        return unidecode(normalized_text)

    def normalize_entity_text(self):
        if self.type == NamedEntityType.PERSON:
            self.normalized_text = self.normalize_text(self.text)

        if self.type == NamedEntityType.LOCATION:
            iso_3 = coco.convert(names=[self.text], to="ISO3")
            self.normalized_text = iso_3 if iso_3 != "not found" else self.normalize_text(self.text)

        return self
