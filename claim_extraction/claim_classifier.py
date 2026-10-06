"""
Phase 1 — Scientific Claim Classification

Purpose:
    Assign a preliminary scientific claim type to a CandidateClaim.

This is a transparent Phase 1 baseline.

Frozen claim types:
    RESULT
    COMPARISON
    METHOD
    DATASET
    STATISTICAL
    CONCLUSION
    OTHER

Important:
    This module produces a PREDICTED claim type.
    Human-validated gold annotations remain authoritative.

It does NOT:
    - verify claims
    - verify citations
    - retrieve evidence
    - determine whether a paper is fake
    - assign risk scores
    - modify gold-standard annotations

The rule-based classifier is a Phase 1 baseline.
It is intentionally replaceable by a future learned classifier
without changing the downstream interface.
"""

from dataclasses import dataclass

from .claim_extractor import CandidateClaim


CLAIM_TYPES = (
    "RESULT",
    "COMPARISON",
    "METHOD",
    "DATASET",
    "STATISTICAL",
    "CONCLUSION",
    "OTHER",
)


@dataclass
class ClaimTypePrediction:
    """Predicted type for one candidate claim."""

    candidate_id: str
    claim_type: str
    signals_used: list[str]


def classify_candidate_claim(
    candidate: CandidateClaim,
) -> ClaimTypePrediction:
    """
    Assign a preliminary claim type using existing candidate signals.

    Priority is deliberately explicit and deterministic.

    Statistical language is checked first because statistical claims
    often contain result/comparison terminology as well.

    Comparison language is checked before generic result language
    because comparisons frequently contain result terminology.

    Method and dataset signals are then considered.

    Conclusion language is considered before the OTHER fallback.

    Human validation remains authoritative.
    """

    signals = set(candidate.signals)

    if "statistical_language" in signals:
        claim_type = "STATISTICAL"

    elif "comparison_language" in signals:
        claim_type = "COMPARISON"

    elif "result_language" in signals:
        claim_type = "RESULT"

    elif "method_language" in signals:
        claim_type = "METHOD"

    elif "dataset_language" in signals:
        claim_type = "DATASET"

    elif "conclusion_language" in signals:
        claim_type = "CONCLUSION"

    else:
        claim_type = "OTHER"

    return ClaimTypePrediction(
        candidate_id=candidate.candidate_id,
        claim_type=claim_type,
        signals_used=list(candidate.signals),
    )


def classify_candidate_claims(
    candidates: list[CandidateClaim],
) -> list[ClaimTypePrediction]:
    """
    Classify a list of candidate claims.
    """

    return [
        classify_candidate_claim(candidate)
        for candidate in candidates
    ]