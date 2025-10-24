from typing import List
from ner_in_docker.drivers.benchmarks.EntityExtractor import EntityExtractor
from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity


class FlairExtractor(EntityExtractor):

    def __init__(self, model_path: str = "models/flair/pytorch_model.bin"):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from flair.models import SequenceTagger
            from flair.data import Sentence

            self.model = SequenceTagger.load(self.model_path)
            self.Sentence = Sentence
        except Exception as e:
            print(f"Error loading Flair model: {e}")
            self.model = None

    def get_name(self) -> str:
        return f"Flair ({self.model_path})"

    def extract(self, text: str) -> List[ExtractedEntity]:
        if self.model is None:
            return []

        try:
            sentence = self.Sentence(text)
            self.model.predict(sentence)

            entities = []
            for entity in sentence.get_spans("ner"):
                start = entity.start_position
                end = entity.end_position
                entity_type = entity.tag.upper()

                entities.append(
                    ExtractedEntity(
                        text=entity.text,
                        type=entity_type,
                        character_start=start,
                        character_end=end,
                    )
                )

            return entities

        except Exception as e:
            print(f"Error extracting entities with Flair: {e}")
            return []
