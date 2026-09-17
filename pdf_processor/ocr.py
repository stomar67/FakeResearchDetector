from pathlib import Path
from typing import List
from .schemas import Page


def ocr_pdf(pdf_path: str) -> List[Page]:
    """
    OCR fallback interface for Phase 1.

    This intentionally does not hard-code an OCR engine. The project can
    connect the approved OCR tool in the environment without changing the
    StructuredDocument contract.
    """
    raise NotImplementedError(
        "OCR fallback is not wired yet. Install/configure the approved OCR "
        "tool for the project environment before enabling this path."
    )
