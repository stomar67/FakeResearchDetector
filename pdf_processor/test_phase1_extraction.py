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

def test_wrapped_author_list_starts_new_reference():
    pages = [
        Page(
            page_number=1,
            text="""References
Liang Xu, Anqi Li, Lei Zhu, Hang Xue, Changtai Zhu,
Kangkang Zhao, Haonan He, Xuanwei Zhang, Qiyue
Kang, and Zhenzhong Lan. 2023. Superclue: A comprehensive benchmark.
An Yang, Baosong Yang, Binyuan Hui, Bo Zheng,
Bowen Yu, Chang Zhou, Chengpeng Li, Chengyuan Li,
Dayiheng Liu, Fei Huang, et al. 2024. Qwen2 technical report.
ZouFan. 2023. Sina weibo comment.
""",
        )
    ]

    refs = extract_references(pages)

    assert len(refs) == 3
    assert refs[0].reference_id == "Liang Xu, Anqi Li, Lei Zhu, Hang Xue, Changtai Zhu, Kangkang Zhao, Haonan He, Xuanwei Zhang, Qiyue Kang, and Zhenzhong Lan 2023"
    assert refs[1].reference_id.startswith("An Yang, Baosong Yang")
    assert "Qwen2 technical report" in refs[1].text
    assert refs[2].reference_id == "ZouFan 2023"


def test_non_citation_parentheticals_are_filtered():
    page = Page(
        page_number=1,
        text=(
            "(Grant Nos. 2042022kf1218, 2042022kf1037). "
            "(LREC-COLING 2024). "
            "(Wang et al., 2023b; Smith, 2021). "
            "Beck (2008)."
        ),
    )

    citations = extract_in_text_citations([page])
    texts = [citation.citation_text for citation in citations]

    assert not any("Grant Nos." in text for text in texts)
    assert "(LREC-COLING 2024)" not in texts

    # Genuine parenthetical and narrative citations must remain.
    assert "(Wang et al., 2023b; Smith, 2021)" in texts
    assert "Beck (2008)" in texts


def test_split_merged_parenthesized_author_year_references():
    from pdf_processor.references import _split_merged_author_year_text

    text = (
        "Ullah, H., Saba, T., Islam, N. (2019). First paper title. "
        "Viera, A. J., & Garrett, J. M. (2005). "
        "Understanding interobserver agreement."
    )

    pieces = _split_merged_author_year_text(text)
    extracted = [piece for piece, _ in pieces]

    assert len(extracted) == 2
    assert extracted[0].startswith("Ullah, H.")
    assert extracted[1].startswith("Viera, A. J.")
    assert "First paper title" in extracted[0]
    assert "Understanding interobserver agreement" in extracted[1]


def test_split_merged_references_removes_article_footer():
    from pdf_processor.references import _split_merged_author_year_text

    text = (
        "Smith, J., & Jones, A. (2020). First paper. "
        "Brown, K., & Green, L. (2021). Second paper. "
        "How to cite this article: Example citation."
    )

    pieces = _split_merged_author_year_text(text)
    extracted = [piece for piece, _ in pieces]

    assert len(extracted) == 2
    assert all("How to cite this article" not in item for item in extracted)
