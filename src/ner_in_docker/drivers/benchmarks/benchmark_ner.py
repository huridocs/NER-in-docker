import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import glob
import json
from pathlib import Path
import requests
from collections import defaultdict
from typing import List, Dict
import random

from ner_in_docker.configuration import DATA_PATH, SRC_PATH


# Named entity tag mappings from OntoNotes to service categories
ENTITY_MAPPING = {
    "PERSON": "PERSON",
    "ORG": "ORGANIZATION",
    "LOC": "LOCATION",
    "GPE": "LOCATION",  # Geo-Political Entity maps to LOCATION
}

# Target entity types we want to benchmark
TARGET_ENTITIES = ["PERSON", "LOCATION", "ORGANIZATION"]


class OntoNotesParser:
    """Parser for CoNLL-2012 OntoNotes format files."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def parse_conll_file(self, filepath: str) -> List[Dict]:
        """
        Parse a single CoNLL file and extract documents with sentences and entities.

        Returns:
            List of documents, each containing sentences with words and named entities.
        """
        documents = []
        current_document = None
        current_sentence = None

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Document start
                if line.startswith("#begin document"):
                    current_document = {"doc_id": line.split("(")[1].split(")")[0], "sentences": []}

                # Document end
                elif line.startswith("#end document"):
                    if current_document:
                        documents.append(current_document)
                        current_document = None

                # Empty line indicates sentence boundary
                elif line == "":
                    if current_sentence and len(current_sentence["words"]) > 0:
                        current_document["sentences"].append(current_sentence)
                        current_sentence = None

                # Parse CoNLL line
                elif not line.startswith("#") and current_document:
                    parts = line.split()
                    if len(parts) < 11:
                        continue

                    if current_sentence is None:
                        current_sentence = {"words": [], "ne_tags": []}

                    # Extract word (column 3) and NE tag (column 10)
                    word = parts[3]
                    ne_tag = parts[10]

                    current_sentence["words"].append(word)
                    current_sentence["ne_tags"].append(ne_tag)

        return documents

    def extract_entities_from_sentence(self, sentence: Dict) -> List[Dict]:
        """
        Extract entity mentions from a sentence with parenthesis-based NE tags.

        OntoNotes uses a parenthesis-based format like:
        - (PERSON*  = start of entity
        - *         = inside entity or no entity
        - *)        = end of entity
        - (GPE)     = single-word entity

        Returns:
            List of entities with text, type, start and end positions.
        """
        entities = []
        active_entities = {}  # entity_type -> {'text': ..., 'start': ..., 'words': [...]}
        char_position = 0

        for i, (word, tag) in enumerate(zip(sentence["words"], sentence["ne_tags"])):
            # Calculate character position
            word_start = char_position
            word_end = char_position + len(word)

            # Parse the NE tag
            # Remove all parentheses and asterisks to get entity type
            clean_tag = tag.replace("(", "").replace(")", "").replace("*", "").strip()

            # Check if this starts a new entity: contains '('
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

            # Check if we're inside an entity (has an active entity and not ending)
            elif clean_tag and clean_tag in active_entities:
                entity = active_entities[clean_tag]
                entity["text"] += " " + word
                entity["end"] = word_end
                entity["words"].append(word)
                entity["word_indices"].append(i)

            # Check if entity is ending: contains ')'
            if ")" in tag:
                # Find which entity is ending
                for entity_type in list(active_entities.keys()):
                    entity = active_entities[entity_type]
                    # If this is a single-word entity or we've been building it
                    if "(" in tag or entity["word_indices"][-1] == i:
                        entities.append(
                            {"text": entity["text"], "type": entity["type"], "start": entity["start"], "end": entity["end"]}
                        )
                        del active_entities[entity_type]
                        break

            # Update character position (word + space)
            char_position = word_end + 1

        # Add any remaining active entities (shouldn't happen in well-formed data)
        for entity in active_entities.values():
            entities.append({"text": entity["text"], "type": entity["type"], "start": entity["start"], "end": entity["end"]})

        return entities

    def get_paragraphs_with_entities(self, target_entities_per_type: int = 10) -> List[Dict]:
        """
        Extract paragraphs (groups of sentences) with named entities.
        Selects paragraphs to get approximately target_entities_per_type examples for each entity type.

        Args:
            target_entities_per_type: Target number of entity examples per type

        Returns:
            List of paragraphs with text and ground truth entities
        """
        # Get all gold_conll files
        pattern = os.path.join(self.data_dir, "**/*.gold_conll")
        all_files = glob.glob(pattern, recursive=True)

        print(f"Found {len(all_files)} CoNLL files")

        # Shuffle files for random selection
        random.shuffle(all_files)

        # First pass: collect all candidate paragraphs
        all_paragraphs = []

        for filepath in all_files:
            try:
                documents = self.parse_conll_file(filepath)

                for doc in documents:
                    # Group sentences into paragraphs (3-5 sentences per paragraph)
                    sentences = doc["sentences"]

                    i = 0
                    while i < len(sentences):
                        # Random paragraph size between 3 and 5 sentences
                        para_size = min(random.randint(3, 5), len(sentences) - i)
                        para_sentences = sentences[i : i + para_size]

                        # Reconstruct text and extract entities
                        text_parts = []
                        all_entities = []
                        char_offset = 0

                        for sent in para_sentences:
                            sent_text = " ".join(sent["words"])
                            # Fix common tokenization issues
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

                            # Extract entities for this sentence
                            sent_entities = self.extract_entities_from_sentence(sent)

                            # Adjust entity positions with current offset
                            for entity in sent_entities:
                                # Only include target entity types
                                if entity["type"] in TARGET_ENTITIES:
                                    entity["start"] += char_offset
                                    entity["end"] += char_offset
                                    all_entities.append(entity)

                            text_parts.append(sent_text)
                            char_offset += len(sent_text) + 1  # +1 for space between sentences

                        paragraph_text = " ".join(text_parts)

                        # Only include paragraphs with entities
                        if len(all_entities) > 0 and len(paragraph_text.strip()) > 50:
                            all_paragraphs.append(
                                {"text": paragraph_text, "entities": all_entities, "doc_id": doc["doc_id"]}
                            )

                        i += para_size

            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                continue

        print(f"\nCollected {len(all_paragraphs)} candidate paragraphs")

        # Second pass: select paragraphs to get approximately target_entities_per_type
        # Group paragraphs by which entity types they contain
        paragraphs_by_type = {entity_type: [] for entity_type in TARGET_ENTITIES}
        for para in all_paragraphs:
            entity_types_in_para = set(e["type"] for e in para["entities"])
            for entity_type in entity_types_in_para:
                paragraphs_by_type[entity_type].append(para)

        # Shuffle each list for random selection
        for entity_type in TARGET_ENTITIES:
            random.shuffle(paragraphs_by_type[entity_type])

        # Greedy selection: pick paragraphs that help us get closer to target
        selected_paragraphs = []
        entity_counts = {entity_type: 0 for entity_type in TARGET_ENTITIES}

        # Keep selecting paragraphs until we have enough of each type
        while not all(count >= target_entities_per_type for count in entity_counts.values()):
            # Find the entity type that needs the most entities
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

            # Find a paragraph that contains this entity type and hasn't been selected
            found = False
            for para in paragraphs_by_type[best_entity_type]:
                if para not in selected_paragraphs:
                    selected_paragraphs.append(para)
                    # Update counts
                    for entity in para["entities"]:
                        entity_counts[entity["type"]] += 1
                    found = True
                    break

            if not found:
                # No more paragraphs available for this entity type
                print(f"Warning: Could not find enough paragraphs for {best_entity_type}")
                break

        # Print final entity counts
        print("\nFinal entity counts after selection:")
        for entity_type in TARGET_ENTITIES:
            print(f"  {entity_type}: {entity_counts[entity_type]}")

        return selected_paragraphs


class NERServiceClient:
    """Client for the NER service API."""

    def __init__(self, service_url: str = "http://localhost:5070/"):
        self.service_url = service_url

    def extract_entities(self, text: str, namespace: str = "benchmark") -> List[Dict]:
        """
        Call the NER service to extract entities from text.

        Returns:
            List of predicted entities
        """
        try:
            response = requests.post(
                self.service_url, files={"text": (None, text), "namespace": (None, namespace)}, timeout=30
            )
            response.raise_for_status()

            result = response.json()

            # Extract entities from response
            if "entities" in result:
                return result["entities"]
            else:
                return []

        except Exception as e:
            print(f"Error calling NER service: {e}")
            return []


class NEREvaluator:
    """Evaluator for Named Entity Recognition performance."""

    def __init__(self):
        self.results = {
            entity_type: {
                "true_positives": 0,
                "false_positives": 0,
                "false_negatives": 0,
                "ground_truth_count": 0,
                "predicted_count": 0,
            }
            for entity_type in TARGET_ENTITIES
        }

    def normalize_text(self, text: str) -> str:
        """Normalize entity text for comparison."""
        return text.lower().strip()

    def calculate_overlap(self, gt_start: int, gt_end: int, pred_start: int, pred_end: int) -> float:
        """Calculate overlap ratio between two spans."""
        overlap_start = max(gt_start, pred_start)
        overlap_end = min(gt_end, pred_end)

        if overlap_start >= overlap_end:
            return 0.0

        overlap_len = overlap_end - overlap_start
        gt_len = gt_end - gt_start

        return overlap_len / gt_len if gt_len > 0 else 0.0

    def evaluate_paragraph(self, paragraph: Dict, predicted_entities: List[Dict]):
        """
        Evaluate predictions against ground truth for a single paragraph.

        Uses partial matching: predicted entity matches ground truth if:
        - Same entity type
        - At least 50% character overlap
        """
        ground_truth = paragraph["entities"]

        # Track matched ground truth entities
        matched_gt = set()
        matched_pred = set()

        # Count ground truth entities by type
        for gt_entity in ground_truth:
            entity_type = gt_entity["type"]
            self.results[entity_type]["ground_truth_count"] += 1

        # Count predicted entities by type
        for pred_entity in predicted_entities:
            entity_type = pred_entity.get("type", "").upper()
            if entity_type in TARGET_ENTITIES:
                self.results[entity_type]["predicted_count"] += 1

        # Match predicted entities to ground truth
        for i, pred_entity in enumerate(predicted_entities):
            pred_type = pred_entity.get("type", "").upper()

            if pred_type not in TARGET_ENTITIES:
                continue

            pred_start = pred_entity.get("character_start", -1)
            pred_end = pred_entity.get("character_end", -1)

            if pred_start < 0 or pred_end < 0:
                continue

            # Find best matching ground truth entity
            best_match_idx = -1
            best_overlap = 0.0

            for j, gt_entity in enumerate(ground_truth):
                if j in matched_gt:
                    continue

                gt_type = gt_entity["type"]

                # Type must match
                if gt_type != pred_type:
                    continue

                # Calculate overlap
                overlap = self.calculate_overlap(gt_entity["start"], gt_entity["end"], pred_start, pred_end)

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_match_idx = j

            # Accept match if overlap >= 50%
            if best_match_idx >= 0 and best_overlap >= 0.5:
                matched_gt.add(best_match_idx)
                matched_pred.add(i)
                self.results[pred_type]["true_positives"] += 1
            else:
                # False positive
                self.results[pred_type]["false_positives"] += 1

        # Count false negatives (unmatched ground truth)
        for j, gt_entity in enumerate(ground_truth):
            if j not in matched_gt:
                self.results[gt_entity["type"]]["false_negatives"] += 1

    def calculate_metrics(self) -> Dict:
        """Calculate precision, recall, and F1 score for each entity type."""
        metrics = {}

        for entity_type in TARGET_ENTITIES:
            stats = self.results[entity_type]

            tp = stats["true_positives"]
            fp = stats["false_positives"]
            fn = stats["false_negatives"]

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            metrics[entity_type] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
                "ground_truth_count": stats["ground_truth_count"],
                "predicted_count": stats["predicted_count"],
            }

        return metrics

    def print_results(self):
        """Print evaluation results in a formatted table."""
        metrics = self.calculate_metrics()

        print("\n" + "=" * 80)
        print("NER SERVICE BENCHMARK RESULTS")
        print("=" * 80)
        print("\nDataset: OntoNotes 5.0 (CoNLL-2012)")
        print("Target: 10 entities per type")
        print(f"Entity types: {', '.join(TARGET_ENTITIES)}")
        print("\n" + "-" * 80)
        print(f"{'Entity Type':<15} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'TP':<6} {'FP':<6} {'FN':<6}")
        print("-" * 80)

        for entity_type in TARGET_ENTITIES:
            m = metrics[entity_type]
            print(
                f"{entity_type:<15} "
                f"{m['precision']:<12.2%} "
                f"{m['recall']:<12.2%} "
                f"{m['f1']:<12.2%} "
                f"{m['true_positives']:<6} "
                f"{m['false_positives']:<6} "
                f"{m['false_negatives']:<6}"
            )

        # Calculate overall metrics (micro-average)
        total_tp = sum(m["true_positives"] for m in metrics.values())
        total_fp = sum(m["false_positives"] for m in metrics.values())
        total_fn = sum(m["false_negatives"] for m in metrics.values())

        overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        overall_f1 = (
            2 * overall_precision * overall_recall / (overall_precision + overall_recall)
            if (overall_precision + overall_recall) > 0
            else 0.0
        )

        print("-" * 80)
        print(
            f"{'OVERALL':<15} "
            f"{overall_precision:<12.2%} "
            f"{overall_recall:<12.2%} "
            f"{overall_f1:<12.2%} "
            f"{total_tp:<6} "
            f"{total_fp:<6} "
            f"{total_fn:<6}"
        )
        print("=" * 80)

        # Print ground truth vs predicted counts
        print("\nEntity counts:")
        print("-" * 50)
        print(f"{'Entity Type':<15} {'Ground Truth':<15} {'Predicted':<15}")
        print("-" * 50)
        for entity_type in TARGET_ENTITIES:
            m = metrics[entity_type]
            print(f"{entity_type:<15} {m['ground_truth_count']:<15} {m['predicted_count']:<15}")
        print("-" * 50)

        return metrics


def main():
    """Main benchmarking workflow."""

    print("Starting NER Service Benchmark...")
    print("=" * 80)

    # Set random seed for reproducibility
    random.seed(42)

    # Configuration
    DATA_DIR = Path(DATA_PATH, "conll-2012", "v12", "data", "test")
    SERVICE_URL = "http://localhost:5070/"
    TARGET_ENTITIES_PER_TYPE = 10

    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory not found: {DATA_DIR}")
        return

    # Initialize components
    print("\n1. Initializing OntoNotes parser...")
    parser = OntoNotesParser(DATA_DIR)

    print(f"\n2. Extracting paragraphs with at least {TARGET_ENTITIES_PER_TYPE} entities per type...")
    paragraphs = parser.get_paragraphs_with_entities(TARGET_ENTITIES_PER_TYPE)

    print(f"Successfully extracted {len(paragraphs)} paragraphs")

    # Print sample paragraph info
    if paragraphs:
        sample = paragraphs[0]
        print("\nSample paragraph:")
        print(f"  Text: {sample['text'][:100]}...")
        print(f"  Entities: {len(sample['entities'])}")
        entity_counts = defaultdict(int)
        for e in sample["entities"]:
            entity_counts[e["type"]] += 1
        print(f"  Entity breakdown: {dict(entity_counts)}")

    # Initialize NER client and evaluator
    print(f"\n3. Initializing NER service client (URL: {SERVICE_URL})...")
    client = NERServiceClient(SERVICE_URL)
    evaluator = NEREvaluator()

    # Process each paragraph
    print("\n4. Processing paragraphs and evaluating predictions...")
    print("-" * 80)

    for i, paragraph in enumerate(paragraphs, 1):
        print(f"Processing paragraph {i}/{len(paragraphs)}...", end=" ")

        # Get predictions from service
        predicted_entities = client.extract_entities(paragraph["text"])

        print(f"(GT: {len(paragraph['entities'])} entities, Pred: {len(predicted_entities)} entities)")

        # Evaluate
        evaluator.evaluate_paragraph(paragraph, predicted_entities)

    # Print results
    print("\n5. Computing final metrics...")
    metrics = evaluator.print_results()

    # Save results to file
    output_file = Path(DATA_PATH, "benchmark_results.json")
    with open(str(output_file), "w") as f:
        json.dump(
            {
                "num_paragraphs": len(paragraphs),
                "metrics": metrics,
                "config": {"data_dir": str(DATA_DIR), "service_url": SERVICE_URL, "entity_types": TARGET_ENTITIES},
            },
            f,
            indent=2,
        )

    print(f"\n✓ Results saved to {output_file}")
    print("\nBenchmark completed successfully!")


if __name__ == "__main__":
    main()
