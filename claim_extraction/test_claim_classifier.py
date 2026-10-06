from claim_extraction.claim_classifier import (
    CLAIM_TYPES,
    classify_candidate_claim,
)
from claim_extraction.claim_extractor import CandidateClaim


def make_candidate(
    text: str,
    signals: list[str],
) -> CandidateClaim:
    return CandidateClaim(
        candidate_id="CAND0001",
        sentence_id="S0001",
        page=1,
        section="Results",
        claim_text=text,
        signals=signals,
    )


def test_statistical_classification():
    candidate = make_candidate(
        "The difference was statistically significant.",
        ["result_language", "statistical_language"],
    )

    result = classify_candidate_claim(candidate)

    assert result.claim_type == "STATISTICAL"
    assert result.candidate_id == "CAND0001"


def test_comparison_classification():
    candidate = make_candidate(
        "Our method outperformed the baseline.",
        ["result_language", "comparison_language"],
    )

    result = classify_candidate_claim(candidate)

    assert result.claim_type == "COMPARISON"


def test_result_classification():
    candidate = make_candidate(
        "The proposed method achieved 91.2% accuracy.",
        ["result_language"],
    )

    result = classify_candidate_claim(candidate)

    assert result.claim_type == "RESULT"


def test_method_classification():
    candidate = make_candidate(
        "We propose a new method.",
        ["method_language"],
    )

    result = classify_candidate_claim(candidate)

    assert result.claim_type == "METHOD"


def test_dataset_classification():
    candidate = make_candidate(
        "We collected a new dataset.",
        ["dataset_language"],
    )

    result = classify_candidate_claim(candidate)

    assert result.claim_type == "DATASET"


def test_conclusion_classification():
    candidate = make_candidate(
        "Therefore, the findings suggest improved generalization.",
        ["conclusion_language"],
    )

    result = classify_candidate_claim(candidate)

    assert result.claim_type == "CONCLUSION"


def test_other_classification():
    candidate = make_candidate(
        "This statement contains no recognized claim signal.",
        [],
    )

    result = classify_candidate_claim(candidate)

    assert result.claim_type == "OTHER"


def test_claim_types_are_frozen():
    assert set(CLAIM_TYPES) == {
        "RESULT",
        "COMPARISON",
        "METHOD",
        "DATASET",
        "STATISTICAL",
        "CONCLUSION",
        "OTHER",
    }