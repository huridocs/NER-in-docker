import os
import random
from collections import defaultdict
from pathlib import Path

from ner_in_docker.configuration import DATA_PATH
from ner_in_docker.drivers.benchmarks.BenchmarkRunner import BenchmarkRunner
from ner_in_docker.drivers.benchmarks.Extractors.LlamaExtractor import LlamaExtractor
from ner_in_docker.drivers.benchmarks.Extractors.GPTExtractor import GPTExtractor
from ner_in_docker.drivers.benchmarks.Extractors.DeepseekExtractor import DeepseekExtractor
from ner_in_docker.drivers.benchmarks.Extractors.QwenExtractor import QwenExtractor
from ner_in_docker.drivers.benchmarks.Extractors.NerServiceExtractor import NerServiceExtractor
from ner_in_docker.drivers.benchmarks.OntoNotesParser import OntoNotesParser, TARGET_ENTITIES

DATA_DIR = Path(DATA_PATH, "conll-2012", "v12", "data", "test")
TARGET_ENTITIES_PER_TYPE = 10

EXTRACTORS = [
    # NerServiceExtractor(),
    # LlamaExtractor(),
    GPTExtractor(),
    # DeepseekExtractor(),
    # QwenExtractor(),
]


def main():
    print("Starting NER Service Benchmark...")
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

    if paragraphs:
        sample = paragraphs[0]
        print("\nSample paragraph:")
        print(f"  Text: {sample['text'][:100]}...")
        print(f"  Entities: {len(sample['entities'])}")
        entity_counts = defaultdict(int)
        for e in sample["entities"]:
            entity_counts[e["type"]] += 1
        print(f"  Entity breakdown: {dict(entity_counts)}")

    print("\n3. Initializing extractors...")

    output_file = Path(DATA_PATH, "benchmark_results.json")
    runner = BenchmarkRunner(paragraphs, output_file)
    runner.run(EXTRACTORS)

    runner.save_results(config={"data_dir": str(DATA_DIR), "entity_types": TARGET_ENTITIES})

    print("\nBenchmark completed successfully!")


if __name__ == "__main__":
    main()
