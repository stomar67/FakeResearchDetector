from .claim_extractor import extract_candidate_claims
from .sentence_processing import process_document
from pdf_processor.schemas import Page, Section, StructuredDocument


def test_extract_candidate_claims():
    document = StructuredDocument(
        paper_id="PTEST",
        variant_id="V0",
        filename="test.pdf",
        metadata={},
        pages=[
            Page(
                page_number=1,
                text=(
                    "Introduction\n"
                    "We propose a new method. "
                    "The proposed method achieved 91.2% accuracy. "
                    "The weather was sunny."
                ),
                extraction_method="pymupdf",
            ),
            Page(
                page_number=2,
                text=(
                    "Results\n"
                    "Our approach outperformed the baseline method. "
                    "The difference was statistically significant."
                ),
                extraction_method="pymupdf",
            ),
        ],
        sections=[
            Section(
                section_id="sec_1",
                title="Introduction",
                text=(
                    "We propose a new method. "
                    "The proposed method achieved 91.2% accuracy. "
                    "The weather was sunny."
                ),
                page_start=1,
                page_end=1,
            ),
            Section(
                section_id="sec_2",
                title="Results",
                text=(
                    "Our approach outperformed the baseline method. "
                    "The difference was statistically significant."
                ),
                page_start=2,
                page_end=2,
            ),
        ],
        references=[],
        in_text_citations=[],
        extraction_info={},
    )

    sentences = process_document(document)
    candidates = extract_candidate_claims(sentences)

    assert len(candidates) == 4

    assert candidates[0].page == 1
    assert candidates[0].section == "Introduction"

    assert candidates[1].page == 1
    assert candidates[1].section == "Introduction"

    assert candidates[2].page == 2
    assert candidates[2].section == "Results"

    assert candidates[3].page == 2
    assert candidates[3].section == "Results"

    assert candidates[1].claim_text == (
        "The proposed method achieved 91.2% accuracy."
    )

    assert "result_language" in candidates[1].signals