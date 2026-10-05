"""
Phase 1 — Claim Classification Error Analysis

Purpose:
    Inspect classification errors on matched gold/candidate claims.

This module does NOT:
    - modify the classifier
    - modify gold annotations
    - modify candidate extraction
    - perform verification
    - retrieve evidence
"""

from pathlib import Path

from pdf_processor import extract_document

from claim_extraction.sentence_processing import process_document
from claim_extraction.claim_extractor import extract_candidate_claims
from claim_extraction.gold_loader import load_gold_claims
from claim_extraction.classification_evaluation import (
    match_gold_to_candidates,
)
from claim_extraction.claim_classifier import (
    classify_candidate_claim,
)


PAPER_PATHS = {
    "P000": Path(r"DATASET\Data Original\P000_V0_ORIGINAL.pdf"),
    "P007": Path(r"DATASET\Data Original\P007_V0_ORIGINAL.pdf"),
    "P036": Path(r"DATASET\Data Original\P036_V0_ORIGINAL.pdf"),
}


def analyze_paper(paper_id: str):
    document = extract_document(
        str(PAPER_PATHS[paper_id])
    )

    sentences = process_document(document)
    candidates = extract_candidate_claims(sentences)
    gold_claims = load_gold_claims(paper_id)

    matched, _ = match_gold_to_candidates(
        gold_claims=gold_claims,
        candidates=candidates,
    )

    errors = []

    for gold, candidate in matched:
        prediction = classify_candidate_claim(candidate)

        if prediction.claim_type == gold.claim_type:
            continue

        errors.append(
            {
                "gold_type": gold.claim_type,
                "predicted_type": prediction.claim_type,
                "signals": candidate.signals,
                "section": candidate.section,
                "page": candidate.page,
                "claim_text": candidate.claim_text,
            }
        )

    return errors


def print_summary(all_errors):
    print("=" * 90)
    print("PHASE 1 — CLAIM CLASSIFICATION ERROR ANALYSIS")
    print("=" * 90)

    print(f"Total classification errors: {len(all_errors)}")

    by_pair = {}

    for error in all_errors:
        key = (
            error["gold_type"],
            error["predicted_type"],
        )

        by_pair[key] = by_pair.get(key, 0) + 1

    print("\nERRORS BY GOLD → PREDICTED TYPE")
    print("-" * 90)

    for (gold_type, predicted_type), count in sorted(
        by_pair.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        print(
            f"{gold_type:15} → "
            f"{predicted_type:15} : {count}"
        )

    by_signal = {}

    for error in all_errors:
        signal_key = tuple(error["signals"])

        by_signal[signal_key] = (
            by_signal.get(signal_key, 0) + 1
        )

    print("\nERRORS BY SIGNAL COMBINATION")
    print("-" * 90)

    for signals, count in sorted(
        by_signal.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        print(
            f"{list(signals)} : {count}"
        )

    print("\n" + "=" * 90)
    print("DETAILED ERRORS")
    print("=" * 90)

    for index, error in enumerate(all_errors, start=1):
        print("\n" + "-" * 90)
        print(f"ERROR {index}")
        print(
            f"Gold type:      {error['gold_type']}"
        )
        print(
            f"Predicted type: {error['predicted_type']}"
        )
        print(
            f"Page:           {error['page']}"
        )
        print(
            f"Section:        {error['section']}"
        )
        print(
            f"Signals:        {error['signals']}"
        )
        print(
            f"Claim:          {error['claim_text']}"
        )


def main():
    all_errors = []

    for paper_id in PAPER_PATHS:
        errors = analyze_paper(paper_id)

        print(
            f"{paper_id}: {len(errors)} classification errors"
        )

        for error in errors:
            error["paper_id"] = paper_id
            all_errors.append(error)

    print_summary(all_errors)


if __name__ == "__main__":
    main()