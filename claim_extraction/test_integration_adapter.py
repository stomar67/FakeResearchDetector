"""Tests for the Phase 1 NLP-to-backend integration adapter."""

import json

from pdf_processor.schemas import (
    DocumentMetadata,
    ExtractionInfo,
    StructuredDocument,
)

from claim_extraction.claim_extractor import CandidateClaim
from claim_extraction.claim_classifier import ClaimTypePrediction
from claim_extraction.citation_association import ClaimCitationAssociation
from claim_extraction.integration_adapter import (
    serialize_phase1_claims,
    serialize_phase1_json,
)


def make_document() -> StructuredDocument:
    return StructuredDocument(
        paper_id="P001",
        variant_id="V0",
        filename="P001.pdf",
        metadata=DocumentMetadata(title="Test paper"),
        extraction_info=ExtractionInfo(),
    )


def make_candidate() -> CandidateClaim:
    return CandidateClaim(
        candidate_id="CAND0001",
        sentence_id="S0001",
        page=7,
        section="Results",
        claim_text="The proposed method achieved higher accuracy.",
        signals=["result_language", "comparison_language"],
    )


def test_adapter_combines_existing_outputs_without_database_ids():
    result = serialize_phase1_claims(
        document=make_document(),
        candidates=[make_candidate()],
        predictions=[
            ClaimTypePrediction(
                candidate_id="CAND0001",
                claim_type="RESULT",
                signals_used=["result_language", "comparison_language"],
            )
        ],
        associations=[
            ClaimCitationAssociation(
                candidate_id="CAND0001",
                citation_text="(Smith et al., 2024)",
                page=7,
                association_method="explicit_in_sentence",
            )
        ],
    )

    assert result == [
        {
            "claim_id": "CAND0001",
            "paper_id": "P001",
            "text": "The proposed method achieved higher accuracy.",
            "page": 7,
            "section": "Results",
            "citation_ids": [],
            "claim_type": "RESULT",
            "citations": [
                {
                    "citation_text": "(Smith et al., 2024)",
                    "page": 7,
                    "association_method": "explicit_in_sentence",
                }
            ],
        }
    ]


def test_adapter_preserves_no_citation_as_empty_collection():
    result = serialize_phase1_claims(
        document=make_document(),
        candidates=[make_candidate()],
        predictions=[
            ClaimTypePrediction(
                candidate_id="CAND0001",
                claim_type="RESULT",
                signals_used=["result_language"],
            )
        ],
        associations=[],
    )

    assert result[0]["citation_ids"] == []
    assert result[0]["citations"] == []


def test_json_serialization_is_valid_and_keeps_candidate_id():
    payload = serialize_phase1_json(
        document=make_document(),
        candidates=[make_candidate()],
        predictions=[
            ClaimTypePrediction(
                candidate_id="CAND0001",
                claim_type="RESULT",
                signals_used=["result_language"],
            )
        ],
        associations=[],
    )

    decoded = json.loads(payload)

    assert decoded[0]["claim_id"] == "CAND0001"
    assert decoded[0]["paper_id"] == "P001"
    assert decoded[0]["citation_ids"] == []
