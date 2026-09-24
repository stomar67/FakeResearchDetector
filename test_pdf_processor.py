from pdf_processor import extract_document

doc = extract_document(
    r"DATASET\Data Original\P000_V0_ORIGINAL.pdf"
)

print(doc.model_dump_json(indent=2))