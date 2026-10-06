from pdf_processor.schemas import (
    Page,
    Section,
    StructuredDocument,
)
from claim_extraction.sentence_processing import (
    process_document,
    split_sentences,
)


def test_split_sentences():
    text = (
        "This is the first sentence. "
        "This is the second sentence."
    )

    result = split_sentences(text)

    assert result == [
        "This is the first sentence.",
        "This is the second sentence.",
    ]


def test_split_sentences_removes_standalone_page_number():
    text = (
        "This is a scientific sentence. "
        "1"
    )

    result = split_sentences(text)

    assert result == [
        "This is a scientific sentence.",
    ]


def test_process_document_preserves_section_and_page():
    document = StructuredDocument(
        paper_id="PTEST",
        variant_id="V0",
        filename="test.pdf",
        metadata={},
        pages=[
            Page(
                page_number=1,
                text="Abstract\nThis is a scientific claim.",
                extraction_method="pymupdf",
            )
        ],
        sections=[
            Section(
                section_id="sec_1",
                title="Abstract",
                text="This is a scientific claim.",
                page_start=1,
                page_end=1,
            )
        ],
        references=[],
        in_text_citations=[],
        extraction_info={},
    )

    result = process_document(document)

    assert len(result) == 1
    assert result[0].sentence_id == "S0001"
    assert result[0].page == 1
    assert result[0].section == "Abstract"
    assert result[0].text == "This is a scientific claim."