from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    title: str = ""
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None


class Page(BaseModel):
    page_number: int
    text: str = ""
    extraction_method: Literal["pymupdf", "ocr"] = "pymupdf"


class Section(BaseModel):
    section_id: str
    title: str
    text: str = ""
    page_start: int
    page_end: int


class Reference(BaseModel):
    reference_id: str
    text: str = ""
    page_number: Optional[int] = None


class InTextCitation(BaseModel):
    citation_text: str
    citation_type: Literal["numeric", "author_year", "unknown"] = "unknown"
    reference_ids: List[str] = Field(default_factory=list)
    page_number: int
    text: str = ""


class ExtractionInfo(BaseModel):
    method: Literal["pymupdf", "ocr"] = "pymupdf"
    ocr_used: bool = False
    quality_score: float = 0.0


class StructuredDocument(BaseModel):
    paper_id: str
    variant_id: str
    filename: str
    metadata: DocumentMetadata
    pages: List[Page] = Field(default_factory=list)
    sections: List[Section] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    in_text_citations: List[InTextCitation] = Field(default_factory=list)
    extraction_info: ExtractionInfo
