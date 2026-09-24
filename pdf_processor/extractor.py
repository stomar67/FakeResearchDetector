import re
from pathlib import Path
from typing import Optional, Tuple

import pymupdf

from .citations import extract_in_text_citations
from .metadata import extract_metadata
from .ocr import ocr_pdf
from .quality import extraction_quality, needs_ocr
from .references import extract_references
from .schemas import ExtractionInfo, Page, StructuredDocument
from .sections import detect_sections


def infer_ids(pdf_path: Path) -> Tuple[str, str]:
    """Infer paper/variant IDs from filename, then parent folders."""
    name = pdf_path.stem.upper()

    paper_match = re.search(r"(P\d{3})", name)
    variant_match = re.search(r"(?:^|_)(V\d{1,2})(?:_|$)", name)

    paper_id = paper_match.group(1) if paper_match else ""
    variant_id = variant_match.group(1) if variant_match else ""

    for parent in pdf_path.parents:
        parent_name = parent.name.upper()

        if not paper_id:
            paper_match = re.search(r"(P\d{3})", parent_name)
            if paper_match:
                paper_id = paper_match.group(1)

        if not variant_id:
            variant_match = re.search(r"(V\d{1,2})", parent_name)
            if variant_match:
                variant_id = variant_match.group(1)

    return paper_id or "UNKNOWN", variant_id or "V0"


def extract_document(
    pdf_path: str,
    paper_id: Optional[str] = None,
    variant_id: Optional[str] = None,
    ocr_threshold: float = 0.25,
) -> StructuredDocument:
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    inferred_paper, inferred_variant = infer_ids(path)
    paper_id = paper_id or inferred_paper
    variant_id = variant_id or inferred_variant

    pages = []
    with pymupdf.open(path) as doc:
        for index, page in enumerate(doc):
            pages.append(
                Page(
                    page_number=index + 1,
                    text=page.get_text("text") or "",
                    extraction_method="pymupdf",
                )
            )

        metadata = extract_metadata(doc)

    quality = extraction_quality("\n".join(p.text for p in pages))
    method = "pymupdf"
    ocr_used = False

    if needs_ocr("\n".join(p.text for p in pages), ocr_threshold):
        try:
            pages = ocr_pdf(str(path))
            method = "ocr"
            ocr_used = True
            quality = extraction_quality("\n".join(p.text for p in pages))
        except NotImplementedError:
            # OCR is intentionally an integration point in this Phase-1 package.
            pass

    return StructuredDocument(
        paper_id=paper_id,
        variant_id=variant_id,
        filename=path.name,
        metadata=metadata,
        pages=pages,
        sections=detect_sections(pages),
        references=extract_references(pages),
        in_text_citations=extract_in_text_citations(pages),
        extraction_info=ExtractionInfo(
            method=method,
            ocr_used=ocr_used,
            quality_score=quality,
        ),
    )
