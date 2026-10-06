"""
Phase 1 — NLP Integration Adapter

Purpose:
    Combine the existing Phase 1 NLP outputs into the logical structure
    consumed by the backend integration layer.

This is a serialization/adapter layer only. It does NOT modify the
existing claim extraction, classification, or citation-association logic.

It does NOT:
    - assign PostgreSQL/database IDs
    - generate citation IDs
    - verify claims or citations
    - retrieve evidence
    - perform numerical verification
    - perform risk scoring
    - implement Phase 2 functionality
"""

from dataclasses import asdict, dataclass, field
import json

from pdf_processor.schemas import StructuredDocument

from .claim_extractor import CandidateClaim
from .claim_classifier import ClaimTypePrediction
from .citation_association import ClaimCitationAssociation


@dataclass
class IntegrationCitation:
    """Citation information preserved for backend association."""

    citation_text: str
    page: int | None
    association_method: str


@dataclass
class IntegrationClaim:
    """Logical Phase 1 claim representation for backend handoff."""

    claim_id: str
    paper_id: str
    text: str
    page: int
    section: str
    citation_ids: list[str] = field(default_factory=list)
    claim_type: str = "OTHER"
    citations: list[IntegrationCitation] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Return a JSON-serializable logical integration record."""
        return asdict(self)


def serialize_phase1_claims(
    document: StructuredDocument,
    candidates: list[CandidateClaim],
    predictions: list[ClaimTypePrediction],
    associations: list[ClaimCitationAssociation],
) -> list[dict]:
    """
    Combine existing NLP outputs into backend-facing logical records.

    Candidate IDs remain the existing CANDxxxx IDs. ``citation_ids`` is
    intentionally empty because database identifiers are assigned by the
    backend. Extracted citation text and association metadata are preserved
    in ``citations`` so the backend can create/map its own citation records.
    """

    predictions_by_id = {
        prediction.candidate_id: prediction
        for prediction in predictions
    }

    citations_by_id: dict[str, list[IntegrationCitation]] = {}
    for association in associations:
        citations_by_id.setdefault(association.candidate_id, []).append(
            IntegrationCitation(
                citation_text=association.citation_text,
                page=association.page,
                association_method=association.association_method,
            )
        )

    output: list[dict] = []

    for candidate in candidates:
        prediction = predictions_by_id.get(candidate.candidate_id)
        if prediction is None:
            raise ValueError(
                "Missing claim-type prediction for candidate "
                f"{candidate.candidate_id}"
            )

        record = IntegrationClaim(
            claim_id=candidate.candidate_id,
            paper_id=document.paper_id,
            text=candidate.claim_text,
            page=candidate.page,
            section=candidate.section,
            citation_ids=[],
            claim_type=prediction.claim_type,
            citations=citations_by_id.get(candidate.candidate_id, []),
        )

        output.append(record.to_dict())

    return output


def serialize_phase1_json(
    document: StructuredDocument,
    candidates: list[CandidateClaim],
    predictions: list[ClaimTypePrediction],
    associations: list[ClaimCitationAssociation],
    *,
    indent: int = 2,
) -> str:
    """Serialize Phase 1 integration records as a JSON array."""

    return json.dumps(
        serialize_phase1_claims(
            document=document,
            candidates=candidates,
            predictions=predictions,
            associations=associations,
        ),
        indent=indent,
        ensure_ascii=False,
    )
