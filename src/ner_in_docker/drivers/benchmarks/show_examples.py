import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from pathlib import Path
import requests
from benchmark_ner import OntoNotesParser, TARGET_ENTITIES
import random

from ner_in_docker.configuration import DATA_PATH


def normalize_entity(entity):
    """Normalize entity for display."""
    return {
        "text": entity.get("text", ""),
        "type": entity.get("type", ""),
        "start": entity.get("start", entity.get("character_start", -1)),
        "end": entity.get("end", entity.get("character_end", -1)),
    }


def display_paragraph_comparison(paragraph_num, paragraph, predicted_entities):
    """Display detailed comparison for a paragraph."""

    print(f"\n{'='*100}")
    print(f"PARAGRAPH {paragraph_num}")
    print(f"{'='*100}")

    # Display text
    text = paragraph["text"]
    print(f"\nText ({len(text)} chars):")
    print(f"  {text[:200]}{'...' if len(text) > 200 else ''}")

    # Display ground truth entities
    print(f"\nGround Truth Entities ({len(paragraph['entities'])}):")
    print(f"  {'Type':<15} {'Text':<40} {'Position':<15}")
    print(f"  {'-'*70}")
    for entity in sorted(paragraph["entities"], key=lambda e: e["start"]):
        print(f"  {entity['type']:<15} {entity['text'][:40]:<40} {entity['start']}-{entity['end']}")

    # Display predicted entities
    print(f"\nPredicted Entities ({len(predicted_entities)}):")
    print(f"  {'Type':<15} {'Text':<40} {'Position':<15}")
    print(f"  {'-'*70}")
    for entity in sorted(predicted_entities, key=lambda e: normalize_entity(e)["start"]):
        norm = normalize_entity(entity)
        if norm["type"].upper() in TARGET_ENTITIES:
            print(f"  {norm['type']:<15} {norm['text'][:40]:<40} {norm['start']}-{norm['end']}")

    # Find matches and mismatches
    gt_entities = paragraph["entities"]
    matches = []
    missed = []
    false_positives = []

    # Track which entities matched
    matched_gt = set()
    matched_pred = set()

    # Find matches
    for i, pred in enumerate(predicted_entities):
        norm_pred = normalize_entity(pred)
        if norm_pred["type"].upper() not in TARGET_ENTITIES:
            continue

        best_match = None
        best_overlap = 0

        for j, gt in enumerate(gt_entities):
            if j in matched_gt:
                continue
            if gt["type"] != norm_pred["type"].upper():
                continue

            # Calculate overlap
            overlap_start = max(gt["start"], norm_pred["start"])
            overlap_end = min(gt["end"], norm_pred["end"])
            if overlap_start < overlap_end:
                overlap = (overlap_end - overlap_start) / (gt["end"] - gt["start"])
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_match = j

        if best_match is not None and best_overlap >= 0.5:
            matched_gt.add(best_match)
            matched_pred.add(i)
            matches.append((gt_entities[best_match], norm_pred, best_overlap))
        else:
            false_positives.append(norm_pred)

    # Find missed entities
    for j, gt in enumerate(gt_entities):
        if j not in matched_gt:
            missed.append(gt)

    # Display analysis
    print(f"\nAnalysis:")
    print(f"  ✓ Correct matches: {len(matches)}")
    print(f"  ✗ Missed (False Negatives): {len(missed)}")
    print(f"  ✗ Wrong predictions (False Positives): {len(false_positives)}")

    if matches:
        print(f"\n  Correct Matches:")
        for gt, pred, overlap in matches:
            print(f"    ✓ {gt['type']:<12} '{gt['text'][:30]}' (overlap: {overlap:.0%})")

    if missed:
        print(f"\n  Missed Entities (should have been detected):")
        for gt in missed:
            print(f"    ✗ {gt['type']:<12} '{gt['text'][:30]}' at position {gt['start']}-{gt['end']}")

    if false_positives:
        print(f"\n  False Positives (incorrectly detected):")
        for pred in false_positives:
            print(f"    ✗ {pred['type']:<12} '{pred['text'][:30]}' at position {pred['start']}-{pred['end']}")


def main():
    """Show examples of predictions vs ground truth."""

    print("Named Entity Recognition - Example Comparisons")
    print("=" * 100)

    # Configuration
    DATA_DIR = Path(DATA_PATH, "conll-2012", "v12", "data", "test")
    SERVICE_URL = "http://localhost:5070/"
    NUM_EXAMPLES = 5

    # Set seed for reproducibility (same paragraphs as benchmark)
    random.seed(42)

    # Extract paragraphs
    print(f"\nExtracting {NUM_EXAMPLES} example paragraphs...")
    parser = OntoNotesParser(DATA_DIR)
    paragraphs = parser.get_paragraphs_with_entities(NUM_EXAMPLES)

    print(f"Found {len(paragraphs)} paragraphs\n")

    # Process each paragraph
    for i, paragraph in enumerate(paragraphs, 1):
        # Get predictions
        try:
            response = requests.post(
                SERVICE_URL, files={"text": (None, paragraph["text"]), "namespace": (None, "examples")}, timeout=30
            )
            response.raise_for_status()
            result = response.json()
            predicted_entities = result.get("entities", [])
        except Exception as e:
            print(f"Error calling service: {e}")
            predicted_entities = []

        # Display comparison
        display_paragraph_comparison(i, paragraph, predicted_entities)

        if i < len(paragraphs):
            input("\nPress Enter to continue to next example...")

    print(f"\n{'='*100}")
    print("Examples completed!")
    print("\nTo see full benchmark results, run: python3 benchmark_ner.py")


if __name__ == "__main__":
    main()
