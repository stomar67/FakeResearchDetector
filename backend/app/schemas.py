from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaperResponse(BaseModel):
    id: int
    title: str | None
    filename: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    id: int
    paper_id: int
    document_type: str
    extracted_text: str | None

    model_config = ConfigDict(from_attributes=True)


class PaperUploadResponse(BaseModel):
    paper: PaperResponse
    document: DocumentResponse


class AnalysisResponse(BaseModel):
    paper_id: int
    status: str
    message: str