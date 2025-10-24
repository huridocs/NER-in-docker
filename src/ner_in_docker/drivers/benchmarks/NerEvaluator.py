from typing import List, Dict

from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity


TARGET_ENTITIES = ["PERSON", "LOCATION", "ORGANIZATION"]


class NEREvaluator:

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
        return text.lower().strip()

    def calculate_overlap(self, gt_start: int, gt_end: int, pred_start: int, pred_end: int) -> float:
        overlap_start = max(gt_start, pred_start)
        overlap_end = min(gt_end, pred_end)

        if overlap_start >= overlap_end:
            return 0.0

        overlap_len = overlap_end - overlap_start
        gt_len = gt_end - gt_start

        return overlap_len / gt_len if gt_len > 0 else 0.0

    def evaluate_paragraph(self, paragraph: Dict, predicted_entities: List[ExtractedEntity]):
        ground_truth = paragraph["entities"]

        matched_gt = set()
        matched_pred = set()

        for gt_entity in ground_truth:
            entity_type = gt_entity["type"]
            self.results[entity_type]["ground_truth_count"] += 1

        for pred_entity in predicted_entities:
            entity_type = pred_entity.type.upper()
            if entity_type in TARGET_ENTITIES:
                self.results[entity_type]["predicted_count"] += 1

        for i, pred_entity in enumerate(predicted_entities):
            pred_type = pred_entity.type.upper()

            if pred_type not in TARGET_ENTITIES:
                continue

            pred_start = pred_entity.character_start
            pred_end = pred_entity.character_end

            if pred_start < 0 or pred_end < 0:
                continue

            best_match_idx = -1
            best_overlap = 0.0

            for j, gt_entity in enumerate(ground_truth):
                if j in matched_gt:
                    continue

                gt_type = gt_entity["type"]

                if gt_type != pred_type:
                    continue

                overlap = self.calculate_overlap(gt_entity["start"], gt_entity["end"], pred_start, pred_end)

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_match_idx = j

            if best_match_idx >= 0 and best_overlap >= 0.5:
                matched_gt.add(best_match_idx)
                matched_pred.add(i)
                self.results[pred_type]["true_positives"] += 1
            else:
                self.results[pred_type]["false_positives"] += 1

        for j, gt_entity in enumerate(ground_truth):
            if j not in matched_gt:
                self.results[gt_entity["type"]]["false_negatives"] += 1

    def calculate_metrics(self) -> Dict:
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

        print("\nEntity counts:")
        print("-" * 50)
        print(f"{'Entity Type':<15} {'Ground Truth':<15} {'Predicted':<15}")
        print("-" * 50)
        for entity_type in TARGET_ENTITIES:
            m = metrics[entity_type]
            print(f"{entity_type:<15} {m['ground_truth_count']:<15} {m['predicted_count']:<15}")
        print("-" * 50)

        return metrics
