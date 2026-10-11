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


def _is_likely_non_citation_group(group: str) -> bool:
    """Reject known funding and venue patterns mistaken for author-year citations."""
    value = re.sub(r"\s+", " ", group.strip())

    # Example: (Grant Nos. 2042022kf1218, 2042022kf1037)
    if re.match(
        r"^(?:grant|funding)\s+(?:nos?\.?|numbers?)(?:\s|$)",
        value,
        flags=re.IGNORECASE,
    ):
        return True

    # Example: (LREC-COLING 2024)
    # Reject acronym-style venue names followed directly by a year.
    if re.fullmatch(
        r"[A-Z][A-Z0-9]*(?:-[A-Z][A-Z0-9]*)+\s+(?:19|20)\d{2}[a-z]?",
        value,
    ):
        return True

    return False


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
            if _is_likely_non_citation_group(match.group(1)):
                continue

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





def match_citations_to_references(citations, references):
    """Conservatively match author-year citations to bibliography entries."""
    import re
    import unicodedata

    year_pattern = re.compile(r"\b((?:19|20)\d{2}[a-z]?)\b", re.I)
    word_pattern = re.compile(r"[^\W\d_][\w'-]*", re.UNICODE)

    def normalize(value):
        value = unicodedata.normalize("NFKD", value or "")
        value = "".join(
            ch for ch in value if not unicodedata.combining(ch)
        )
        value = value.replace("\u00ad", "")
        value = value.replace("’", "'").replace("–", "-").replace("—", "-")
        value = re.sub(r"(?<=\w)-\s+(?=\w)", "-", value)
        return re.sub(r"\s+", " ", value).strip()

    def surname_key(author_text):
        author_text = normalize(author_text).strip(" ,.;()")
        author_text = re.sub(
            r"\bet\s+al\.?$", "", author_text, flags=re.I
        ).strip()

        # "Beck, A. T." -> Beck
        # "Aaron T Beck" -> Beck
        # "Clark and Beck" -> Beck
        if "," in author_text:
            first = author_text.split(",", 1)[0].strip()
            words = word_pattern.findall(first)
        else:
            words = word_pattern.findall(author_text)
            words = [
                word for word in words
                if word.casefold() not in {"and", "et", "al"}
            ]

        return words[-1].casefold() if words else ""

    def citation_parts(citation_text):
        text = normalize(citation_text).strip().strip("()")
        result = []

        for part in re.split(r"\s*;\s*", text):
            year_match = year_pattern.search(part)
            if not year_match:
                continue

            surname = surname_key(part[:year_match.start()])
            year = year_match.group(1).casefold()

            if surname:
                result.append((surname, year))

        return result

    def reference_parts(reference):
        identifier = normalize(reference.reference_id)
        text = (
            identifier
            if year_pattern.search(identifier)
            else normalize(reference.text)
        )

        year_match = year_pattern.search(text)
        if not year_match:
            return "", ""

        surname = surname_key(text[:year_match.start()])
        return surname, year_match.group(1).casefold()

    reference_index = {}
    for reference in references:
        surname, year = reference_parts(reference)
        if surname and year:
            reference_index.setdefault((surname, year), []).append(
                reference.reference_id
            )

    matched_citations = []

    for citation in citations:
        result = citation.model_copy(deep=True)

        # Preserve numeric citation IDs exactly as extracted.
        if citation.citation_type != "author_year":
            matched_citations.append(result)
            continue

        matched_ids = []
        for surname, year in citation_parts(citation.citation_text):
            candidates = reference_index.get((surname, year), [])

            # Do not guess when multiple references share a surname and year.
            if len(candidates) == 1 and candidates[0] not in matched_ids:
                matched_ids.append(candidates[0])

        result.reference_ids = matched_ids
        matched_citations.append(result)

    return matched_citations
