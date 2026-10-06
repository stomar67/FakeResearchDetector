from .gold_loader import load_gold_claims


def test_gold_loader():
    expected_counts = {
        "P000": 175,
        "P007": 170,
        "P036": 177,
    }

    for paper_id, expected_count in expected_counts.items():
        claims = load_gold_claims(paper_id)

        assert len(claims) == expected_count

        assert claims[0].claim_id
        assert claims[0].page is not None
        assert claims[0].section
        assert claims[0].claim_type
        assert claims[0].is_checkable is True
        assert claims[0].claim_text