import re
from typing import Optional

import fitz

from .schemas import DocumentMetadata


DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)


def extract_metadata(doc: fitz.Document) -> DocumentMetadata:
    raw = doc.metadata or {}
    title = (raw.get("title") or "").strip()
    author_raw = (raw.get("author") or "").strip()

    authors = []
    if author_raw:
        authors = [a.strip() for a in re.split(r";|,\s+(?=[A-Z])", author_raw) if a.strip()]

    year: Optional[int] = None
    date = (raw.get("creationDate") or raw.get("modDate") or "")
    match = re.search(r"(19|20)\d{2}", date)
    if match:
        year = int(match.group(0))

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
        year=year,
        doi=doi,
    )
