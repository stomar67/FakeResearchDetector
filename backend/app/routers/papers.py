from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..models import Document, Paper
from ..schemas import (
    AnalysisResponse,
    PaperUploadResponse,
)


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

    return AnalysisResponse(
        paper_id=paper_id,
        status="pending",
        message="Analysis endpoint is ready. PDF processing will be integrated in Day 7.",
    )