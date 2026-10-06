"""
Phase 1 — Gold Standard Loader

Loads the manually validated Phase 1 claim annotations for the
three pilot papers.

Authoritative pilot files:
    P000_Phase1_Gold_Standard_FINAL.xlsx
    P007_Phase1_Annotation.xlsx
    P036_Phase1_Annotation.xlsx

This module does NOT modify the gold-standard files.
"""

from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook


@dataclass
class GoldClaim:
    paper_id: str
    claim_id: str
    claim_text: str
    page: int | None
    section: str
    claim_type: str
    citation_ids: str
    is_checkable: bool
    notes: str


PROJECT_ROOT = Path(__file__).resolve().parent
ANNOTATION_DIR = PROJECT_ROOT / "gold_standart_claim_annotaions"


GOLD_FILES = {
    "P000": ANNOTATION_DIR / "P000_Phase1_Gold_Standard_FINAL.xlsx",
    "P007": ANNOTATION_DIR / "P007_Phase1_Annotation.xlsx",
    "P036": ANNOTATION_DIR / "P036_Phase1_Annotation.xlsx",
}


def load_gold_claims(paper_id: str) -> list[GoldClaim]:
    """
    Load validated claims for one pilot paper.

    Only the Final_Annotations sheet is used when it exists.
    """

    if paper_id not in GOLD_FILES:
        raise ValueError(
            f"Unknown paper_id: {paper_id}. "
            f"Expected one of: {', '.join(GOLD_FILES)}"
        )

    file_path = GOLD_FILES[paper_id]

    if not file_path.exists():
        raise FileNotFoundError(
            f"Gold-standard file not found: {file_path}"
        )

    workbook = load_workbook(
        filename=file_path,
        read_only=True,
        data_only=True,
    )

    if "Final_Annotations" in workbook.sheetnames:
        sheet = workbook["Final_Annotations"]
    else:
        raise ValueError(
            f"{file_path.name} does not contain a Final_Annotations sheet."
        )

    rows = sheet.iter_rows(values_only=True)

    headers = next(rows)

    header_map = {
        str(header).strip(): index
        for index, header in enumerate(headers)
        if header is not None
    }

    required_columns = {
        "paper_id",
        "claim_id",
        "claim_text",
        "page",
        "section",
        "claim_type",
        "citation_ids",
        "is_checkable",
        "notes",
    }

    missing = required_columns - set(header_map)

    if missing:
        raise ValueError(
            f"{file_path.name} is missing columns: {sorted(missing)}"
        )

    claims = []

    for row in rows:
        claim_text = row[header_map["claim_text"]]

        if claim_text is None:
            continue

        claims.append(
            GoldClaim(
                paper_id=str(row[header_map["paper_id"]]),
                claim_id=str(row[header_map["claim_id"]]),
                claim_text=str(claim_text),
                page=(
                    int(row[header_map["page"]])
                    if row[header_map["page"]] is not None
                    else None
                ),
                section=str(row[header_map["section"]]),
                claim_type=str(row[header_map["claim_type"]]),
                citation_ids=str(row[header_map["citation_ids"]]),
                is_checkable=bool(row[header_map["is_checkable"]]),
                notes=str(row[header_map["notes"]]),
            )
        )

    workbook.close()

    return claims