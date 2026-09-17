import re


def extraction_quality(text: str) -> float:
    """Simple Phase-1 quality heuristic. Higher means more usable extracted text."""
    if not text or not text.strip():
        return 0.0

    chars = len(text.strip())
    alpha = len(re.findall(r"[A-Za-z]", text))
    words = re.findall(r"\b\w+\b", text)

    if chars == 0 or not words:
        return 0.0

    alpha_ratio = alpha / max(chars, 1)
    word_density = min(len(words) / max(chars / 5, 1), 1.0)

    score = 0.7 * alpha_ratio + 0.3 * word_density
    return round(max(0.0, min(score, 1.0)), 3)


def needs_ocr(text: str, threshold: float = 0.25) -> bool:
    return extraction_quality(text) < threshold
