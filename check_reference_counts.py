from pathlib import Path
import pymupdf

from pdf_processor.references import extract_references
from pdf_processor.schemas import Page
from pdf_processor.references import _split_merged_author_year_text

targets = {"P024_V0_Original.pdf", "P029_V0_ORIGINAL.pdf"}

found = set()

for pdf_path in Path(".").rglob("*.pdf"):
    if pdf_path.name not in targets:
        continue

    found.add(pdf_path.name)

    print("\n" + "=" * 75)
    print("PDF:", pdf_path.resolve())

    pages = []

    with pymupdf.open(pdf_path) as doc:
        for index, page in enumerate(doc):
            pages.append(
                Page(
                    page_number=index + 1,
                    text=page.get_text("text") or "",
                    extraction_method="pymupdf",
                )
            )

    refs = extract_references(pages)
    print("Extracted references:", len(refs))

    for i, ref in enumerate(refs, start=1):
        text = " ".join(ref.text.split())

        if len(text) > 1200:
            
            pieces = _split_merged_author_year_text(ref.text)

            print("Pieces detected by splitter:", len(pieces))

            for j, (piece, _) in enumerate(pieces, start=1):
                print(f"  Piece {j}: {piece[:180]}")
            print(f"\nPOSSIBLY MERGED [{i}], length={len(text)}")
            print("Reference ID:", repr(ref.reference_id))
            print("ID starts with '[':", ref.reference_id.startswith("["))
            print("START:", text[:350])
            print("...")
            print("END:", text[-250:])

    print("Diagnostic complete.")

missing = targets - found
if missing:
    print("\nPDFs NOT FOUND:", ", ".join(sorted(missing)))
