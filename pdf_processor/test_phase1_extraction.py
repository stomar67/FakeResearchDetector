from pdf_processor.citations import extract_in_text_citations
from pdf_processor.references import extract_references
from pdf_processor.schemas import Page


def test_references():
    pages = [
        Page(
            page_number=1,
            text="""References
Aaron T Beck. 2008. The book title.
Alexis Conneau, Kartikay Khandelwal, Naman Goyal, Veselin Stoyanov. 2020. A paper title.
moyer, and Veselin Stoyanov. 2020. Wrapped continuation.
OpenAI. 2023. Technical report.
16049
[5] Smith, J. 2021. Numbered reference.
continued text.
""",
        )
    ]

    refs = extract_references(pages)
    assert len(refs) == 4
    assert refs[0].reference_id == "Aaron T Beck 2008"
    assert "moyer, and Veselin Stoyanov. 2020." in refs[1].text
    assert refs[2].reference_id == "OpenAI 2023"
    assert refs[3].reference_id == "[5]"
    assert "16049" not in "\n".join(r.text for r in refs)


def test_citations():
    pages = [
        Page(
            page_number=1,
            text=(
                "Beck (2008) and Clark and Beck (2010). "
                "(Wang et al., 2023b; Smith, 2021). [3, 7–9]."
            ),
        )
    ]
    citations = extract_in_text_citations(pages)
    texts = [c.citation_text for c in citations]

    assert "[3, 7–9]" in texts
    assert "(Wang et al., 2023b; Smith, 2021)" in texts
    assert "Beck (2008)" in texts
    assert "Clark and Beck (2010)" in texts
    assert "(2008)" not in texts


if __name__ == "__main__":
    test_references()
    test_citations()
    print("Phase 1 extraction tests passed.")

def test_author_year_reference_matching():
    from pdf_processor.citations import match_citations_to_references
    from pdf_processor.schemas import InTextCitation, Reference

    references = [
        Reference(
            reference_id="Aaron T Beck 2008",
            text="Aaron T Beck. 2008. The book title.",
            page_number=2,
        ),
        Reference(
            reference_id="David A Clark and Aaron T Beck 2010",
            text="David A Clark and Aaron T Beck. 2010. Another title.",
            page_number=2,
        ),
    ]

    citations = [
        InTextCitation(
            citation_text="(Beck, 2008)",
            citation_type="author_year",
            page_number=1,
        ),
        InTextCitation(
            citation_text="Clark and Beck (2010)",
            citation_type="author_year",
            page_number=1,
        ),
        InTextCitation(
            citation_text="[3]",
            citation_type="numeric",
            reference_ids=["3"],
            page_number=1,
        ),
    ]

    matched = match_citations_to_references(citations, references)

    assert matched[0].reference_ids == ["Aaron T Beck 2008"]
    assert matched[1].reference_ids == [
        "David A Clark and Aaron T Beck 2010"
    ]
    assert matched[2].reference_ids == ["3"]

def test_multiple_author_year_citations_in_one_group():
    from pdf_processor.citations import match_citations_to_references
    from pdf_processor.schemas import InTextCitation, Reference

    references = [
        Reference(
            reference_id="Wang et al. 2023b",
            text="Wang et al. 2023b. First paper.",
            page_number=2,
        ),
        Reference(
            reference_id="Smith 2021",
            text="Smith, J. 2021. Second paper.",
            page_number=2,
        ),
    ]

    citations = [
        InTextCitation(
            citation_text="(Wang et al., 2023b; Smith, 2021)",
            citation_type="author_year",
            page_number=1,
        )
    ]

    matched = match_citations_to_references(citations, references)

    assert set(matched[0].reference_ids) == {
        "Wang et al. 2023b",
        "Smith 2021",
    }
