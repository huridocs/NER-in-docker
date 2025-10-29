import glob
import os
import random
from typing import List, Dict, Optional


ENTITY_MAPPING = {
    "PERSON": "PERSON",
    "ORG": "ORGANIZATION",
    "LOC": "LOCATION",
    "GPE": "LOCATION",
}

TARGET_ENTITIES = ["PERSON", "LOCATION", "ORGANIZATION"]


class OntoNotesParser:

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def parse_conll_file(self, filepath: str) -> List[Dict]:
        documents = []
        current_document = None
        current_sentence = None

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if line.startswith("#begin document"):
                    current_document = {"doc_id": line.split("(")[1].split(")")[0], "sentences": []}

                elif line.startswith("#end document"):
                    if current_document:
                        documents.append(current_document)
                        current_document = None

                elif line == "":
                    if current_sentence and len(current_sentence["words"]) > 0:
                        current_document["sentences"].append(current_sentence)
                        current_sentence = None

                elif not line.startswith("#") and current_document:
                    parts = line.split()
                    if len(parts) < 11:
                        continue

                    if current_sentence is None:
                        current_sentence = {"words": [], "ne_tags": [], "pos_tags": []}

                    word = parts[3]
                    pos_tag = parts[4]
                    ne_tag = parts[10]

                    current_sentence["words"].append(word)
                    current_sentence["pos_tags"].append(pos_tag)
                    current_sentence["ne_tags"].append(ne_tag)

        return documents

    def _convert_to_bio_tags(self, ne_tags: List[str]) -> List[str]:
        """
        Convert CoNLL parenthesis format to BIO tags.
        Based on the official OntoNotes implementation.

        Examples:
            "(PERSON)" -> "B-PERSON"
            "(PERSON*" -> "B-PERSON"
            "*" -> "I-{current_label}" (if inside a span) or "O" (if outside)
            "*)" -> "I-{current_label}"
            "*" (not in span) -> "O"
        """
        bio_tags = []
        current_label: Optional[str] = None

        for annotation in ne_tags:
            label = annotation.strip("()*")

            if "(" in annotation:
                bio_tags.append(f"B-{label}")
                current_label = label
            elif current_label is not None:
                bio_tags.append(f"I-{current_label}")
            else:
                bio_tags.append("O")

            if ")" in annotation:
                current_label = None

        return bio_tags

    def extract_entities_from_sentence(self, sentence: Dict) -> List[Dict]:
        bio_tags = self._convert_to_bio_tags(sentence["ne_tags"])

        entities = []
        current_entity = None
        char_position = 0

        for i, (word, bio_tag) in enumerate(zip(sentence["words"], bio_tags)):
            word_start = char_position
            word_end = char_position + len(word)

            if bio_tag.startswith("B-"):
                if current_entity is not None:
                    entities.append(current_entity)

                entity_label = bio_tag[2:]
                if entity_label in ENTITY_MAPPING:
                    current_entity = {
                        "text": word,
                        "type": ENTITY_MAPPING[entity_label],
                        "start": word_start,
                        "end": word_end,
                    }
                else:
                    current_entity = None

            elif bio_tag.startswith("I-"):
                if current_entity is not None:
                    current_entity["text"] += " " + word
                    current_entity["end"] = word_end

            else:
                if current_entity is not None:
                    entities.append(current_entity)
                    current_entity = None

            char_position = word_end + 1

        if current_entity is not None:
            entities.append(current_entity)

        return entities

    def get_paragraphs_with_entities(self, target_entities_per_type: int = 10) -> List[Dict]:
        pattern = os.path.join(self.data_dir, "**/*.gold_conll")
        all_files = glob.glob(pattern, recursive=True)

        print(f"Found {len(all_files)} CoNLL files")

        random.shuffle(all_files)

        all_paragraphs = []

        for filepath in all_files:
            try:
                documents = self.parse_conll_file(filepath)

                for doc in documents:
                    sentences = doc["sentences"]

                    i = 0
                    while i < len(sentences):
                        para_size = min(random.randint(3, 5), len(sentences) - i)
                        para_sentences = sentences[i : i + para_size]

                        text_parts = []
                        all_entities = []
                        char_offset = 0

                        for sent in para_sentences:
                            sent_entities = self.extract_entities_from_sentence(sent)

                            sent_text = " ".join(sent["words"])

                            def clean_text(text):
                                text = text.replace(" .", ".")
                                text = text.replace(" ,", ",")
                                text = text.replace(" !", "!")
                                text = text.replace(" ?", "?")
                                text = text.replace(" :", ":")
                                text = text.replace(" ;", ";")
                                text = text.replace("-LRB- ", "(")
                                text = text.replace(" -RRB-", ")")
                                text = text.replace("`` ", '"')
                                text = text.replace(" ''", '"')
                                return text

                            sent_text = clean_text(sent_text)

                            sent_entities_sorted = sorted(sent_entities, key=lambda e: e["start"])
                            search_start = 0

                            for entity in sent_entities_sorted:
                                if entity["type"] in TARGET_ENTITIES:
                                    entity_text = clean_text(entity["text"])
                                    new_start = sent_text.find(entity_text, search_start)
                                    if new_start != -1:
                                        entity["text"] = entity_text
                                        entity["start"] = new_start + char_offset
                                        entity["end"] = new_start + len(entity_text) + char_offset
                                        all_entities.append(entity)
                                        search_start = new_start + len(entity_text)

                            text_parts.append(sent_text)
                            char_offset += len(sent_text) + 1

                        paragraph_text = " ".join(text_parts)

                        if len(all_entities) > 0 and len(paragraph_text.strip()) > 50:
                            all_paragraphs.append(
                                {"text": paragraph_text, "entities": all_entities, "doc_id": doc["doc_id"]}
                            )

                        i += para_size

            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                continue

        print(f"\nCollected {len(all_paragraphs)} candidate paragraphs")

        paragraphs_by_type = {entity_type: [] for entity_type in TARGET_ENTITIES}
        for para in all_paragraphs:
            entity_types_in_para = set(e["type"] for e in para["entities"])
            for entity_type in entity_types_in_para:
                paragraphs_by_type[entity_type].append(para)

        for entity_type in TARGET_ENTITIES:
            random.shuffle(paragraphs_by_type[entity_type])

        selected_paragraphs = []
        entity_counts = {entity_type: 0 for entity_type in TARGET_ENTITIES}

        while not all(count >= target_entities_per_type for count in entity_counts.values()):
            min_ratio = float("inf")
            best_entity_type = None

            for entity_type in TARGET_ENTITIES:
                if entity_counts[entity_type] < target_entities_per_type:
                    ratio = entity_counts[entity_type] / target_entities_per_type
                    if ratio < min_ratio:
                        min_ratio = ratio
                        best_entity_type = entity_type

            if best_entity_type is None:
                break

            found = False
            for para in paragraphs_by_type[best_entity_type]:
                if para not in selected_paragraphs:
                    selected_paragraphs.append(para)
                    for entity in para["entities"]:
                        entity_counts[entity["type"]] += 1
                    found = True
                    break

            if not found:
                print(f"Warning: Could not find enough paragraphs for {best_entity_type}")
                break

        print("\nFinal entity counts after selection:")
        for entity_type in TARGET_ENTITIES:
            print(f"  {entity_type}: {entity_counts[entity_type]}")

        return selected_paragraphs
