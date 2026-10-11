
import re
from typing import List, Optional, Tuple

from .schemas import Reference



REFERENCE_START_RE = re.compile(
    r"^\s*(?:references|bibliography|literature cited|works cited)"
    r"(?:\s*:)?\s*$",
    re.IGNORECASE,
)

NUMERIC_REFERENCE_RE = re.compile(
    r"^\s*(?:\[(?P<bracket>\d+)\]|(?P<plain>\d{1,3})[.)])\s*(?P<text>.*)$"
)

PAGE_ARTIFACT_RE = re.compile(r"^\s*\d{4,6}\s*$")
YEAR_PATTERN = r"(?:19|20)\d{2}[a-z]?"

AUTHOR_YEAR_REFERENCE_RE = re.compile(
    rf"^\s*(?P<authors>[A-Z][^\n]*?)\s+"
    rf"(?P<year>{YEAR_PATTERN})\.\s*(?P<rest>.*)$"
)


AUTHOR_YEAR_PAREN_REFERENCE_RE = re.compile(
    rf"^\s*(?P<authors>[A-Z][^\n]*?)\s+"
    rf"\((?P<year>{YEAR_PATTERN})\)[.,]?\s*(?P<rest>.*)$"
)


YEAR_REST_RE = re.compile(
    rf"^\s*(?P<year>{YEAR_PATTERN})\.\s*(?P<rest>.*)$"
)

FRAGMENT_YEAR_RE = re.compile(
    rf"^\s*(?P<authors>.+?)\s+"
    rf"(?P<year>{YEAR_PATTERN})\.\s*(?P<rest>.*)$"
)


def _find_author_year_starts(text: str) -> List[re.Match]:
    """Find likely parenthesized author-year starts in merged reference text."""
    pattern = re.compile(
        rf"(?P<authors>[A-ZÀ-ÖØ-Þ][^()\n]*?)"
        rf"\s+\((?P<year>{YEAR_PATTERN})\)"
        rf"[.,]?\s+"
    )

    matches = []

    for match in pattern.finditer(text):
        authors = match.group("authors").strip(" ,.;")
        if len(authors) < 2 or len(authors) > 180:
            continue

        # Keep the match only when the captured author field does not
        # contain an earlier sentence or title.
        if re.search(r"[.!?]\s+[A-Z]", authors):
            continue

        matches.append(match)

    return matches


def _is_author_year_start(
    line: str,
) -> Optional[Tuple[str, str, str]]:
    if not line or PAGE_ARTIFACT_RE.fullmatch(line):
        return None

    match = AUTHOR_YEAR_REFERENCE_RE.match(line)
    if not match:
        match = AUTHOR_YEAR_PAREN_REFERENCE_RE.match(line)

    if not match:
        return None

    authors = match.group("authors").strip(" ,.")
    year = match.group("year")
    rest = match.group("rest").strip()

    if len(authors) < 2 or not rest:
        return None

    if re.match(
        r"^(?:and|or|but|with|moyer|et al\.?)\b",
        authors,
        re.IGNORECASE,
    ):
        return None

    return authors, year, rest


def _is_probable_author_list_line(line: str) -> bool:
    if not line or PAGE_ARTIFACT_RE.fullmatch(line):
        return False

    if re.search(rf"\b{YEAR_PATTERN}\b", line):
        return False

    if not line[0].isupper():
        return False

    # Multiple comma-separated names, or an author line ending in a comma.
    return line.count(",") >= 3 or (
        line.endswith(",") and line.count(",") >= 2
    )


def _join_author_lines(lines: List[str]) -> str:
    """Join wrapped names and repair PDF line-break hyphenation."""
    text = " ".join(lines)
    text = re.sub(r"(\w)-\s+([a-z])", r"\1\2", text)
    return text.strip()




