import json
import os
import random
from collections import defaultdict
from pathlib import Path

from ner_in_docker.configuration import DATA_PATH
from ner_in_docker.drivers.benchmarks.ontonotes_parser import OntoNotesParser, TARGET_ENTITIES
from ner_in_docker.drivers.benchmarks.ner_service_client import NERServiceClient
from ner_in_docker.drivers.benchmarks.ner_evaluator import NEREvaluator


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
