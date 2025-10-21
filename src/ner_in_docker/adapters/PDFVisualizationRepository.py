from pathlib import Path
from os import makedirs
from os.path import join
import tempfile
from pdf_annotate import PdfAnnotator, Location, Appearance

from ner_in_docker.domain.NamedEntity import NamedEntity
from ner_in_docker.domain.NamedEntityType import NamedEntityType
from ner_in_docker.ports.VisualizationRepository import VisualizationRepository


ENTITY_COLOR_BY_TYPE = {
    NamedEntityType.PERSON: "#3498DB",
    NamedEntityType.ORGANIZATION: "#E74C3C",
    NamedEntityType.LOCATION: "#2ECC71",
    NamedEntityType.DATE: "#F39C12",
    NamedEntityType.LAW: "#9B59B6",
    NamedEntityType.DOCUMENT_CODE: "#1ABC9C",
    NamedEntityType.REFERENCE: "#E67E22",
}


class PDFVisualizationRepository(VisualizationRepository):
    def create_pdf_with_annotations(self, pdf_path: Path, named_entities: list[NamedEntity]) -> Path:
        output_path = Path(tempfile.gettempdir()) / f"annotated_{pdf_path.name}"
        
        annotator = PdfAnnotator(str(pdf_path))
        
        entities_by_page = self._group_entities_by_page(named_entities)
        
        for page_number, page_entities in entities_by_page.items():
            for entity_index, entity in enumerate(page_entities):
                if not entity.text_positions or not entity.segment:
                    continue
                    
                page_height = entity.segment.page_height
                
                for position in entity.text_positions:
                    self._add_entity_annotation(
                        annotator, 
                        entity, 
                        position, 
                        page_number, 
                        page_height,
                        entity_index
                    )
        
        annotator.write(str(output_path))
        return output_path
    
    def _group_entities_by_page(self, named_entities: list[NamedEntity]) -> dict[int, list[NamedEntity]]:
        entities_by_page = {}
        for entity in named_entities:
            if not entity.segment:
                continue
            page = entity.segment.page_number
            if page not in entities_by_page:
                entities_by_page[page] = []
            entities_by_page[page].append(entity)
        return entities_by_page
    
    def _hex_color_to_rgb(self, color: str) -> tuple:
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        alpha = 0.3
        return r / 255, g / 255, b / 255, alpha
    
    def _add_entity_annotation(
        self, 
        annotator: PdfAnnotator, 
        entity: NamedEntity, 
        position: dict,
        page_number: int,
        page_height: int,
        entity_index: int
    ) -> None:
        color = ENTITY_COLOR_BY_TYPE.get(entity.type, "#95A5A6")
        
        left = position["left"]
        top = page_height - position["top"]
        right = position["left"] + position["width"]
        bottom = page_height - (position["top"] + position["height"])
        
        annotator.add_annotation(
            "square",
            Location(x1=left, y1=bottom, x2=right, y2=top, page=page_number - 1),
            Appearance(
                stroke_color=self._hex_color_to_rgb(color),
                fill=self._hex_color_to_rgb(color)
            ),
        )
        
        text_box_width = min(len(entity.type) * 6 + 8, right - left)
        text_box_height = 10
        
        annotator.add_annotation(
            "square",
            Location(x1=left, y1=top, x2=left + text_box_width, y2=top + text_box_height, page=page_number - 1),
            Appearance(fill=self._hex_color_to_rgb(color)),
        )
        
        content = entity.type[:15]
        annotator.add_annotation(
            "text",
            Location(x1=left, y1=top, x2=left + text_box_width, y2=top + text_box_height, page=page_number - 1),
            Appearance(content=content, font_size=7, fill=(1, 1, 1), stroke_width=2),
        )

