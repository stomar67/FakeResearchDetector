from pathlib import Path
from pdf_processor import extract_document

base = Path("DATASET/Data Original")
files = sorted(base.glob("P0[0-0][0-9]_V0*"))

print("Papers:", len(files))

for path in files:
    doc = extract_document(str(path))

    page_ok = all(
        page.page_number == i + 1
        for i, page in enumerate(doc.pages)
    )

    reference_ok = all(
        ref.page_number is None
        or 1 <= ref.page_number <= len(doc.pages)
        for ref in doc.references
    )

    citation_ok = all(
        1 <= citation.page_number <= len(doc.pages)
        for citation in doc.in_text_citations
    )

    print(
        f"{path.name}: "
        f"pages={'OK' if page_ok else 'FAIL'}, "
        f"references={'OK' if reference_ok else 'FAIL'}, "
        f"citations={'OK' if citation_ok else 'FAIL'}"
    )
