"""
Phase 1 — Claim–Citation Association

Purpose:
    Associate candidate scientific claims with citations that are
    explicitly present inside the candidate sentence.

Important:
    This module performs citation association only.

It does NOT:
    - determine whether a citation supports a claim
    - retrieve external evidence
    - verify citation correctness
    - score claims
    - determine whether a paper is fake
    - perform semantic citation verification
"""

from dataclasses import dataclass
import re

from pdf_processor.schemas import StructuredDocument
from .claim_extractor import CandidateClaim


@dataclass
class ClaimCitationAssociation:
    """Citation explicitly associated with a candidate claim."""

    candidate_id: str
    citation_text: str
    page: int | None
    association_method: str


def normalize_citation_for_matching(text: str) -> str:
    """
    Normalize only PDF extraction artifacts for comparison.

    The original citation text is preserved separately.
    """

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _citation_variants(citation_text: str) -> set[str]:
    """
    Generate conservative matching variants for one citation.

    This handles PDF line-break artifacts without changing the
    authoritative citation text.
    """

    normalized = normalize_citation_for_matching(citation_text)

    variants = {normalized}

    # Remove whitespace immediately inside citation parentheses.
    variants.add(
        re.sub(r"\(\s+", "(", normalized)
    )

    variants.add(
        re.sub(r"\s+\)", ")", normalized)
    )

    return {
        variant.strip()
        for variant in variants
        if variant.strip()
    }


def associate_candidate_citations(
    candidate: CandidateClaim,
    document: StructuredDocument,
) -> list[ClaimCitationAssociation]:
    """
    Associate citations explicitly occurring inside a candidate sentence.

    Only citation text that can be found inside the candidate sentence
    after conservative PDF-artifact normalization is associated.

    No semantic support decision is made.
    """

    candidate_text = normalize_citation_for_matching(
        candidate.claim_text
    )

    if not candidate_text:
        return []

    associations: list[ClaimCitationAssociation] = []
    seen: set[str] = set()

    for citation in document.in_text_citations:

        citation_variants = _citation_variants(
            citation.citation_text
        )

        matched_variant = None

        for variant in citation_variants:
            if variant and variant in candidate_text:
                matched_variant = variant
                break

        if matched_variant is None:
            continue

        # Deduplicate equivalent citation strings.
        dedup_key = matched_variant.lower()

        if dedup_key in seen:
            continue

        seen.add(dedup_key)

        associations.append(
            ClaimCitationAssociation(
                candidate_id=candidate.candidate_id,
                citation_text=citation.citation_text,
                page=citation.page_number,
                association_method="explicit_in_sentence",
            )
        )

    return associations


def associate_candidate_citations_batch(
    candidates: list[CandidateClaim],
    document: StructuredDocument,
) -> list[ClaimCitationAssociation]:
    """
    Associate citations for all candidate claims in a document.
    """

    associations: list[ClaimCitationAssociation] = []

    for candidate in candidates:
        associations.extend(
            associate_candidate_citations(
                candidate=candidate,
                document=document,
            )
        )

    return associations