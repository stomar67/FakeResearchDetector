import re
from typing import List
from .schemas import Reference, Page

REF_HEADING_RE = re.compile(r"^\s*references\s*$", re.IGNORECASE)
NUM_REF_RE = re.compile(r"^\s*\[?(\d{1,4})\]?\s*[.)]?\s+(.+)$")


def extract_references(pages: List[Page]) -> List[Reference]:
    references: List[Reference] = []
    in_references = False
    current_id = None
    current_text = []
    current_page = None

    def flush():
        nonlocal current_id, current_text, current_page
        if current_id is not None:
            references.append(
                Reference(
                    reference_id=current_id,
                    text=" ".join(current_text).strip(),
                    page_number=current_page,
                )
            )
        current_id = current_text = current_page = None

    for page in pages:
        for raw_line in page.text.splitlines():
            line = raw_line.strip()
            if REF_HEADING_RE.match(line):
                flush()
                in_references = True
                continue

            if not in_references or not line:
                continue

            match = NUM_REF_RE.match(line)
            if match:
                flush()
                current_id = match.group(1)
                current_text = [match.group(2)]
                current_page = page.page_number
            elif current_id is not None:
                current_text.append(line)

    flush()
    return references
