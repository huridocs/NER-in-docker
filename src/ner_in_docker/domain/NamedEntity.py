from dateparser.search import search_dates
from dateparser_data.settings import default_parsers
from pdf_features.Rectangle import Rectangle
from pdf_features.PdfWord import PdfWord
from pdf_token_type_labels import TokenType
from pydantic import BaseModel
from unidecode import unidecode
import dateparser
import logging

from ner_in_docker.configuration import TITLES_TYPES, SEPARATOR
from ner_in_docker.domain.NamedEntityType import NamedEntityType
import country_converter as coco
from ner_in_docker.domain.Segment import Segment

logging.getLogger("country_converter").setLevel(logging.ERROR)


class NamedEntity(BaseModel):
    type: NamedEntityType
    text: str
    normalized_text: str = ""
    character_start: int = 0
    character_end: int = 0
    group_name: str = ""
    segment_type: TokenType = TokenType.TEXT
    appearance_count: int = 0
    percentage_to_segment_text: int = 0
    first_type_appearance: bool = False
    last_type_appearance: bool = False
    segment: Segment = None
    text_positions: list[Rectangle] = []
    relevance_percentage: int = 0

    @staticmethod
    def from_segment(named_entity: "NamedEntity", segment: Segment, group_name: str = "") -> "NamedEntity":
        named_entity.segment = segment
        if not named_entity.group_name:
            named_entity.group_name = group_name
        return named_entity

    @staticmethod
    def normalize_text(text: str) -> str:
        normalized_text = text.lower().strip()
        normalized_text = normalized_text.replace(",", " ")
        normalized_text = normalized_text.replace(".", " ")
        normalized_text = " ".join(sorted(normalized_text.split()))
        return unidecode(normalized_text)

    @staticmethod
    def normalize_reference(text: str) -> str:
        return text.split(SEPARATOR)[0].strip()

    def normalize_location(self, text):
        iso_3 = coco.convert(names=[text], to="ISO3")
        return iso_3 if iso_3 != "not found" else self.normalize_text(text)

    def normalize_date(self, text, language: str = "en"):
        if self.normalized_text:
            return self.normalized_text

        parsers = [parser for parser in default_parsers if parser != "relative-time"]
        settings = {"STRICT_PARSING": True, "PARSERS": parsers}
        return (
            dateparser.parse(text, languages=[language]).strftime("%Y-%m-%d")
            if search_dates(self.text, languages=[language], settings=settings)
            else self.text
        )

    def get_with_normalize_entity_text(self, language: str = "en"):
        if self.type == NamedEntityType.REFERENCE:
            return self

        normalization_functions = {
            NamedEntityType.PERSON: self.normalize_text,
            NamedEntityType.ORGANIZATION: self.normalize_text,
            NamedEntityType.LOCATION: self.normalize_location,
            NamedEntityType.DATE: lambda x: self.normalize_date(x, language),
            NamedEntityType.LAW: self.normalize_text,
            NamedEntityType.DOCUMENT_CODE: lambda x: x.strip(),
        }

        self.normalized_text = normalization_functions[self.type](self.text)
        return self

    def set_relevance_score(self, named_entities: list["NamedEntity"]):
        self.set_score_parameters(named_entities)

        if self.type == NamedEntityType.REFERENCE:
            self.relevance_percentage = 100 if str(self.segment_type).lower() in TITLES_TYPES else 0
            return self

        self.relevance_percentage += int(10 * self.percentage_to_segment_text / 100)
        if self.first_type_appearance:
            self.relevance_percentage += 15
        if self.last_type_appearance:
            self.relevance_percentage += 15
        if str(self.segment_type).lower() in TITLES_TYPES:
            self.relevance_percentage += 60
        if str(self.segment_type).lower() == "page header":
            self.relevance_percentage += 30
        if str(self.segment_type).lower() in "text":
            self.relevance_percentage += 15

        return self

    def set_score_parameters(self, named_entities):
        # Set appearance_count
        self.appearance_count = sum(1 for ne in named_entities if ne.type == self.type and ne.text == self.text)
        # Set percentage_to_segment_text
        if self.segment and hasattr(self.segment, "text") and self.segment.text:
            self.percentage_to_segment_text = int(100 * len(self.text) / len(self.segment.text))
        else:
            self.percentage_to_segment_text = 0
        # Set first_type_appearance and last_type_appearance
        same_type_entities = [ne for ne in named_entities if ne.type == self.type]
        if same_type_entities:
            self.first_type_appearance = same_type_entities[0].text == self.text
            self.last_type_appearance = same_type_entities[-1].text == self.text
        else:
            self.first_type_appearance = False
            self.last_type_appearance = False

    def add_positions_from_pdf_words(self, pdf_words: list[PdfWord]) -> "NamedEntity":
        if not self.segment or not self.segment.bounding_box:
            return self

        bounding_boxes = []
        for position in pdf_words:
            bounding_boxes.append(position.bounding_box)

        self.text_positions = bounding_boxes
        return self

    def has_iso_code(self):
        if self.type != NamedEntityType.LOCATION:
            return True

        iso_3 = coco.convert(names=[self.text], to="ISO3")
        return iso_3 != "not found"
