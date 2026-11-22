# Cognifile AI – Backend (service-ai)

A Python **FastAPI** service for PDF question answering (RAG). It extracts text from an uploaded PDF, splits it into chunks, embeds them with Google Gemini, stores them in **ChromaDB**, and answers questions using only the retrieved context, with page references.

## Tech stack

- Python 3.12+
- FastAPI + Uvicorn
- LangChain (`langchain-google-genai`, `langchain-chroma`, `langchain-text-splitters`)
- ChromaDB (local vector store)
- PyMuPDF (PDF text extraction)
- Google Gemini (chat model and embeddings)
- [uv](https://docs.astral.sh/uv/) for dependency management

## How it works

```
Upload PDF → extract text (PyMuPDF) → chunk (1000 chars, 200 overlap)
          → embed (Gemini) → store in ChromaDB (data/chroma)

Question → embed question → retrieve top 4 chunks for that document_id
        → Gemini answers from the context only → answer + page sources
```

## Project structure

```
service-ai/
├── app/
│   ├── main.py                  # FastAPI app, CORS, routers, /health
│   ├── core/config.py           # Settings loaded from .env
│   ├── api/routes/
│   │   ├── documents.py         # POST upload, POST summary
│   │   └── chat.py              # POST chat
│   ├── schemas/chat.py          # Request/response models
│   ├── rag/
│   │   ├── loaders/pdf_loader.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   └── pipeline.py          # RAG answer generation
│   ├── llm/provider.py          # Gemini chat model
│   └── services/summary_service.py
├── data/                        # Created at runtime (git-ignored)
│   ├── chroma/                  # Vector database
│   └── uploads/
├── pyproject.toml
├── uv.lock
└── .env                         # Secrets (never commit)
```

## Setup

### 1. Install uv

```bash
pip install uv
```

### 2. Install dependencies

```bash
cd service-ai
uv sync
```

### 3. Create the `.env` file

Get an API key from [Google AI Studio](https://aistudio.google.com/apikey), then create `.env` in the `service-ai` folder:

```env
GOOGLE_API_KEY=your_api_key_here
APP_ENV=development
PRIMARY_MODEL=gemini-3.8-flash
```

> Never commit `.env`. Check the model name against the [Gemini models list](https://ai.google.dev/gemini-api/docs/models) if you get model errors.

## Run

```bash
uv run uvicorn app.main:app --reload
```

- API: <http://127.0.0.1:8000>
- Interactive docs (Swagger): <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

Restart the server after changing `.env`, because settings are cached.

## API endpoints

All routes below are prefixed with `/api/v1`.

| Method | Endpoint                          | Description                          |
| ------ | --------------------------------- | ------------------------------------ |
| GET    | `/health` (no prefix)             | Service status                       |
| POST   | `/api/v1/documents/upload`        | Upload and index a PDF (max 10 MB)   |
| POST   | `/api/v1/documents/{id}/summary`  | Summarize an indexed PDF             |
| POST   | `/api/v1/chat`                    | Ask a question about an indexed PDF  |

### Upload a PDF

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "file=@notes.pdf"
```

Response:

```json
{
  "document_id": "d34c75b0-c06d-4bde-bdc1-37885b0bd64a",
  "filename": "notes.pdf",
  "total_pages": 12,
  "total_chunks": 48,
  "status": "indexed"
}
```

### Chat with the PDF

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "document_id": "<document_id>"}'
```

Response:

```json
{
  "answer": "...",
  "document_id": "<document_id>",
  "sources": [{ "page_number": 3, "document_name": "notes.pdf" }]
}
```

### Summarize

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/<document_id>/summary
```

## Useful commands

| Task | Command |
| ---- | ------- |
| Install dependencies | `uv sync` |
| Add a package | `uv add <package>` |
| Run the server (dev) | `uv run uvicorn app.main:app --reload` |
| Run on another port | `uv run uvicorn app.main:app --reload --port 8001` |
| Run in production mode | `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Reset all indexed data | Stop the server, then delete `data/chroma` |

Quick test of the Gemini connection (embeddings and chat model):

```bash
uv run python -c "
from app.rag.embeddings import get_embeddings
from app.llm.provider import get_llm
print('EMBED OK', len(get_embeddings().embed_query('hello')))
print('LLM OK', get_llm().invoke('say hi').content)
"
```

## CORS

The backend only accepts requests from these frontend origins (set in `app/main.py`):

- `http://127.0.0.1:5500`
- `http://localhost:5500`

Add your own origin to `allow_origins` if you serve the frontend elsewhere or deploy it.

## Troubleshooting

| Problem | Fix |
| ------- | --- |
| `502 Bad Gateway` | A generic error. Read the traceback in the uvicorn terminal. Common causes: invalid or over-quota API key, wrong model name |
| `ValidationError: GOOGLE_API_KEY` on start | `.env` is missing or not in the `service-ai` folder |
| CORS error in the browser | Serve the frontend from port 5500 or update `allow_origins` |
| "PDF contains no extractable text" | The PDF is scanned images. It needs OCR first |
| "No indexed content was found" | Upload the PDF again, because the `document_id` is not in the database |
| Changed `.env` but nothing changed | Restart uvicorn |

## Security notes

- `.env`, `.venv/` and `data/` are git-ignored. Keep it that way.
- If an API key was ever shared or committed, rotate it in Google AI Studio.
- Uploads are limited to PDFs of 10 MB or less, and the file header is validated.