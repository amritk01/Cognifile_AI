
from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.rag.chunking import TextChunk
from app.rag.embeddings import get_embeddings


CHROMA_PATH = Path("data/chroma")


@lru_cache
def get_vector_store() -> Chroma:
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name="cognifile_documents",
        embedding_function=get_embeddings(),
        persist_directory=str(CHROMA_PATH),
    )


def store_chunks(
    chunks: list[TextChunk],
    filename: str,
) -> int:
    if not chunks:
        return 0

    documents = [
        Document(
            page_content=chunk.text,
            metadata={
                "document_id": chunk.document_id,
                "page_number": chunk.page_number,
                "filename": filename,
            },
        )
        for chunk in chunks
    ]

    ids = [chunk.chunk_id for chunk in chunks]

    vector_store = get_vector_store()

    vector_store.add_documents(
        documents=documents,
        ids=ids,
    )

    return len(documents)

