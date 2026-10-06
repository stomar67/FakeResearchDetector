from claim_extraction.citation_association import (
    associate_candidate_citations_batch,
)
from claim_extraction.claim_classifier import (
    classify_candidate_claims,
)
from claim_extraction.claim_extractor import (
    extract_candidate_claims,
)
from claim_extraction.integration_adapter import (
    serialize_phase1_claims,
)
from claim_extraction.sentence_processing import (
    process_document,
)
from pdf_processor.schemas import StructuredDocument


def run_phase1_nlp(
    document: StructuredDocument,
) -> list[dict]:
    """
    Run the existing Phase 1 NLP pipeline on a StructuredDocument.

    This function only orchestrates the existing NLP modules.
    It does not modify extraction, classification, or citation
    association logic.
    """

    sentences = process_document(document)

    candidates = extract_candidate_claims(sentences)

    predictions = classify_candidate_claims(candidates)

    associations = associate_candidate_citations_batch(
        candidates=candidates,
        document=document,
    )

    return serialize_phase1_claims(
        document=document,
        candidates=candidates,
        predictions=predictions,
        associations=associations,
    )