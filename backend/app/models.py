from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    paper_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    variant_id: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    documents: Mapped[list["Document"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
    )

    sections: Mapped[list["Section"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
    )

    references: Mapped[list["Reference"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
    )

    claims: Mapped[list["Claim"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
    )

    citations: Mapped[list["Citation"]] = relationship(
        back_populates="paper",
        cascade="all, delete-orphan",
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id"),
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pdf",
    )

    storage_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    paper: Mapped["Paper"] = relationship(
        back_populates="documents",
    )

    pages: Mapped[list["Page"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    extraction_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    document: Mapped["Document"] = relationship(
        back_populates="pages",
    )


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id"),
        nullable=False,
    )

    section_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    section_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    page_start: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    page_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    paper: Mapped["Paper"] = relationship(
        back_populates="sections",
    )


class Reference(Base):
    __tablename__ = "references"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id"),
        nullable=False,
    )

    reference_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reference_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    paper: Mapped["Paper"] = relationship(
        back_populates="references",
    )

    citations: Mapped[list["Citation"]] = relationship(
        back_populates="reference",
    )


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id"),
        nullable=False,
    )

    section_id: Mapped[int | None] = mapped_column(
        ForeignKey("sections.id"),
        nullable=True,
    )

    claim_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    paper: Mapped["Paper"] = relationship(
        back_populates="claims",
    )

    citations: Mapped[list["Citation"]] = relationship(
        back_populates="claim",
        cascade="all, delete-orphan",
    )


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id"),
        nullable=False,
    )

    claim_id: Mapped[int | None] = mapped_column(
        ForeignKey("claims.id"),
        nullable=True,
    )

    reference_id: Mapped[int | None] = mapped_column(
        ForeignKey("references.id"),
        nullable=True,
    )

    citation_text: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    paper: Mapped["Paper"] = relationship(
        back_populates="citations",
    )

    claim: Mapped["Claim | None"] = relationship(
        back_populates="citations",
    )

    reference: Mapped["Reference | None"] = relationship(
        back_populates="citations",
    )