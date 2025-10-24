from typing import List
from ner_in_docker.drivers.benchmarks.EntityExtractor import EntityExtractor
from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity


class GlinerExtractor(EntityExtractor):

    def __init__(self, model_path: str = "models/gliner/pytorch_model.bin"):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from gliner import GLiNER

            self.model = GLiNER.from_pretrained(self.model_path)
        except Exception as e:
            print(f"Error loading GLiNER model: {e}")
            self.model = None

    def get_name(self) -> str:
        return f"GLiNER ({self.model_path})"

    def extract(self, text: str) -> List[ExtractedEntity]:
        if self.model is None:
            return []

        try:
            entity_types = ["PERSON", "LOCATION", "ORGANIZATION"]

            entities_raw = self.model.predict_entities(text, entity_types)

            entities = []
            for entity in entities_raw:
                entities.append(
                    ExtractedEntity(
                        text=entity.get("text", ""),
                        type=entity.get("label", "").upper(),
                        character_start=entity.get("start", -1),
                        character_end=entity.get("end", -1),
                    )
                )

            return entities

        except Exception as e:
            print(f"Error extracting entities with GLiNER: {e}")
            return []
