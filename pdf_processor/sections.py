import re
from typing import List
from .schemas import Section, Page

SECTION_RE = re.compile(
    r"^\s*(?:(\d+(?:\.\d+)*)[.)]?\s+)?"
    r"(abstract|introduction|background|related work|literature review|"
    r"methodology|methods|materials and methods|experiments?|results|"
    r"discussion|conclusion|limitations?|acknowledg(?:e)?ments?|references)"
    r"\s*$",
    re.IGNORECASE,
)


def detect_sections(pages: List[Page]) -> List[Section]:
    sections = []
    current_title = None
    current_start = None
    current_text = []
    current_end = None

    def flush():
        nonlocal current_title, current_start, current_text, current_end
        if current_title is not None:
            sections.append(
                Section(
                    section_id=f"sec_{len(sections) + 1}",
                    title=current_title,
                    text="\n".join(current_text).strip(),
                    page_start=current_start,
                    page_end=current_end,
                )
            )
        current_title = current_start = current_end = None
        current_text = []

    for page in pages:
        for line in page.text.splitlines():
            match = SECTION_RE.match(line.strip())
            if match:
                flush()
                current_title = line.strip()
                current_start = page.page_number
                current_end = page.page_number
            elif current_title is not None:
                current_text.append(line)
                current_end = page.page_number

    flush()
    return sections
