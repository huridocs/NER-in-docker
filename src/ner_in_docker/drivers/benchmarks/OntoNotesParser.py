import glob
import os
import random
from typing import List, Dict


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
                        current_sentence = {"words": [], "ne_tags": []}

                    word = parts[3]
                    ne_tag = parts[10]

                    current_sentence["words"].append(word)
                    current_sentence["ne_tags"].append(ne_tag)

        return documents

    def extract_entities_from_sentence(self, sentence: Dict) -> List[Dict]:
        entities = []
        active_entities = {}
        char_position = 0

        for i, (word, tag) in enumerate(zip(sentence["words"], sentence["ne_tags"])):
            word_start = char_position
            word_end = char_position + len(word)

            clean_tag = tag.replace("(", "").replace(")", "").replace("*", "").strip()

            if "(" in tag and clean_tag:
                entity_type = clean_tag
                if entity_type in ENTITY_MAPPING:
                    mapped_type = ENTITY_MAPPING[entity_type]
                    active_entities[entity_type] = {
                        "text": word,
                        "type": mapped_type,
                        "start": word_start,
                        "end": word_end,
                        "words": [word],
                        "word_indices": [i],
                    }

            elif clean_tag and clean_tag in active_entities:
                entity = active_entities[clean_tag]
                entity["text"] += " " + word
                entity["end"] = word_end
                entity["words"].append(word)
                entity["word_indices"].append(i)

            if ")" in tag:
                for entity_type in list(active_entities.keys()):
                    entity = active_entities[entity_type]
                    if "(" in tag or entity["word_indices"][-1] == i:
                        entities.append(
                            {"text": entity["text"], "type": entity["type"], "start": entity["start"], "end": entity["end"]}
                        )
                        del active_entities[entity_type]
                        break

            char_position = word_end + 1

        for entity in active_entities.values():
            entities.append({"text": entity["text"], "type": entity["type"], "start": entity["start"], "end": entity["end"]})

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
                            sent_text = " ".join(sent["words"])
                            sent_text = sent_text.replace(" .", ".")
                            sent_text = sent_text.replace(" ,", ",")
                            sent_text = sent_text.replace(" !", "!")
                            sent_text = sent_text.replace(" ?", "?")
                            sent_text = sent_text.replace(" :", ":")
                            sent_text = sent_text.replace(" ;", ";")
                            sent_text = sent_text.replace("-LRB- ", "(")
                            sent_text = sent_text.replace(" -RRB-", ")")
                            sent_text = sent_text.replace("`` ", '"')
                            sent_text = sent_text.replace(" ''", '"')

                            sent_entities = self.extract_entities_from_sentence(sent)

                            for entity in sent_entities:
                                if entity["type"] in TARGET_ENTITIES:
                                    entity["start"] += char_offset
                                    entity["end"] += char_offset
                                    all_entities.append(entity)

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
