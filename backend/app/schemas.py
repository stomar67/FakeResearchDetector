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

class ResultSection(BaseModel):
    id: int
    name: str
    order: int
    page_start: int | None
    page_end: int | None
    content: str | None


class ResultReference(BaseModel):
    id: int
    reference_number: int
    reference_identifier: str | None
    page_number: int | None
    raw_text: str


class ResultClaim(BaseModel):
    id: int
    text: str
    claim_type: str | None
    page_number: int | None
    section_id: int | None
    citation_ids: list[int]


class ResultCitation(BaseModel):
    id: int
    citation_text: str
    page_number: int | None
    claim_id: int | None
    reference_id: int | None

class ResultPaper(BaseModel):
    id: int
    paper_id: str | None
    variant_id: str | None
    title: str | None
    filename: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaperResultsResponse(BaseModel):
    paper: ResultPaper
    sections: list[ResultSection]
    references: list[ResultReference]
    claims: list[ResultClaim]
    citations: list[ResultCitation]