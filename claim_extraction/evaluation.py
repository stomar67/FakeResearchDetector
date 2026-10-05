"""
Phase 1 — Gold Standard Evaluation Utilities

This module compares model/baseline candidate claims against
manually validated gold-standard claims.

It does NOT:
    - verify citations
    - retrieve evidence
    - determine truth/fakeness
    - assign risk scores
"""

from dataclasses import dataclass


@dataclass
class EvaluationResult:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


def normalize_for_matching(text: str) -> str:
    """
    Normalize only for evaluation matching.

    This does NOT modify the stored gold-standard claim text.
    """

    return " ".join(text.split()).strip().lower()


def evaluate_candidates(
    gold_claims: list[str],
    predicted_claims: list[str],
) -> EvaluationResult:

    gold = {
        normalize_for_matching(claim)
        for claim in gold_claims
    }

    predicted = {
        normalize_for_matching(claim)
        for claim in predicted_claims
    }

    true_positives = len(gold & predicted)
    false_positives = len(predicted - gold)
    false_negatives = len(gold - predicted)

    precision = (
        true_positives / (true_positives + false_positives)
        if true_positives + false_positives
        else 0.0
    )

    recall = (
        true_positives / (true_positives + false_negatives)
        if true_positives + false_negatives
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return EvaluationResult(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=precision,
        recall=recall,
        f1=f1,
    )