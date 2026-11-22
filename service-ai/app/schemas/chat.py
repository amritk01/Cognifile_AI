
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question about a document"
    )

    document_id: str = Field(
        ...,
        min_length=1,
        description="ID of the document"
    )

class SourceReference(BaseModel):
    page_number: int = Field(ge=1)
    document_name: str


class ChatResponse(BaseModel):
    answer: str
    document_id: str
    sources: list[SourceReference] = Field(
        default_factory=list
    )
