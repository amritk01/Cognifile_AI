
import logging

from fastapi import APIRouter, HTTPException

from app.rag.pipeline import generate_rag_answer
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

logger = logging.getLogger(__name__)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        return await generate_rag_answer(
            question=request.question,
            document_id=request.document_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except Exception:
        logger.exception("RAG chat request failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to generate a document answer"
        )
