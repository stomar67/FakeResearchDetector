import re
from typing import Optional

import pymupdf

from .schemas import DocumentMetadata


DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def _extract_year(doc: pymupdf.Document) -> Optional[int]:
    """Prefer explicit publication/copyright year over PDF file timestamps."""
    first_page_text = ""
    if len(doc) > 0:
        first_page_text = doc[0].get_text("text") or ""

    explicit_patterns = [
        r"©\s*(19|20)\d{2}",
        r"\b(?:published|publication|proceedings|conference)\b[^\n]{0,80}"
        r"\b((?:19|20)\d{2})\b",
    ]

    for pattern in explicit_patterns:
        match = re.search(pattern, first_page_text, re.IGNORECASE)
        if match:
            year_match = re.search(r"(19|20)\d{2}", match.group(0))
            if year_match:
                return int(year_match.group(0))

    raw = doc.metadata or {}
    for key in ("creationDate", "modDate"):
        date = raw.get(key) or ""
        match = YEAR_RE.search(date)
        if match:
            return int(match.group(0))

    return None


def extract_metadata(doc: pymupdf.Document) -> DocumentMetadata:
    raw = doc.metadata or {}
    title = (raw.get("title") or "").strip()
    author_raw = (raw.get("author") or "").strip()

    authors = []
    if author_raw:
        authors = [
            a.strip()
            for a in re.split(r";|,\s+(?=[A-Z])", author_raw)
            if a.strip()
        ]

    doi = None
    for page in doc:
        text = page.get_text("text") or ""
        match = DOI_RE.search(text)
        if match:
            doi = match.group(0).rstrip(".,;)")
            break

    return DocumentMetadata(
        title=title,
        authors=authors,
        year=_extract_year(doc),
        doi=doi,
    )
