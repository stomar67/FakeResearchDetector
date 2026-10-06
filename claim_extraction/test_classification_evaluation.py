from claim_extraction.classification_evaluation import (
    evaluate_classification,
    normalize_claim_text,
)
from claim_extraction.claim_extractor import CandidateClaim
from claim_extraction.gold_loader import GoldClaim


def make_gold(
    claim_id: str,
    text: str,
    claim_type: str,
) -> GoldClaim:
    return GoldClaim(
        paper_id="PTEST",
        claim_id=claim_id,
        claim_text=text,
        page=1,
        section="Results",
        claim_type=claim_type,
        citation_ids="",
        is_checkable=True,
        notes="",
    )


def make_candidate(
    candidate_id: str,
    text: str,
    signals: list[str],
) -> CandidateClaim:
    return CandidateClaim(
        candidate_id=candidate_id,
        sentence_id="S0001",
        page=1,
        section="Results",
        claim_text=text,
        signals=signals,
    )


def test_normalize_claim_text():
    assert normalize_claim_text(
        "The model achieved\n91.2% accuracy."
    ) == "The model achieved 91.2% accuracy."


def test_matching_and_correct_classification():
    gold = [
        make_gold(
            "PTEST-C001",
            "The model achieved 91.2% accuracy.",
            "RESULT",
        )
    ]

    candidates = [
        make_candidate(
            "CAND0001",
            "The model achieved 91.2% accuracy.",
            ["result_language"],
        )
    ]

    result = evaluate_classification(
        gold_claims=gold,
        candidates=candidates,
    )

    assert result.total_gold_claims == 1
    assert result.matched_claims == 1
    assert result.unmatched_gold_claims == 0
    assert result.correct == 1
    assert result.incorrect == 0
    assert result.accuracy == 1.0


def test_incorrect_classification_is_counted():
    gold = [
        make_gold(
            "PTEST-C001",
            "Our method outperformed the baseline.",
            "RESULT",
        )
    ]

    candidates = [
        make_candidate(
            "CAND0001",
            "Our method outperformed the baseline.",
            ["result_language", "comparison_language"],
        )
    ]

    result = evaluate_classification(
        gold_claims=gold,
        candidates=candidates,
    )

    assert result.matched_claims == 1
    assert result.correct == 0
    assert result.incorrect == 1
    assert result.accuracy == 0.0

    assert result.confusion_matrix["RESULT"]["COMPARISON"] == 1


def test_unmatched_gold_claim_is_not_classification_error():
    gold = [
        make_gold(
            "PTEST-C001",
            "This claim is missing from candidates.",
            "METHOD",
        )
    ]

    candidates = []

    result = evaluate_classification(
        gold_claims=gold,
        candidates=candidates,
    )

    assert result.total_gold_claims == 1
    assert result.matched_claims == 0
    assert result.unmatched_gold_claims == 1
    assert result.correct == 0
    assert result.incorrect == 0
    assert result.accuracy == 0.0


def test_multiple_claims_and_confusion_matrix():
    gold = [
        make_gold(
            "PTEST-C001",
            "The model achieved 91.2% accuracy.",
            "RESULT",
        ),
        make_gold(
            "PTEST-C002",
            "We collected a new dataset.",
            "DATASET",
        ),
    ]

    candidates = [
        make_candidate(
            "CAND0001",
            "The model achieved 91.2% accuracy.",
            ["result_language"],
        ),
        make_candidate(
            "CAND0002",
            "We collected a new dataset.",
            ["dataset_language"],
        ),
    ]

    result = evaluate_classification(
        gold_claims=gold,
        candidates=candidates,
    )

    assert result.matched_claims == 2
    assert result.correct == 2
    assert result.incorrect == 0
    assert result.accuracy == 1.0

    assert result.confusion_matrix["RESULT"]["RESULT"] == 1
    assert result.confusion_matrix["DATASET"]["DATASET"] == 1