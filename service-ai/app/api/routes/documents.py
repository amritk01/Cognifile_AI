
import asyncio
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.rag.chunking import chunk_pdf
from app.rag.loaders.pdf_loader import extract_pdf_text
from app.rag.vector_store import store_chunks

from pydantic import BaseModel

from app.services.summary_service import generate_document_summary

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    temp_path = None

    try:
        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="PDF must be 10 MB or smaller"
            )

        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file"
            )

        with NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        document_id = str(uuid4())

        # 1. Extract PDF text
        document = await asyncio.to_thread(
            extract_pdf_text,
            temp_path
        )

        # 2. Split into chunks
        chunks = await asyncio.to_thread(
            chunk_pdf,
            document,
            document_id
        )

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="PDF contains no extractable text"
            )

        # 3. Generate embeddings and store in ChromaDB
        stored_count = await asyncio.to_thread(
            store_chunks,
            chunks,
            filename
        )

        # 4. Return indexed document details
        return {
            "document_id": document_id,
            "filename": filename,
            "total_pages": document.total_pages,
            "total_chunks": stored_count,
            "status": "indexed"
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("PDF indexing failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to index PDF document"
        )

    finally:
        await file.close()

        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


class SummaryResponse(BaseModel):
    document_id: str
    summary: str
    sections_processed: int
    status: str


@router.post(
    "/{document_id}/summary",
    response_model=SummaryResponse,
)
async def summarize_document(document_id: str):
    try:
        result = await generate_document_summary(
            document_id=document_id
        )

        return SummaryResponse(**result)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception:
        logger.exception("PDF summarization failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to generate PDF summary",
        )
