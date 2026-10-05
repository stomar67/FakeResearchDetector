from claim_extraction.citation_association import (
    associate_candidate_citations,
    normalize_citation_for_matching,
)
from claim_extraction.claim_extractor import CandidateClaim
from pdf_processor.schemas import (
    InTextCitation,
    Page,
    Section,
    StructuredDocument,
)


def make_candidate(text: str) -> CandidateClaim:
    return CandidateClaim(
        candidate_id="CAND0001",
        sentence_id="S0001",
        page=1,
        section="Introduction",
        claim_text=text,
        signals=["method_language"],
    )


def make_document(citations):
    return StructuredDocument(
        paper_id="PTEST",
        variant_id="V0",
        filename="test.pdf",
        metadata={},
        pages=[
            Page(
                page_number=1,
                text="Introduction",
                extraction_method="pymupdf",
            )
        ],
        sections=[
            Section(
                section_id="sec_1",
                title="Introduction",
                text="",
                page_start=1,
                page_end=1,
            )
        ],
        references=[],
        in_text_citations=citations,
        extraction_info={},
    )


def test_normalize_citation_for_matching():
    citation = "(Smith et al.,\n2024)"

    assert normalize_citation_for_matching(citation) == (
        "(Smith et al., 2024)"
    )


def test_associate_explicit_citation_in_sentence():
    candidate = make_candidate(
        "Our method improves accuracy "
        "(Smith et al., 2024)."
    )

    document = make_document(
        [
            InTextCitation(
                citation_text="(Smith et al., 2024)",
                citation_type="author_year",
                reference_ids=[],
                page_number=1,
                text="Our method improves accuracy (Smith et al., 2024).",
            )
        ]
    )

    result = associate_candidate_citations(
        candidate,
        document,
    )

    assert len(result) == 1
    assert result[0].candidate_id == "CAND0001"
    assert result[0].citation_text == "(Smith et al., 2024)"
    assert result[0].page == 1
    assert result[0].association_method == "explicit_in_sentence"


def test_no_association_when_citation_is_only_on_same_page():
    candidate = make_candidate(
        "Our method improves accuracy."
    )

    document = make_document(
        [
            InTextCitation(
                citation_text="(Smith et al., 2024)",
                citation_type="author_year",
                reference_ids=[],
                page_number=1,
                text="Our method improves accuracy. (Smith et al., 2024)",
            )
        ]
    )

    result = associate_candidate_citations(
        candidate,
        document,
    )

    assert result == []


def test_associate_multiple_citations():
    candidate = make_candidate(
        "Our method builds on previous approaches "
        "(Smith et al., 2024; Jones et al., 2023)."
    )

    document = make_document(
        [
            InTextCitation(
                citation_text="(Smith et al., 2024; Jones et al., 2023)",
                citation_type="author_year",
                reference_ids=[],
                page_number=1,
                text="...",
            ),
            InTextCitation(
                citation_text="(Jones et al., 2023)",
                citation_type="author_year",
                reference_ids=[],
                page_number=1,
                text="...",
            ),
        ]
    )

    result = associate_candidate_citations(
        candidate,
        document,
    )

    # Kunjum's extractor represents the complete parenthetical
    # citation as one citation object. Phase 1 preserves that
    # extracted citation relationship rather than splitting it.
    assert len(result) == 1
    assert result[0].candidate_id == "CAND0001"
    assert result[0].citation_text == (
        "(Smith et al., 2024; Jones et al., 2023)"
    )
    assert result[0].page == 1
    assert result[0].association_method == "explicit_in_sentence"


def test_pdf_line_break_in_citation_is_matched():
    candidate = make_candidate(
        "Our method improves accuracy "
        "(Smith et al., 2024)."
    )

    document = make_document(
        [
            InTextCitation(
                citation_text="(Smith et al.,\n2024)",
                citation_type="author_year",
                reference_ids=[],
                page_number=1,
                text="...",
            )
        ]
    )

    result = associate_candidate_citations(
        candidate,
        document,
    )

    assert len(result) == 1
    assert result[0].citation_text == "(Smith et al.,\n2024)"