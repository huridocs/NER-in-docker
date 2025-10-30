import json
import time
from pathlib import Path
from typing import List, Dict

from ner_in_docker.drivers.benchmarks.EntityExtractor import EntityExtractor
from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity
from ner_in_docker.drivers.benchmarks.NerEvaluator import NEREvaluator, TARGET_ENTITIES


class BenchmarkRunner:

    def __init__(
        self,
        paragraphs: List[Dict],
        output_path: Path = None,
        overlap_threshold: float = 0.5,
        text_similarity_threshold: float = 0.8,
    ):
        self.paragraphs = paragraphs
        self.output_path = output_path
        self.overlap_threshold = overlap_threshold
        self.text_similarity_threshold = text_similarity_threshold
        self.results_by_extractor = {}

    def run(self, extractors: List[EntityExtractor]) -> Dict:
        for extractor in extractors:
            print(f"\n{'='*80}")
            print(f"TESTING: {extractor.get_name()}")
            print(f"{'='*80}")

            print("\nWarming up model (loading into memory)...")
            extractor.warmup()
            print("Warmup complete. Starting benchmark...")

            evaluator = NEREvaluator(
                overlap_threshold=self.overlap_threshold,
                text_similarity_threshold=self.text_similarity_threshold,
            )
            elapsed_time = self._run_extractor(extractor, evaluator)

            print("\nComputing final metrics...")
            metrics = evaluator.print_results(extractor.get_name(), elapsed_time)

            metrics["elapsed_time_seconds"] = elapsed_time
            metrics["avg_time_per_paragraph_seconds"] = elapsed_time / len(self.paragraphs) if self.paragraphs else 0

            self.results_by_extractor[extractor.get_name()] = metrics

        return self.results_by_extractor

    def _expand_predictions(
        self, predicted_entities: List[ExtractedEntity], ground_truth: List[Dict], evaluator: NEREvaluator
    ) -> List[ExtractedEntity]:
        expanded_entities = []
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
            else:
                expanded_entities.append(pred_entity)

        return expanded_entities

    def _run_extractor(self, extractor: EntityExtractor, evaluator: NEREvaluator) -> float:
        print(f"\nProcessing {len(self.paragraphs)} paragraphs...")
        print("-" * 80)

        start_time = time.time()

        for i, paragraph in enumerate(self.paragraphs, 1):
            print(f"Paragraph {i}/{len(self.paragraphs)}...", end=" ")

            predicted_entities = extractor.extract(paragraph["text"])

            expanded_entities = self._expand_predictions(predicted_entities, paragraph["entities"], evaluator)

            print(
                f"(GT: {len(paragraph['entities'])} entities, Pred: {len(predicted_entities)} → {len(expanded_entities)} expanded)"
            )

            evaluator.evaluate_paragraph(paragraph, expanded_entities)

        elapsed_time = time.time() - start_time
        return elapsed_time

    def save_results(self, config: Dict = None):
        if self.output_path is None:
            return

        output_data = {
            "num_paragraphs": len(self.paragraphs),
            "evaluation_config": {
                "overlap_threshold": self.overlap_threshold,
                "text_similarity_threshold": self.text_similarity_threshold,
            },
            "results_by_extractor": self.results_by_extractor,
        }

        if config:
            output_data["config"] = config

        with open(str(self.output_path), "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\n✓ Results saved to {self.output_path}")
