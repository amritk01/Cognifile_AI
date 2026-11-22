
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Python AI and RAG backend for Cognifile",
    version="0.1.0"
)

# Allow frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Register Chat API
app.include_router(
    chat_router,
    prefix="/api/v1"
)

# Register PDF Upload API
app.include_router(
    documents_router,
    prefix="/api/v1"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV
    }
