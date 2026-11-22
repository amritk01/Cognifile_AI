
from pathlib import Path

import pymupdf
from pydantic import BaseModel


class PDFPage(BaseModel):
    page_number: int
    text: str


class PDFContent(BaseModel):
    filename: str
    total_pages: int
    pages: list[PDFPage]


def extract_pdf_text(file_path: str | Path) -> PDFContent:
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"PDF file not found: {path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported")

    pages = []

    with pymupdf.open(path) as document:
        if not document.is_pdf:
            raise ValueError("Invalid PDF document")

        total_pages = len(document)

        for page_index, page in enumerate(document):
            text = page.get_text("text", sort=True)

            pages.append(
                PDFPage(
                    page_number=page_index + 1,
                    text=text.strip()
                )
            )

    return PDFContent(
        filename=path.name,
        total_pages=total_pages,
        pages=pages
    )
