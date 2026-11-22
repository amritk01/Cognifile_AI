
from pydantic import BaseModel
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.loaders.pdf_loader import PDFContent


class TextChunk(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int
    text: str


def chunk_pdf(
    document: PDFContent,
    document_id: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[TextChunk]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = []

    for page in document.pages:
        if not page.text.strip():
            continue

        page_chunks = splitter.split_text(page.text)

        for index, text in enumerate(page_chunks):
            chunks.append(
                TextChunk(
                    chunk_id=(
                        f"{document_id}_p{page.page_number}_c{index}"
                    ),
                    document_id=document_id,
                    page_number=page.page_number,
                    text=text
                )
            )

    return chunks
