# Phase 1 PDF Processor

Scope: PDF -> page-aware structured document.

Included:
- PyMuPDF text extraction
- metadata extraction
- page provenance
- basic section detection
- numeric/author-year in-text citation extraction
- numeric reference extraction
- extraction quality heuristic
- OCR fallback interface

Not included:
- semantic citation verification
- scholarly evidence retrieval
- numeric consistency reasoning
- figure verification
- contradiction detection
- evidence fusion/risk scoring
- Neo4j
- final integrity report

## Usage

```python
from pdf_processor import extract_document

doc = extract_document("path/to/P000_V0_ORIGINAL.pdf")
print(doc.model_dump_json(indent=2))
```

The OCR engine is intentionally an integration point. Configure the approved OCR tool in the project environment before enabling it.