def _is_reference_heading(lines: List[str], index: int) -> bool:
    """Identify bibliography headings while rejecting table-column labels."""
    line = lines[index].strip()

    if not REFERENCE_START_RE.fullmatch(line):
        return False

    table_labels = {
        "main topic",
        "detection",
        "dataset type",
        "public",
        "real",
        "synthetic",
        "not specified",
        "crop",
        "diseases and pests",
        "method/model of detection",
        "precision (%)",
        "precision",
        "recall (%)",
        "recall",
        "f1 score (%)",
        "f1 score",
    }

    def normalize(value: str) -> str:
        return " ".join(value.split()).casefold()

    # Check the preceding lines as well as the following lines.
    # Table headers commonly place "References" after other column labels.
    preceding = [
        normalize(item)
        for item in lines[max(0, index - 5):index]
        if item.strip()
    ]

    matching_labels = sum(
        item in table_labels for item in preceding
    )

    if matching_labels >= 2:
        return False

    following = [
        " ".join(item.split())
        for item in lines[index + 1:index + 6]
        if item.strip()
    ]

    if not following:
        return False

    # A genuine bibliography should be followed by a plausible entry.
    for item in following:
        if (
            NUMERIC_REFERENCE_RE.match(item)
            or _is_author_year_start(item)
            or re.match(
                r"^[A-ZÀ-ÖØ-Þ][\wÀ-ÖØ-öø-ÿ'’.-]*,",
                item,
            )
        ):
            return True

    return False





def _split_merged_author_year_text(text: str) -> List[Tuple[str, str]]:
    """Split merged parenthesized author-year references."""
    text = re.sub(r"\s+", " ", text).strip()

    # Remove known publisher boilerplate.
    footer = re.search(
        r"\b(?:How to cite this article\s*:|"
        r"Wiley Online Library on\s+\[)",
        text,
        re.IGNORECASE,
    )
    if footer:
        text = text[:footer.start()].rstrip()

    if not text:
        return []

    # Look ahead so a rejected candidate does not prevent finding
    # the next valid author-year start.
    pattern = re.compile(
        rf"(?=(?P<authors>[^\W\d_][^()\n]{{1,179}}?)"
        rf"\s+\((?P<year>{YEAR_PATTERN})\)[.,]?(?=\s))",
        re.UNICODE,
    )

    starts = [0]

    for match in pattern.finditer(text):
        start = match.start()
        authors = match.group("authors").strip(" ,.;")

        if start == 0 or not (2 <= len(authors) <= 180):
            continue

        # A plausible author list normally contains commas, '&',
        # 'and', or 'et al.'.
        if not (
            "," in authors
            or re.search(r"\b(?:and|&|et\s+al\.?)\b", authors, re.I)
        ):
            continue

        # Reject candidates that accidentally include the previous
        # reference's title, such as "First paper title. Viera, ...".
        if re.search(r"[.!?]\s+[A-Z][a-z]", authors):
            continue

        prefix = text[:start].rstrip()

        # A new reference must begin after a sentence/reference boundary.
        if not prefix or prefix[-1] not in ".;":
            continue

        # Avoid splitting at an initial such as "Viera, A. J.".
        if re.search(r"(?:\b[A-Z]\.){1,3}$", prefix):
            continue

        if start > starts[-1]:
            starts.append(start)

    pieces = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        piece = text[start:end].strip()
        if piece:
            pieces.append((piece, ""))

    return pieces




