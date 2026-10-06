from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from pdf_processor.extractor import extract_document

from ..dependencies import get_db
from ..models import Citation, Claim, Document, Page, Paper, Reference, Section
from ..schemas import (
    AnalysisResponse,
    PaperUploadResponse,
)
from ..services.nlp_service import run_phase1_nlp


router = APIRouter(
    prefix="/papers",
    tags=["papers"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post(
    "/upload",
    response_model=PaperUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_paper(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    safe_filename = f"{uuid4().hex}_{Path(file.filename).name}"
    file_path = UPLOAD_DIR / safe_filename

    file_contents = await file.read()

    if not file_contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    file_path.write_bytes(file_contents)

    paper = Paper(
        filename=file.filename,
    )

    db.add(paper)
    db.flush()

    document = Document(
        paper_id=paper.id,
        document_type="pdf",
        storage_path=str(file_path),
    )

    db.add(document)
    db.commit()

    db.refresh(paper)
    db.refresh(document)

    return PaperUploadResponse(
        paper=paper,
        document=document,
    )


@router.post(
    "/{paper_id}/analyze",
    response_model=AnalysisResponse,
)
def analyze_paper(
    paper_id: int,
    db: Session = Depends(get_db),
):
    paper = db.get(Paper, paper_id)

    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found.",
        )

    document = (
        db.query(Document)
        .filter(Document.paper_id == paper_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    structured_document = extract_document(
        document.storage_path,
    )

    paper.paper_id = structured_document.paper_id
    paper.variant_id = structured_document.variant_id

    document.extracted_text = "\n".join(
        page.text for page in structured_document.pages
    )

    for page in structured_document.pages:
        db.add(
            Page(
                document_id=document.id,
                page_number=page.page_number,
                text=page.text,
                extraction_method=page.extraction_method,
            )
        )

    section_records = {}

    for section_order, section in enumerate(
        structured_document.sections,
        start=1,
    ):
        db_section = Section(
            paper_id=paper.id,
            section_name=section.title,
            section_order=section_order,
            page_start=section.page_start,
            page_end=section.page_end,
            content=section.text,
        )

        db.add(db_section)

        section_records.setdefault(
            section.title.strip().lower(),
            [],
        ).append(db_section)

    reference_map = {}

    for reference_number, reference in enumerate(
        structured_document.references,
        start=1,
    ):
        db_reference = Reference(
            paper_id=paper.id,
            reference_number=reference_number,
            reference_identifier=reference.reference_id,
            page_number=reference.page_number,
            raw_text=reference.text,
        )

        db.add(db_reference)

        reference_map[reference.reference_id.strip()] = db_reference

    db.flush()

    citation_records = []

    for citation in structured_document.in_text_citations:
        reference_id = None

        if citation.reference_ids:
            reference = reference_map.get(
                citation.reference_ids[0].strip()
            )

            if reference is not None:
                reference_id = reference.id

        db_citation = Citation(
            paper_id=paper.id,
            claim_id=None,
            reference_id=reference_id,
            citation_text=citation.citation_text,
            page_number=citation.page_number,
        )

        db.add(db_citation)
        citation_records.append(db_citation)

    db.flush()

    # Run Sneha's existing Phase 1 NLP pipeline.
    integrated_claims = run_phase1_nlp(
        structured_document,
    )

    for integrated_claim in integrated_claims:
        section_id = None

        matching_sections = section_records.get(
            integrated_claim["section"].strip().lower(),
            [],
        )

        if matching_sections:
            candidate_page = integrated_claim["page"]

            page_matches = [
                section
                for section in matching_sections
                if (
                    section.page_start is None
                    or section.page_end is None
                    or (
                        section.page_start
                        <= candidate_page
                        <= section.page_end
                    )
                )
            ]

            if len(page_matches) == 1:
                section_id = page_matches[0].id
            elif len(matching_sections) == 1:
                section_id = matching_sections[0].id

        db_claim = Claim(
            paper_id=paper.id,
            section_id=section_id,
            claim_text=integrated_claim["text"],
            claim_type=integrated_claim["claim_type"],
            page_number=integrated_claim["page"],
        )

        db.add(db_claim)
        db.flush()

        for associated_citation in integrated_claim["citations"]:
            citation_text = associated_citation["citation_text"].strip()

            matching_citations = [
                citation
                for citation in citation_records
                if citation.citation_text.strip() == citation_text
                and citation.page_number
                == associated_citation["page"]
            ]

            for matching_citation in matching_citations:
                if matching_citation.claim_id is None:
                    matching_citation.claim_id = db_claim.id
                    break

    db.commit()

    return AnalysisResponse(
        paper_id=paper_id,
        status="completed",
        message=(
            "PDF extraction, Phase 1 NLP processing, "
            "and database persistence completed successfully."
        ),
    )