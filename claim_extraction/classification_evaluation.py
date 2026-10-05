"""
Phase 1 — Claim Classification Evaluation

Purpose:
    Evaluate predicted claim types against manually validated
    Phase 1 gold-standard annotations.

Important:
    Claim extraction and claim classification are evaluated separately.

    A gold claim is matched to a candidate only when their normalized
    source text matches exactly.

    Unmatched gold claims are reported separately and are NOT treated
    as classification errors.

This module does NOT:
    - modify gold annotations
    - modify candidate extraction
    - modify claim classification
    - verify citations
    - retrieve evidence
"""

from dataclasses import dataclass
import re

from .claim_classifier import (
    ClaimTypePrediction,
    classify_candidate_claims,
)
from .claim_extractor import CandidateClaim
from .gold_loader import GoldClaim


@dataclass
class ClassificationEvaluation:
    total_gold_claims: int
    matched_claims: int
    unmatched_gold_claims: int
    correct: int
    incorrect: int
    accuracy: float
    confusion_matrix: dict[str, dict[str, int]]


def normalize_claim_text(text: str) -> str:
    """
    Normalize only unavoidable PDF/source formatting differences.

    This is used for matching, not for changing stored source text.
    """

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def match_gold_to_candidates(
    gold_claims: list[GoldClaim],
    candidates: list[CandidateClaim],
) -> tuple[
    list[tuple[GoldClaim, CandidateClaim]],
    list[GoldClaim],
]:
    """
    Match gold claims to candidate claims by normalized exact text.

    Each candidate is used at most once.
    """

    candidate_by_text: dict[str, list[CandidateClaim]] = {}

    for candidate in candidates:
        normalized = normalize_claim_text(
            candidate.claim_text
        )

        candidate_by_text.setdefault(
            normalized,
            [],
        ).append(candidate)

    matched = []
    unmatched = []

    used_candidate_ids: set[str] = set()

    for gold in gold_claims:
        normalized = normalize_claim_text(
            gold.claim_text
        )

        possible_candidates = candidate_by_text.get(
            normalized,
            [],
        )

        candidate = None

        for possible in possible_candidates:
            if possible.candidate_id not in used_candidate_ids:
                candidate = possible
                break

        if candidate is None:
            unmatched.append(gold)
            continue

        used_candidate_ids.add(candidate.candidate_id)

        matched.append((gold, candidate))

    return matched, unmatched


def evaluate_classification(
    gold_claims: list[GoldClaim],
    candidates: list[CandidateClaim],
) -> ClassificationEvaluation:
    """
    Evaluate claim-type predictions for matched gold/candidate pairs.
    """

    matched, unmatched = match_gold_to_candidates(
        gold_claims=gold_claims,
        candidates=candidates,
    )

    predictions = classify_candidate_claims(
        [candidate for _, candidate in matched]
    )

    prediction_by_candidate_id = {
        prediction.candidate_id: prediction
        for prediction in predictions
    }

    correct = 0
    incorrect = 0

    confusion_matrix: dict[str, dict[str, int]] = {}

    for gold, candidate in matched:
        prediction = prediction_by_candidate_id[
            candidate.candidate_id
        ]

        gold_type = gold.claim_type
        predicted_type = prediction.claim_type

        confusion_matrix.setdefault(
            gold_type,
            {},
        )

        confusion_matrix[gold_type][predicted_type] = (
            confusion_matrix[gold_type].get(predicted_type, 0) + 1
        )

        if gold_type == predicted_type:
            correct += 1
        else:
            incorrect += 1

    accuracy = (
        correct / len(matched)
        if matched
        else 0.0
    )

    return ClassificationEvaluation(
        total_gold_claims=len(gold_claims),
        matched_claims=len(matched),
        unmatched_gold_claims=len(unmatched),
        correct=correct,
        incorrect=incorrect,
        accuracy=accuracy,
        confusion_matrix=confusion_matrix,
    )