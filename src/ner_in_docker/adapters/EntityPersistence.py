from pdf_features import Rectangle
from pydantic import BaseModel
from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.NamedEntityType import NamedEntityType
from typing import Optional
from ner_in_docker.domain.Segment import Segment


class EntityPersistence(BaseModel):
    group_name: str = ""
    type: NamedEntityType
    text: str
    normalized_text: str = ""
    character_start: int = 0
    character_end: int = 0
    relevance_percentage: int = 0
    segment_text: Optional[str] = None
    segment_page_number: Optional[int] = None
    segment_segment_number: Optional[int] = None
    segment_type: str = "Text"
    segment_source_id: Optional[str] = None
    segment_bounding_box_left: Optional[int] = None
    segment_bounding_box_top: Optional[int] = None
    segment_bounding_box_width: Optional[int] = None
    segment_bounding_box_height: Optional[int] = None
    appearance_count: int = 0
    percentage_to_segment_text: int = 0
    first_type_appearance: bool = False
    last_type_appearance: bool = False

    def to_named_entity(self) -> NamedEntity:
        segment = Segment(
            text=self.segment_text if self.segment_text else "",
            page_number=self.segment_page_number if self.segment_segment_number else 0,
            segment_number=self.segment_segment_number if self.segment_segment_number else 0,
            type=self.segment_type,
            source_id=self.segment_source_id if self.segment_source_id else "",
            bounding_box=Rectangle.from_width_height(
                left=self.segment_bounding_box_left if self.segment_bounding_box_left else 0,
                top=self.segment_bounding_box_top if self.segment_bounding_box_top else 0,
                width=self.segment_bounding_box_width if self.segment_bounding_box_width else 0,
                height=self.segment_bounding_box_height if self.segment_bounding_box_height else 0,
            ),
        )

        return NamedEntity(
            type=NamedEntityType(self.type),
            text=self.text,
            normalized_text=self.normalized_text,
            character_start=self.character_start,
            character_end=self.character_end,
            group_name=self.group_name,
            segment=segment,
            appearance_count=self.appearance_count,
            percentage_to_segment_text=self.percentage_to_segment_text,
            first_type_appearance=self.first_type_appearance,
            last_type_appearance=self.last_type_appearance,
            relevance_percentage=self.relevance_percentage,
        )

    @staticmethod
    def from_row(row):
        return EntityPersistence(
            type=NamedEntityType(row[1]),
            text=row[2],
            normalized_text=row[3],
            character_start=row[4],
            character_end=row[5],
            group_name=row[6],
            segment_text=row[7],
            segment_page_number=row[8],
            segment_segment_number=row[9],
            segment_type=row[10],
            segment_source_id=row[11],
            segment_bounding_box_left=row[12],
            segment_bounding_box_top=row[13],
            segment_bounding_box_width=row[14],
            segment_bounding_box_height=row[15],
            appearance_count=row[16],
            percentage_to_segment_text=row[17],
            first_type_appearance=bool(row[18]),
            last_type_appearance=bool(row[19]),
            relevance_percentage=row[20],
        )

    @staticmethod
    def from_named_entity(named_entity: NamedEntity) -> "EntityPersistence":
        segment = named_entity.segment
        return EntityPersistence(
            type=named_entity.type,
            text=named_entity.text,
            normalized_text=named_entity.normalized_text,
            character_start=named_entity.character_start,
            character_end=named_entity.character_end,
            group_name=named_entity.group_name,
            segment_text=segment.text if segment else None,
            segment_page_number=segment.page_number if segment else None,
            segment_segment_number=segment.segment_number if segment else None,
            segment_type=segment.type if segment else "Text",
            segment_source_id=segment.source_id if segment else None,
            segment_bounding_box_left=segment.bounding_box.left if segment and segment.bounding_box else None,
            segment_bounding_box_top=segment.bounding_box.top if segment and segment.bounding_box else None,
            segment_bounding_box_width=segment.bounding_box.width if segment and segment.bounding_box else None,
            segment_bounding_box_height=segment.bounding_box.height if segment and segment.bounding_box else None,
            appearance_count=named_entity.appearance_count,
            percentage_to_segment_text=named_entity.percentage_to_segment_text,
            first_type_appearance=named_entity.first_type_appearance,
            last_type_appearance=named_entity.last_type_appearance,
            relevance_percentage=named_entity.relevance_percentage,
        )
