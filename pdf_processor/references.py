import re
from typing import List, Optional, Tuple

from .schemas import Reference


REFERENCE_START_RE = re.compile(r"^\s*references\s*$", re.IGNORECASE)

# Only treat bracketed numbers as numbered bibliography entries.
NUMERIC_REFERENCE_RE = re.compile(r"^\s*\[(\d+)\]\s*(.*)$")

# Standalone page-number/footer artifacts frequently appear in extracted PDFs.
PAGE_ARTIFACT_RE = re.compile(r"^\s*\d{4,6}\s*$")

# Conservative author-year reference start:
# - must begin with an uppercase letter or an organization-style token
# - a 4-digit year must be followed by a period
# - rejects lines beginning with lowercase continuation text
AUTHOR_YEAR_REFERENCE_RE = re.compile(
    r"^\s*(?P<authors>[A-Z][^\n]*?)\s+"
    r"(?P<year>(?:19|20)\d{2}[a-z]?)\.\s*(?P<rest>.*)$"
)

# Common continuation prefixes. These should never start a new bibliography item.
CONTINUATION_PREFIX_RE = re.compile(
    r"^(?:and|or|but|for|with|from|in|on|of|to|the|a|an|moyer|et al\.)\b",
    re.IGNORECASE,
)


def _is_author_year_start(line: str) -> Optional[Tuple[str, str, str]]:
    """Return authors/year/rest only for plausible new author-year entries."""
    if not line or PAGE_ARTIFACT_RE.fullmatch(line):
        return None

    if CONTINUATION_PREFIX_RE.match(line):
        return None

    match = AUTHOR_YEAR_REFERENCE_RE.match(line)
    if not match:
        return None

    authors = match.group("authors").strip(" ,.").strip()
    year = match.group("year").strip()
    rest = match.group("rest").strip()

    # Avoid treating ordinary prose containing a year as a reference.
    if len(authors) < 2:
        return None

    return authors, year, rest


def extract_references(pages) -> List[Reference]:
    """
    Extract bibliography entries from the References section.

    Phase 1:
    - numbered references such as [1] ...
    - unnumbered author-year references
    - multi-line reference preservation
    - page provenance
    - page-number footer filtering
    - no semantic citation verification
    """

    references: List[Reference] = []
    in_references = False
    current_reference: Optional[str] = None
    current_text: List[str] = []
    current_page: Optional[int] = None

    def flush_current() -> None:
        nonlocal current_reference, current_text, current_page

        if current_reference is not None and current_text:
            references.append(
                Reference(
                    reference_id=current_reference,
                    text=" ".join(current_text).strip(),
                    page_number=current_page,
                )
            )

        current_reference = None
        current_text = []
        current_page = None

    for page in pages:
        for raw_line in page.text.splitlines():
            cleaned = " ".join(raw_line.split())

            if not cleaned:
                continue

            if REFERENCE_START_RE.fullmatch(cleaned):
                flush_current()
                in_references = True
                continue

            if not in_references:
                continue

            # Ignore standalone PDF page-number artifacts.
            if PAGE_ARTIFACT_RE.fullmatch(cleaned):
                continue

            numeric_match = NUMERIC_REFERENCE_RE.match(cleaned)
            if numeric_match:
                flush_current()
                number = numeric_match.group(1)
                first_text = numeric_match.group(2).strip()

                current_reference = f"[{number}]"
                current_text = [first_text] if first_text else []
                current_page = page.page_number
                continue

            author_year = _is_author_year_start(cleaned)
            if author_year:
                flush_current()
                authors, year, _ = author_year

                current_reference = f"{authors} {year}"
                current_text = [cleaned]
                current_page = page.page_number
                continue

            if current_reference is not None:
                current_text.append(cleaned)

    flush_current()
    return references
