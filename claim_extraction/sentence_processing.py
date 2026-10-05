"""
Phase 1 — Sentence and Section Processing

Purpose:
    Convert Kunjum's StructuredDocument output into structured sentences
    while preserving exact source text, section, and page provenance.

This module does NOT:
    - extract scientific claims
    - classify claims
    - verify citations
    - retrieve evidence
    - score claims
"""

from dataclasses import dataclass
import re

from pdf_processor.schemas import StructuredDocument


@dataclass
class SentenceRecord:
    """Structured sentence used by downstream Phase 1 components."""

    sentence_id: str
    page: int | None
    section: str
    text: str


def normalize_pdf_artifacts(text: str) -> str:
    """
    Normalize only unavoidable PDF extraction artifacts.

    This normalized form is used for matching/location purposes.
    It is NOT used as the stored source text.
    """

    # Rejoin words split across PDF line breaks.
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

    # Convert remaining line breaks to spaces.
    text = re.sub(r"\s*\n\s*", " ", text)

    # Collapse repeated whitespace.
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def _is_structural_noise(sentence: str) -> bool:
    """
    Identify only obvious non-sentence structural artifacts.

    This intentionally uses conservative rules so that scientific
    source wording is not silently removed or rewritten.
    """

    stripped = sentence.strip()

    if not stripped:
        return True

    # Standalone page numbers accidentally included in section text.
    if re.fullmatch(r"\d+", stripped):
        return True

    return False


def split_sentences(text: str) -> list[str]:
    """
    Split text into candidate sentence units.

    This is preprocessing only.
    It is not the final scientific-claim boundary decision.
    """

    text = normalize_pdf_artifacts(text)

    if not text:
        return []

    parts = re.split(
        r"(?<=[.!?])\s+(?=[A-Z0-9])",
        text,
    )

    return [
        part.strip()
        for part in parts
        if part.strip() and not _is_structural_noise(part)
    ]


def _normalized_for_matching(text: str) -> str:
    """Create a comparison form without changing stored source text."""

    return normalize_pdf_artifacts(text)


def _find_unique_page(
    sentence: str,
    section,
    pages,
) -> int | None:
    """
    Find the exact page containing a sentence.

    Search is restricted to the section's page range.

    Returns:
        page number if exactly one page matches
        None if no unique page can be established
    """

    sentence_normalized = _normalized_for_matching(sentence)

    if not sentence_normalized:
        return None

    matching_pages = []

    for page in pages:
        if not (
            section.page_start
            <= page.page_number
            <= section.page_end
        ):
            continue

        page_normalized = _normalized_for_matching(page.text)

        if sentence_normalized in page_normalized:
            matching_pages.append(page.page_number)

    if len(matching_pages) == 1:
        return matching_pages[0]

    return None

def process_document(
    document: StructuredDocument,
) -> list[SentenceRecord]:
    """
    Convert Kunjum's StructuredDocument into SentenceRecords.

    Section text is used as the source for sentence segmentation.

    Page numbers are recovered by locating each sentence in the
    original page-level text.

    Sentences that cannot be uniquely mapped to a source page are
    excluded rather than assigned invented provenance.

    The References section is excluded because bibliography entries
    are not substantive scientific claims from the paper body.
    """

    records: list[SentenceRecord] = []
    counter = 1

    for section in document.sections:

        # References are bibliographic entries, not paper claims.
        if section.title.strip().lower() == "references":
            continue

        sentences = split_sentences(section.text)

        for sentence in sentences:

            page = _find_unique_page(
                sentence=sentence,
                section=section,
                pages=document.pages,
            )

            # Do not propagate sentences whose page provenance
            # cannot be established uniquely.
            if page is None:
                continue

            records.append(
                SentenceRecord(
                    sentence_id=f"S{counter:04d}",
                    page=page,
                    section=section.title,
                    text=sentence,
                )
            )

            counter += 1

    return records