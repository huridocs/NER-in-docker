from dateparser.search import search_dates
from dateparser_data.settings import default_parsers
from pydantic import BaseModel
from unidecode import unidecode
import dateparser
from domain.NamedEntityType import NamedEntityType
import country_converter as coco


class NamedEntity(BaseModel):
    type: NamedEntityType
    text: str
    normalized_text: str = ""
    character_start: int = 0
    character_end: int = 0

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

        parsers = [parser for parser in default_parsers if parser != "relative-time"]
        settings = {"STRICT_PARSING": True, "PARSERS": parsers}
        return dateparser.parse(text).strftime("%Y-%m-%d") if search_dates(self.text, settings=settings) else self.text

    def get_with_normalize_entity_text(self):
        normalization_functions = {
            NamedEntityType.PERSON: self.normalize_text,
            NamedEntityType.ORGANIZATION: self.normalize_text,
            NamedEntityType.LOCATION: self.normalize_location,
            NamedEntityType.DATE: self.normalize_date,
            NamedEntityType.LAW: self.normalize_text,
        }

        self.normalized_text = normalization_functions[self.type](self.text)
        return self
