from pydantic import BaseModel
from unidecode import unidecode
import dateparser
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

    def normalize_location(self, text):
        iso_3 = coco.convert(names=[text], to="ISO3")
        return iso_3 if iso_3 != "not found" else self.normalize_text(text)

    def normalize_date(self, text):
        if self.normalized_text:
            return self.normalized_text
        return dateparser.parse(text).strftime("%Y-%m-%d")

    def normalize_entity_text(self):
        normalization_functions = {
            NamedEntityType.PERSON: self.normalize_text,
            NamedEntityType.ORGANIZATION: self.normalize_text,
            NamedEntityType.LOCATION: self.normalize_location,
            NamedEntityType.DATE: self.normalize_date,
            NamedEntityType.LAW: self.normalize_text,
        }

        self.normalized_text = normalization_functions[self.type](self.text)
        return self
