import re
from typing import List, Set

from .schemas import InTextCitation, Page


NUMERIC_GROUP_RE = re.compile(
    r"\[((?:\d+\s*[-–]\s*\d+|\d+)"
    r"(?:\s*[,;]\s*(?:\d+\s*[-–]\s*\d+|\d+))*)\]"
)

# Parenthetical citations:
# (Beck, 2008), (Clark and Beck, 2010), (Wang et al., 2023b),
# (Smith, 2020; Jones, 2021)
AUTHOR_YEAR_GROUP_RE = re.compile(
    r"\(([A-Z][^()]*?\b(?:19|20)\d{2}[a-z]?[^()]*)\)"
)

# Narrative citations:
# Beck (2008), Wang et al. (2023), Clark and Beck (2010)
NARRATIVE_AUTHOR_YEAR_RE = re.compile(
    r"\b([A-Z][A-Za-z'’.-]+"
    r"(?:\s+(?:and|&)\s+[A-Z][A-Za-z'’.-]+"
    r"|\s+et\s+al\.)?)"
    r"\s*\((\d{4}[a-z]?)\)"
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


def _context(text: str, start: int, end: int, radius: int = 100) -> str:
    return text[max(0, start - radius): min(len(text), end + radius)].strip()


def extract_in_text_citations(pages: List[Page]) -> List[InTextCitation]:
    results: List[InTextCitation] = []

    for page in pages:
        text = page.text

        for match in NUMERIC_GROUP_RE.finditer(text):
            results.append(
                InTextCitation(
                    citation_text=match.group(0),
                    citation_type="numeric",
                    reference_ids=_expand_numeric(match.group(1)),
                    page_number=page.page_number,
                    text=_context(text, match.start(), match.end()),
                )
            )

        # Parenthetical author-year citations. IDs remain empty in Phase 1;
        # matching them to bibliography entries is a later verification task.
        for match in AUTHOR_YEAR_GROUP_RE.finditer(text):
            results.append(
                InTextCitation(
                    citation_text=match.group(0),
                    citation_type="author_year",
                    reference_ids=[],
                    page_number=page.page_number,
                    text=_context(text, match.start(), match.end()),
                )
            )

        # Narrative form, e.g. Beck (2008). Avoid duplicating the same
        # occurrence already captured inside a parenthetical match.
        for match in NARRATIVE_AUTHOR_YEAR_RE.finditer(text):
            citation_text = match.group(0)
            if any(
                existing.page_number == page.page_number
                and existing.citation_text == citation_text
                for existing in results
            ):
                continue

            results.append(
                InTextCitation(
                    citation_text=citation_text,
                    citation_type="author_year",
                    reference_ids=[],
                    page_number=page.page_number,
                    text=_context(text, match.start(), match.end()),
                )
            )

    return results
