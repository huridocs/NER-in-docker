from typing import List, Dict
from difflib import SequenceMatcher

from ner_in_docker.drivers.benchmarks.ExtractedEntity import ExtractedEntity


TARGET_ENTITIES = ["PERSON", "LOCATION", "ORGANIZATION"]


class NEREvaluator:

    def __init__(self, overlap_threshold: float = 0.5, text_similarity_threshold: float = 0.8):
        self.overlap_threshold = overlap_threshold
        self.text_similarity_threshold = text_similarity_threshold
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

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        norm_text1 = self.normalize_text(text1)
        norm_text2 = self.normalize_text(text2)
        return SequenceMatcher(None, norm_text1, norm_text2).ratio()

    def calculate_token_overlap(self, text1: str, text2: str) -> float:
        tokens1 = set(self.normalize_text(text1).split())
        tokens2 = set(self.normalize_text(text2).split())

        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return len(intersection) / len(union) if union else 0.0

    def calculate_overlap(self, gt_start: int, gt_end: int, pred_start: int, pred_end: int) -> float:
        overlap_start = max(gt_start, pred_start)
        overlap_end = min(gt_end, pred_end)

        if overlap_start >= overlap_end:
            return 0.0

        overlap_len = overlap_end - overlap_start
        gt_len = gt_end - gt_start

        return overlap_len / gt_len if gt_len > 0 else 0.0

    def is_entity_match(self, gt_entity: Dict, pred_entity: ExtractedEntity, paragraph_text: str) -> tuple[bool, float]:
        gt_start = gt_entity["start"]
        gt_end = gt_entity["end"]
        pred_start = pred_entity.character_start
        pred_end = pred_entity.character_end

        char_overlap = self.calculate_overlap(gt_start, gt_end, pred_start, pred_end)

        gt_text = gt_entity.get(
            "text", paragraph_text[gt_start:gt_end] if gt_start >= 0 and gt_end <= len(paragraph_text) else ""
        )
        pred_text = pred_entity.text

        token_overlap = self.calculate_token_overlap(gt_text, pred_text)

        text_similarity = self.calculate_text_similarity(gt_text, pred_text)

        is_match = (
            char_overlap >= self.overlap_threshold
            or (token_overlap >= 0.5 and text_similarity >= self.text_similarity_threshold)
            or text_similarity >= 0.9
        )

        match_score = max(char_overlap, (token_overlap + text_similarity) / 2, text_similarity)

        return is_match, match_score

    def evaluate_paragraph(self, paragraph: Dict, predicted_entities: List[ExtractedEntity]) -> Dict:
        ground_truth = paragraph["entities"]
        paragraph_text = paragraph["text"]

        matched_gt = set()
        matched_pred = set()

        match_details = {
            "matched_predictions": [],
            "false_positives": [],
            "false_negatives": [],
        }

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

            best_match_gt_indices = []
            best_match_score = 0.0

            for j, gt_entity in enumerate(ground_truth):
                gt_type = gt_entity["type"]

                if gt_type != pred_type:
                    continue

                is_match, match_score = self.is_entity_match(gt_entity, pred_entity, paragraph_text)

                if is_match and match_score > best_match_score:
                    best_match_score = match_score
                    best_match_gt_indices = []
                    for k, gt_e in enumerate(ground_truth):
                        if gt_e["type"] == pred_type:
                            text_sim = self.calculate_text_similarity(pred_entity.text, gt_e["text"])
                            if text_sim >= 0.8:
                                best_match_gt_indices.append(k)

            if best_match_gt_indices:
                matched_gt_entities = [ground_truth[idx] for idx in best_match_gt_indices]
                match_details["matched_predictions"].append(
                    {
                        "prediction": pred_entity,
                        "matched_ground_truth": matched_gt_entities,
                        "match_score": best_match_score,
                        "num_matches": len(best_match_gt_indices),
                    }
                )

                for idx in best_match_gt_indices:
                    if idx not in matched_gt:
                        matched_gt.add(idx)
                        self.results[pred_type]["true_positives"] += 1
                matched_pred.add(i)
            else:
                match_details["false_positives"].append(pred_entity)
                self.results[pred_type]["false_positives"] += 1

        for j, gt_entity in enumerate(ground_truth):
            if j not in matched_gt:
                match_details["false_negatives"].append(gt_entity)
                self.results[gt_entity["type"]]["false_negatives"] += 1

        return match_details

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

    def print_results(self, extractor_name: str = "NER SERVICE", elapsed_time: float = None):
        metrics = self.calculate_metrics()

        print("\n" + "=" * 80)
        print(f"{extractor_name} BENCHMARK RESULTS")
        print("=" * 80)
        print("\nDataset: OntoNotes 5.0 (CoNLL-2012)")
        print("Target: 10 entities per type")
        print(f"Entity types: {', '.join(TARGET_ENTITIES)}")
        print("\nEvaluation Method: Fuzzy Matching")
        print(f"  - Character overlap threshold: {self.overlap_threshold:.0%}")
        print(f"  - Text similarity threshold: {self.text_similarity_threshold:.0%}")
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

        if elapsed_time is not None:
            print("-" * 80)
            print(f"Total time: {elapsed_time:.2f} seconds")

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
