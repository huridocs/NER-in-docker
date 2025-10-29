import json
import os
import random
import sys
import pyperclip
from collections import defaultdict
from pathlib import Path
from typing import List

from ner_in_docker.configuration import DATA_PATH
from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity
from ner_in_docker.drivers.benchmarks.NerEvaluator import NEREvaluator
from ner_in_docker.drivers.benchmarks.OntoNotesParser import OntoNotesParser, TARGET_ENTITIES

DATA_DIR = Path(DATA_PATH, "conll-2012", "v12", "data", "test")
TARGET_ENTITIES_PER_TYPE = 10


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
                start = original_text.find(entity_text)
                if start != -1:
                    end = start + len(entity_text)
                else:
                    start = original_text.lower().find(entity_text.lower())
                    if start != -1:
                        end = start + len(entity_text)
                    else:
                        print(f"Warning: Could not find entity '{entity_text}' in text")
                        continue

            extracted_entities.append(
                ExtractedEntity(text=entity_text, type=entity_type, character_start=start, character_end=end)
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

    evaluator = NEREvaluator()
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

        elapsed_time = get_positive_float("\nEnter the time elapsed for this paragraph (in seconds): ")
        total_time += elapsed_time

        evaluator.evaluate_paragraph(paragraph, predicted_entities)

        print(f"\n✓ Paragraph {i} complete!")
        print(f"  Ground truth: {len(paragraph['entities'])} entities")
        print(f"  Predicted: {len(predicted_entities)} entities")
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
