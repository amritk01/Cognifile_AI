
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings


@lru_cache
def get_llm() -> ChatGoogleGenerativeAI:
    settings = get_settings()

    return ChatGoogleGenerativeAI(
        model=settings.PRIMARY_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
        max_retries=settings.MAX_RETRIES,
    )
