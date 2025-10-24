import json
from pathlib import Path
from typing import List, Dict

from ner_in_docker.drivers.benchmarks.EntityExtractor import EntityExtractor
from ner_in_docker.drivers.benchmarks.NerEvaluator import NEREvaluator


class BenchmarkRunner:

    def __init__(self, paragraphs: List[Dict], output_path: Path = None):
        self.paragraphs = paragraphs
        self.output_path = output_path
        self.results_by_extractor = {}

    def run(self, extractors: List[EntityExtractor]) -> Dict:
        for extractor in extractors:
            print(f"\n{'='*80}")
            print(f"TESTING: {extractor.get_name()}")
            print(f"{'='*80}")

            evaluator = NEREvaluator()
            self._run_extractor(extractor, evaluator)

            print("\nComputing final metrics...")
            metrics = evaluator.print_results()
            self.results_by_extractor[extractor.get_name()] = metrics

        return self.results_by_extractor

    def _run_extractor(self, extractor: EntityExtractor, evaluator: NEREvaluator):
        print(f"\nProcessing {len(self.paragraphs)} paragraphs...")
        print("-" * 80)

        for i, paragraph in enumerate(self.paragraphs, 1):
            print(f"Paragraph {i}/{len(self.paragraphs)}...", end=" ")

            predicted_entities = extractor.extract(paragraph["text"])

            print(f"(GT: {len(paragraph['entities'])} entities, Pred: {len(predicted_entities)} entities)")

            evaluator.evaluate_paragraph(paragraph, predicted_entities)

    def save_results(self, config: Dict = None):
        if self.output_path is None:
            return

        output_data = {
            "num_paragraphs": len(self.paragraphs),
            "results_by_extractor": self.results_by_extractor,
        }

        if config:
            output_data["config"] = config

        with open(str(self.output_path), "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\n✓ Results saved to {self.output_path}")
