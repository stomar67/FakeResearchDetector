import re
from typing import List, Set
from .schemas import InTextCitation, Page

NUMERIC_GROUP_RE = re.compile(r"\[((?:\d+\s*[-–]\s*\d+|\d+)(?:\s*[,;]\s*(?:\d+\s*[-–]\s*\d+|\d+))*)\]")
AUTHOR_YEAR_RE = re.compile(
    r"\(([A-Z][A-Za-z'’-]+(?:\s+et\s+al\.)?(?:\s*(?:,|&|and)\s*[A-Z][A-Za-z'’-]+)*),?\s*(\d{4}[a-z]?)\)"
)


def _expand_numeric(value: str) -> List[str]:
    ids: Set[str] = set()
    for part in re.split(r"\s*[,;]\s*", value):
        if re.fullmatch(r"\d+\s*[-–]\s*\d+", part):
            a, b = re.split(r"\s*[-–]\s*", part)
            start, end = int(a), int(b)
            if end - start <= 50:
                ids.update(str(i) for i in range(start, end + 1))
        elif part.strip().isdigit():
            ids.add(part.strip())
    return sorted(ids, key=int)


def extract_in_text_citations(pages: List[Page]) -> List[InTextCitation]:
    results = []

    for page in pages:
        text = page.text

        for match in NUMERIC_GROUP_RE.finditer(text):
            ids = _expand_numeric(match.group(1))
            results.append(
                InTextCitation(
                    citation_text=match.group(0),
                    citation_type="numeric",
                    reference_ids=ids,
                    page_number=page.page_number,
                    text=text[max(0, match.start()-100): min(len(text), match.end()+100)].strip(),
                )
            )

        for match in AUTHOR_YEAR_RE.finditer(text):
            results.append(
                InTextCitation(
                    citation_text=match.group(0),
                    citation_type="author_year",
                    reference_ids=[],
                    page_number=page.page_number,
                    text=text[max(0, match.start()-100): min(len(text), match.end()+100)].strip(),
                )
            )

    return results
