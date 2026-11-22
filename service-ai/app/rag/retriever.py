
from pydantic import BaseModel, Field

from app.rag.vector_store import get_vector_store


class RetrievedChunk(BaseModel):
    text: str
    document_id: str
    filename: str
    page_number: int = Field(ge=1)
    distance: float


def retrieve_chunks(
    question: str,
    document_id: str,
    top_k: int = 4,
) -> list[RetrievedChunk]:

    if not question.strip():
        raise ValueError("Question cannot be empty")

    if not document_id.strip():
        raise ValueError("Document ID cannot be empty")

    if top_k < 1:
        raise ValueError("top_k must be positive")

    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_score(
        query=question,
        k=top_k,
        filter={"document_id": document_id},
    )

    chunks = []

    for document, distance in results:
        chunks.append(
            RetrievedChunk(
                text=document.page_content,
                document_id=document.metadata["document_id"],
                filename=document.metadata["filename"],
                page_number=int(
                    document.metadata["page_number"]
                ),
                distance=float(distance),
            )
        )

    return chunks
