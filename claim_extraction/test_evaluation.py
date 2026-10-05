from .evaluation import evaluate_candidates


def test_evaluate_candidates():
    gold_claims = [
        "The proposed method achieved 91.2% accuracy.",
        "Our approach outperformed the baseline method.",
        "The difference was statistically significant.",
    ]

    predicted_claims = [
        "The proposed method achieved 91.2% accuracy.",
        "Our approach outperformed the baseline method.",
        "This is an unrelated sentence.",
    ]

    result = evaluate_candidates(
        gold_claims=gold_claims,
        predicted_claims=predicted_claims,
    )

    assert result.true_positives == 2
    assert result.false_positives == 1
    assert result.false_negatives == 1
    assert result.precision == 2 / 3
    assert result.recall == 2 / 3
    assert result.f1 == 2 / 3