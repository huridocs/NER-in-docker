import json
import os
import random
import re
import sys
import pyperclip
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Tuple

from ner_in_docker.configuration import DATA_PATH
from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity
from ner_in_docker.drivers.benchmarks.NerEvaluator import NEREvaluator
from ner_in_docker.drivers.benchmarks.OntoNotesParser import OntoNotesParser, TARGET_ENTITIES

DATA_DIR = Path(DATA_PATH, "conll-2012", "v12", "data", "test")
TARGET_ENTITIES_PER_TYPE = 10


def find_entity_position_fuzzy(entity_text: str, original_text: str) -> Optional[Tuple[int, int]]:
    start = original_text.find(entity_text)
    if start != -1:
        return (start, start + len(entity_text))

    start = original_text.lower().find(entity_text.lower())
    if start != -1:
        return (start, start + len(entity_text))

    entity_normalized = entity_text.replace("'s", "").replace("'s", "").strip()
    entity_normalized = re.sub(r"\s*-\s*", "-", entity_normalized)
    entity_normalized = re.sub(r"\s+", " ", entity_normalized)

    entity_tokens = entity_normalized.replace("-", " ").split()
    if not entity_tokens:
        return None

    pattern_parts = []
    for i, token in enumerate(entity_tokens):
        escaped_token = re.escape(token)
        pattern_parts.append(escaped_token)

        if i < len(entity_tokens) - 1:
            pattern_parts.append(r"\s*-?\s*")

    pattern = "".join(pattern_parts) + r"(?:\s*'s?)?"

    try:
        match = re.search(pattern, original_text, re.IGNORECASE)
        if match:
            return (match.start(), match.end())
    except re.error:
        pass

    entity_tokens_lower = [t.lower() for t in entity_tokens]
    text_words = original_text.split()

    for i in range(len(text_words)):
        match_count = 0
        j = i
        while j < len(text_words) and match_count < len(entity_tokens_lower):
            word_clean = re.sub(r"[^\w\s-]", "", text_words[j]).lower()
            if word_clean == entity_tokens_lower[match_count] or entity_tokens_lower[match_count] in word_clean:
                match_count += 1
            elif match_count > 0:
                break
            j += 1

        if match_count == len(entity_tokens_lower):
            start_pos = original_text.find(text_words[i])
            if start_pos != -1:
                end_word = text_words[j - 1]
                end_pos = original_text.find(end_word, start_pos) + len(end_word)
                return (start_pos, end_pos)

    return None


def generate_prompt(text: str) -> str:
    prompt = f"""You are a Named Entity Recognition system. Extract ALL entities from the text and return ONLY a JSON array.

Task: Extract entities of these types:
- PERSON: Names of people
- ORGANIZATION: Companies, institutions, agencies
- LOCATION: Cities, countries, geographic locations

Instructions:
1. Find ALL entity mentions in the text
2. Return ONLY a valid JSON array
3. Each entity must have: text, type
4. Do NOT include markdown, explanations, or extra text

Example output format:
[
{{"text": "John Doe", "type": "PERSON"}},
{{"text": "New York", "type": "LOCATION"}}
]

Text to analyze:
{text}

Output (JSON array only):"""
    return prompt


def parse_model_response(response_text: str, original_text: str) -> List[ExtractedEntity]:
    try:
        response_text = response_text.strip()

        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        entities_data = json.loads(response_text)

        if isinstance(entities_data, dict) and "entities" in entities_data:
            entities_data = entities_data["entities"]

        if not isinstance(entities_data, list):
            print(f"Warning: Expected list, got {type(entities_data)}")
            return []

        extracted_entities = []
        for entity in entities_data:
            entity_text = entity.get("text", entity.get("source_text", ""))
            entity_type = entity.get("type", entity.get("entity_type", "")).upper()

            if not entity_text or not entity_type:
                continue

            start = entity.get("start", entity.get("character_start", -1))
            end = entity.get("end", entity.get("character_end", -1))

            if start == -1 or end == -1:
                position = find_entity_position_fuzzy(entity_text, original_text)
                if position:
                    start, end = position
                else:
                    print(f"Warning: Could not find entity '{entity_text}' in text (tried fuzzy matching)")
                    continue

            actual_text = original_text[start:end]

            extracted_entities.append(
                ExtractedEntity(text=actual_text, type=entity_type, character_start=start, character_end=end)
            )

        return extracted_entities

    except json.JSONDecodeError as e:
        print(f"\nERROR: JSON parsing error: {e}")
        print(f"Response was: {response_text[:200]}...")
        print("\nPlease make sure the model output is valid JSON.")
        return []
    except Exception as e:
        print(f"\nERROR: Error parsing response: {e}")
        return []


