import re
from pathlib import Path
from typing import Optional, Tuple

import fitz

from .citations import extract_in_text_citations
from .metadata import extract_metadata
from .ocr import ocr_pdf
from .quality import extraction_quality, needs_ocr
from .references import extract_references
from .schemas import ExtractionInfo, Page, StructuredDocument
from .sections import detect_sections


def infer_ids(pdf_path: Path) -> Tuple[str, str]:
    """
    Accept common dataset naming patterns and fall back to parent folders.
    """
    name = pdf_path.stem

    paper = re.search(r"\b(P\d{3})\b", name, re.IGNORECASE)
    variant = re.search(r"\b(V\d{1,2})\b", name, re.IGNORECASE)

    paper_id = paper.group(1).upper() if paper else ""
    variant_id = variant.group(1).upper() if variant else ""

    if not paper_id:
        for parent in pdf_path.parents:
            match = re.search(r"\b(P\d{3})\b", parent.name, re.IGNORECASE)
            if match:
                paper_id = match.group(1).upper()
                break

    if not variant_id:
        for parent in pdf_path.parents:
            match = re.search(r"\b(V\d{1,2})\b", parent.name, re.IGNORECASE)
            if match:
                variant_id = match.group(1).upper()
                break

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
    with fitz.open(path) as doc:
        for index, page in enumerate(doc):
            text = page.get_text("text") or ""
            pages.append(
                Page(
                    page_number=index + 1,
                    text=text,
                    extraction_method="pymupdf",
                )
            )

        metadata = extract_metadata(doc)

    combined_text = "\n".join(p.text for p in pages)
    quality = extraction_quality(combined_text)

    if needs_ocr(combined_text, ocr_threshold):
        try:
            pages = ocr_pdf(str(path))
            method = "ocr"
            ocr_used = True
        except NotImplementedError:
            # Keep the PyMuPDF output available and expose its quality score.
            method = "pymupdf"
            ocr_used = False
    else:
        method = "pymupdf"
        ocr_used = False

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
