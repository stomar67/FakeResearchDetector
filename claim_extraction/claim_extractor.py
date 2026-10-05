"""
Phase 1 — Candidate Scientific Claim Extraction

Purpose:
    Identify sentences that are potential checkable scientific claims.

Important:
    This module produces CANDIDATES.
    It does not make final annotation decisions.

It does NOT:
    - verify claims
    - verify citations
    - retrieve evidence
    - determine whether a paper is fake
    - assign risk scores
"""

from dataclasses import dataclass
import re

from .sentence_processing import SentenceRecord


@dataclass
class CandidateClaim:
    """A sentence proposed as a candidate scientific claim."""

    candidate_id: str
    sentence_id: str
    page: int
    section: str
    claim_text: str
    signals: list[str]


CLAIM_SIGNAL_PATTERNS = {
    "result_language": re.compile(
        r"\b("
        r"achieved|obtained|resulted|result|results|"
        r"found|findings|showed|shows|demonstrated|"
        r"improved|improvement|outperformed|"
        r"accuracy|precision|recall|f1|f1-score|"
        r"significant|significantly"
        r")\b",
        re.IGNORECASE,
    ),
    "comparison_language": re.compile(
        r"\b("
        r"better|worse|higher|lower|greater|less|"
        r"compared|comparison|outperform|superior|inferior|"
        r"than|versus|vs\."
        r")\b",
        re.IGNORECASE,
    ),
    "method_language": re.compile(
        r"\b("
        r"method|model|algorithm|approach|framework|"
        r"propose|proposed|architecture|technique|"
        r"trained|training|implemented|"
        r"uses|used|consists"
        r")\b",
        re.IGNORECASE,
    ),
    "dataset_language": re.compile(
        r"\b("
        r"dataset|data set|corpus|samples|instances|"
        r"participants|subjects|benchmark|collection"
        r")\b",
        re.IGNORECASE,
    ),
    "statistical_language": re.compile(
        r"\b("
        r"p\s*[<>=]|"
        r"p-value|"
        r"confidence interval|"
        r"standard deviation|"
        r"mean|median|variance|"
        r"correlation|regression|"
        r"statistically"
        r")\b",
        re.IGNORECASE,
    ),
    "conclusion_language": re.compile(
        r"\b("
        r"therefore|thus|hence|"
        r"we conclude|"
        r"we demonstrate|"
        r"we hypothesize|"
        r"indicate|indicates|"
        r"suggest|suggests|"
        r"conclusion"
        r")\b",
        re.IGNORECASE,
    ),
}


def detect_claim_signals(sentence: str) -> list[str]:
    """
    Return the scientific-claim signals detected in a sentence.
    """

    signals = []

    for signal_name, pattern in CLAIM_SIGNAL_PATTERNS.items():
        if pattern.search(sentence):
            signals.append(signal_name)

    return signals


def is_candidate_claim(sentence: str) -> bool:
    """
    Decide whether a sentence should be proposed as a candidate claim.

    This is intentionally permissive. Human validation remains the
    authoritative Phase 1 step.
    """

    signals = detect_claim_signals(sentence)

    return len(signals) >= 1


def extract_candidate_claims(
    sentences: list[SentenceRecord],
) -> list[CandidateClaim]:
    """
    Generate candidate claims from structured sentence records.
    """

    candidates: list[CandidateClaim] = []
    counter = 1

    for sentence in sentences:
        signals = detect_claim_signals(sentence.text)

        if not signals:
            continue

        candidates.append(
            CandidateClaim(
                candidate_id=f"CAND{counter:04d}",
                sentence_id=sentence.sentence_id,
                page=sentence.page,
                section=sentence.section,
                claim_text=sentence.text,
                signals=signals,
            )
        )

        counter += 1

    return candidates