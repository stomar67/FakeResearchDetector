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