def extract_references(pages) -> List[Reference]:
    """Extract numbered and author-year references from bibliography pages."""
    references: List[Reference] = []
    in_references = False

    current_reference: Optional[str] = None
    current_text: List[str] = []
    current_page: Optional[int] = None

    pending_author_lines: List[Tuple[str, int]] = []
    
    def flush_current() -> None:
        nonlocal current_reference, current_text, current_page

        if current_reference is not None and current_text:
            full_text = " ".join(current_text).strip()

            # Split merged author-year references, but preserve numbered entries.
            if not current_reference.startswith("["):
                pieces = _split_merged_author_year_text(full_text)
            else:
                pieces = [(full_text, "")]

            if len(pieces) <= 1:
                references.append(
                    Reference(
                        reference_id=current_reference,
                        text=full_text,
                        page_number=current_page,
                    )
                )
            else:
                for index, (piece, _) in enumerate(pieces):
                    if index == 0:
                        reference_id = current_reference
                    else:
                        start_match = re.match(
                            rf"(?P<authors>.+?)\s+"
                            rf"(?:\((?P<year1>{YEAR_PATTERN})\)|"
                            rf"(?P<year2>{YEAR_PATTERN})\.)",
                            piece,
                        )

                        if start_match:
                            year = (
                                start_match.group("year1")
                                or start_match.group("year2")
                            )
                            authors = start_match.group("authors").strip(" ,.")
                            reference_id = f"{authors} {year}"
                        else:
                            reference_id = current_reference

                    references.append(
                        Reference(
                            reference_id=reference_id,
                            text=piece,
                            page_number=current_page,
                        )
                    )

        current_reference = None
        current_text = []
        current_page = None



    def discard_pending() -> None:
        pending_author_lines.clear()

    for page in pages:
        raw_lines = page.text.splitlines()

        for line_index, raw_line in enumerate(raw_lines):
            cleaned = " ".join(raw_line.split())

            if not cleaned:
                continue

            if _is_reference_heading(
                [line.strip() for line in raw_lines],
                line_index,
            ):
                flush_current()
                discard_pending()
                in_references = True
                continue

            if not in_references:
                continue

            if PAGE_ARTIFACT_RE.fullmatch(cleaned):
                continue

            # Explicitly numbered bibliography entry.
            
            numeric_match = NUMERIC_REFERENCE_RE.match(cleaned)
            if numeric_match:
                flush_current()
                discard_pending()

                number = numeric_match.group("bracket") or numeric_match.group("plain")
                first_text = numeric_match.group("text").strip()

                current_reference = f"[{number}]"
                current_text = [first_text] if first_text else []
                current_page = page.page_number
                continue


            # A buffered author list has reached its year.
            # This also handles lowercase fragments such as "moyer, and..."
            # after a surname was split across PDF lines.
            if pending_author_lines:
                fragment_match = FRAGMENT_YEAR_RE.match(cleaned)

                if fragment_match:
                    authors_tail = fragment_match.group("authors").strip()
                    year = fragment_match.group("year")

                    preceding_lines = [
                        line for line, _ in pending_author_lines
                    ]
                    authors = _join_author_lines(
                        preceding_lines + [authors_tail]
                    )

                    flush_current()
                    current_reference = f"{authors.rstrip(' .,')} {year}"
                    current_text = preceding_lines + [cleaned]
                    current_page = pending_author_lines[0][1]
                    discard_pending()
                    continue

                # A year-only line completes the buffered author list.
                year_match = YEAR_REST_RE.match(cleaned)
                if year_match:
                    preceding_lines = [
                        line for line, _ in pending_author_lines
                    ]
                    authors = _join_author_lines(preceding_lines)

                    flush_current()
                    current_reference = (
                        f"{authors} {year_match.group('year')}"
                    )
                    current_text = preceding_lines + [cleaned]
                    current_page = pending_author_lines[0][1]
                    discard_pending()
                    continue

                # Still collecting the wrapped author list.
                pending_author_lines.append((cleaned, page.page_number))
                continue

            # A complete author-year entry starts a new reference.
            author_year = _is_author_year_start(cleaned)
            if author_year:
                flush_current()

                authors, year, _ = author_year
                current_reference = f"{authors.rstrip(' .,')} {year}"
                current_text = [cleaned]
                current_page = page.page_number
                continue

            # Start buffering a wrapped author list before its year.
            if _is_probable_author_list_line(cleaned):
                flush_current()
                pending_author_lines.append((cleaned, page.page_number))
                continue

            # Ordinary continuation of the current reference.
            if current_reference is not None:
                current_text.append(cleaned)

    # Do not silently discard a trailing author list if the PDF is malformed.
    if pending_author_lines:
        flush_current()
        authors = _join_author_lines(
            [line for line, _ in pending_author_lines]
        )
        references.append(
            Reference(
                reference_id=authors,
                text=authors,
                page_number=pending_author_lines[0][1],
            )
        )

    flush_current()
    return references