def copy_to_clipboard(text: str) -> bool:
    pyperclip.copy(text)
    return True


def get_user_input_multiline(prompt_message: str) -> str:
    print(prompt_message)
    print("(Paste the response and press Ctrl+D on Unix/Mac or Ctrl+Z on Windows, then Enter when done)")
    print("-" * 80)

    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    return "\n".join(lines)


def get_positive_float(prompt_message: str) -> float:
    while True:
        try:
            value = float(input(prompt_message))
            if value >= 0:
                return value
            else:
                print("Please enter a non-negative number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def main():
    print("=" * 80)
    print("MANUAL NER BENCHMARK - Cloud Models")
    print("=" * 80)

    print("\nEnter the model name (for display purposes only):")
    model_name = input("> ").strip()
    if not model_name:
        model_name = "Cloud Model"

    print(f"\nModel: {model_name}")

    print("\n" + "-" * 80)
    print("Fuzzy Matching Configuration")
    print("-" * 80)
    print("Use fuzzy matching for evaluation? (recommended)")
    print("  Default: Character overlap 50%, Text similarity 80%")
    use_defaults = input("Use defaults? (Y/n): ").strip().lower()

    if use_defaults in ["n", "no"]:
        print("\nEnter overlap threshold (0.0-1.0, default 0.5):")
        overlap_threshold = get_positive_float("> ")
        if overlap_threshold > 1.0:
            overlap_threshold = 0.5
            print(f"Invalid value, using default: {overlap_threshold}")

        print("\nEnter text similarity threshold (0.0-1.0, default 0.8):")
        text_similarity_threshold = get_positive_float("> ")
        if text_similarity_threshold > 1.0:
            text_similarity_threshold = 0.8
            print(f"Invalid value, using default: {text_similarity_threshold}")
    else:
        overlap_threshold = 0.5
        text_similarity_threshold = 0.8

    print("\n✓ Using fuzzy matching with:")
    print(f"  - Character overlap threshold: {overlap_threshold:.0%}")
    print(f"  - Text similarity threshold: {text_similarity_threshold:.0%}")
    print("=" * 80)

    random.seed(42)

    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory not found: {DATA_DIR}")
        return

    print("\n1. Initializing OntoNotes parser...")
    parser = OntoNotesParser(str(DATA_DIR))

    print(f"\n2. Extracting paragraphs with at least {TARGET_ENTITIES_PER_TYPE} entities per type...")
    paragraphs = parser.get_paragraphs_with_entities(TARGET_ENTITIES_PER_TYPE)

    print(f"Successfully extracted {len(paragraphs)} paragraphs")

    if not paragraphs:
        print("Error: No paragraphs found!")
        return

    sample = paragraphs[0]
    print("\nSample paragraph:")
    print(f"  Text: {sample['text'][:100]}...")
    print(f"  Entities: {len(sample['entities'])}")
    entity_counts = defaultdict(int)
    for e in sample["entities"]:
        entity_counts[e["type"]] += 1
    print(f"  Entity breakdown: {dict(entity_counts)}")

    print("\n" + "=" * 80)
    print("Ready to start benchmark!")
    print(f"You will process {len(paragraphs)} paragraphs.")
    print("\nFor each paragraph:")
    print("  1. The prompt will be copied to your clipboard (if available)")
    print("  2. You paste it to the cloud model and copy the response")
    print("  3. You paste the model's response here")
    print("  4. You enter the time it took to process")
    print("=" * 80)

    input("\nPress Enter to start...")

    evaluator = NEREvaluator(overlap_threshold=overlap_threshold, text_similarity_threshold=text_similarity_threshold)
    total_time = 0.0

    print("\n" + "=" * 80)
    print("PROCESSING PARAGRAPHS")
    print("=" * 80)

    for i, paragraph in enumerate(paragraphs, 1):
        print(f"\n{'=' * 80}")
        print(f"Paragraph {i}/{len(paragraphs)}")
        print(f"{'=' * 80}")

        text = paragraph["text"]
        preview_length = 150
        if len(text) > preview_length:
            print(f"Text preview: {text[:preview_length]}...")
        else:
            print(f"Text: {text}")

        print(f"\nGround truth: {len(paragraph['entities'])} entities")

        prompt = generate_prompt(text)

        if copy_to_clipboard(prompt):
            print("\n✓ Prompt copied to clipboard!")
        else:
            print("\n⚠ Clipboard not available. Here's the prompt:")
            print("-" * 80)
            print(prompt)
            print("-" * 80)

        print("\nGo to your cloud model, paste the prompt, and copy the response.")
        response_text = get_user_input_multiline("\nNow paste the model's response here:")

        predicted_entities = parse_model_response(response_text, text)
        print(f"\n✓ Parsed {len(predicted_entities)} entities from response")

        print("\nExpanding predictions to match all ground truth occurrences...")
        expanded_entities = []
        ground_truth = paragraph["entities"]
        used_gt_indices = set()

        for pred_entity in predicted_entities:
            pred_type = pred_entity.type.upper()
            if pred_type not in TARGET_ENTITIES:
                expanded_entities.append(pred_entity)
                continue

            similar_gt_entities = []
            for j, gt_entity in enumerate(ground_truth):
                if j in used_gt_indices:
                    continue
                if gt_entity["type"] != pred_type:
                    continue

                text_sim = evaluator.calculate_text_similarity(pred_entity.text, gt_entity["text"])
                if text_sim >= 0.8:
                    similar_gt_entities.append((j, gt_entity))

            if similar_gt_entities:
                for gt_idx, gt_entity in similar_gt_entities:
                    used_gt_indices.add(gt_idx)
                    expanded_entity = ExtractedEntity(
                        text=gt_entity["text"],
                        type=pred_type,
                        character_start=gt_entity["start"],
                        character_end=gt_entity["end"],
                    )
                    expanded_entities.append(expanded_entity)

                if len(similar_gt_entities) > 1:
                    print(f"  Expanded '{pred_entity.text}' ({pred_type}) → {len(similar_gt_entities)} occurrences")
            else:
                expanded_entities.append(pred_entity)

        predicted_entities = expanded_entities
        print(f"✓ Expanded to {len(predicted_entities)} entities")

        elapsed_time = get_positive_float("\nEnter the time elapsed for this paragraph (in seconds): ")
        total_time += elapsed_time

        print(f"\n{'='*80}")
        print("GROUND TRUTH ENTITIES IN THIS PARAGRAPH:")
        print("=" * 80)
        from collections import Counter

        ground_truth = paragraph["entities"]
        gt_by_type = {}
        for gt_entity in ground_truth:
            entity_type = gt_entity["type"]
            if entity_type not in gt_by_type:
                gt_by_type[entity_type] = []
            gt_by_type[entity_type].append(gt_entity["text"])

        for entity_type in sorted(gt_by_type.keys()):
            entities = gt_by_type[entity_type]
            counter = Counter(entities)
            print(f"\n{entity_type}:")
            for text, count in counter.most_common():
                if count > 1:
                    print(f"  - '{text}' (appears {count} times)")
                else:
                    print(f"  - '{text}'")

        print(f"\n{'='*80}")
        print("MODEL PREDICTED ENTITIES:")
        print("=" * 80)
        pred_by_type = {}
        for pred_entity in predicted_entities:
            entity_type = pred_entity.type.upper()
            if entity_type not in TARGET_ENTITIES:
                continue
            if entity_type not in pred_by_type:
                pred_by_type[entity_type] = []
            pred_by_type[entity_type].append(pred_entity.text)

        for entity_type in sorted(pred_by_type.keys()):
            entities = pred_by_type[entity_type]
            counter = Counter(entities)
            print(f"\n{entity_type}:")
            for text, count in counter.most_common():
                if count > 1:
                    print(f"  - '{text}' (appears {count} times)")
                else:
                    print(f"  - '{text}'")

        print(f"\n{'='*80}")
        print("EVALUATION DETAILS")
        print("=" * 80)

        match_details = evaluator.evaluate_paragraph(paragraph, predicted_entities)

        for match_info in match_details["matched_predictions"]:
            pred_entity = match_info["prediction"]
            matched_gt_entities = match_info["matched_ground_truth"]
            match_score = match_info["match_score"]
            num_matches = match_info["num_matches"]

            pred_type = pred_entity.type.upper()
            pred_start = pred_entity.character_start
            pred_end = pred_entity.character_end

            if num_matches > 1:
                print(
                    f"✓ MATCH ({pred_type}): '{pred_entity.text}' at pos {pred_start}:{pred_end} matched {num_matches} GT occurrences [score: {match_score:.1%}]"
                )
                for gt_entity in matched_gt_entities:
                    print(f"    - GT '{gt_entity['text']}' at pos {gt_entity['start']}:{gt_entity['end']}")
            else:
                gt_entity = matched_gt_entities[0]
                print(
                    f"✓ MATCH ({pred_type}): '{pred_entity.text}' at pos {pred_start}:{pred_end} matched GT '{gt_entity['text']}' at pos {gt_entity['start']}:{gt_entity['end']} [score: {match_score:.1%}]"
                )

        for pred_entity in match_details["false_positives"]:
            pred_type = pred_entity.type.upper()
            print(
                f"✗ FALSE POSITIVE ({pred_type}): Model found '{pred_entity.text}' at pos {pred_entity.character_start}:{pred_entity.character_end} but it doesn't match any ground truth entity"
            )

        for gt_entity in match_details["false_negatives"]:
            print(
                f"✗ FALSE NEGATIVE ({gt_entity['type']}): Ground truth has '{gt_entity['text']}' at pos {gt_entity['start']}:{gt_entity['end']} but model didn't find it"
            )

        print("=" * 80)

        print(f"\n✓ Paragraph {i} complete!")
        print(f"  Ground truth: {len(paragraph['entities'])} entities")
        print(f"  Predicted: {len(predicted_entities)} entities")

        matched_count = sum(len(m["matched_ground_truth"]) for m in match_details["matched_predictions"])
        print(f"  Matched: {matched_count} entities")
        print(f"  False Positives: {len(match_details['false_positives'])}")
        print(f"  False Negatives: {len(match_details['false_negatives'])}")
        print(f"  Time: {elapsed_time:.2f}s")

    print("\n" + "=" * 80)
    print("Computing final metrics...")
    print("=" * 80)

    metrics = evaluator.print_results(model_name, total_time)

    output_file = Path(DATA_PATH, f"manual_benchmark_{model_name.replace(' ', '_').lower()}.json")
    results = {
        "model_name": model_name,
        "num_paragraphs": len(paragraphs),
        "total_time_seconds": total_time,
        "avg_time_per_paragraph_seconds": total_time / len(paragraphs),
        "evaluation_config": {
            "overlap_threshold": overlap_threshold,
            "text_similarity_threshold": text_similarity_threshold,
        },
        "metrics": metrics,
        "config": {
            "data_dir": str(DATA_DIR),
            "entity_types": TARGET_ENTITIES,
            "target_entities_per_type": TARGET_ENTITIES_PER_TYPE,
        },
    }

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to {output_file}")
    print("\nBenchmark completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
        sys.exit(1)
