# Cognifile AI – Frontend

A lightweight web UI for **Cognifile AI**. Upload a PDF, then chat with it. Answers come from the FastAPI + RAG backend (`service-ai`) and include page references.

Built with plain HTML, CSS and JavaScript (ES modules). No build step and no dependencies.

## Features

- Upload a PDF (up to 10 MB) with validation
- Automatic indexing through the backend
- Chat with the uploaded document
- Source page references on answers
- Loading indicator and clear error messages

## Project structure

```
frontend/
├── index.html
├── css/
│   └── style.css
└── js/
    ├── app.js      # entry point
    ├── api.js      # backend calls (upload, chat)
    ├── upload.js   # PDF upload + active document state
    └── chat.js     # chat UI logic
```

## Prerequisites

- The backend (`service-ai`) running at `http://127.0.0.1:8000`
- A way to serve static files on **port 5500**, such as the VS Code *Live Server* extension or Python

> The backend only allows CORS from `http://127.0.0.1:5500` and `http://localhost:5500`. Opening `index.html` directly (`file://`) or using another port will be blocked.

## Run locally

1. Start the backend:

   ```bash
   cd service-ai
   uv run uvicorn app.main:app --reload
   ```

2. Serve the frontend on port 5500:

   ```bash
   cd frontend
   python -m http.server 5500
   ```

   (or click **Go Live** in VS Code Live Server)

3. Open <http://127.0.0.1:5500>
4. Choose a PDF, wait for "Indexed N pages", then ask questions.

## Configuration

The backend URL is set in `js/api.js`:

```js
const API_BASE_URL = "http://127.0.0.1:8000/api/v1";
```

Change it when deploying the backend elsewhere, and add the frontend's origin to `allow_origins` in the backend's `app/main.py`.

## API endpoints used

| Method | Endpoint                    | Purpose                       |
| ------ | --------------------------- | ----------------------------- |
| POST   | `/api/v1/documents/upload`  | Upload and index a PDF        |
| POST   | `/api/v1/chat`              | Ask a question about a PDF    |

## Troubleshooting

| Problem | Fix |
| ------- | --- |
| "Cannot reach the server" | Check the backend is running on port 8000 and the frontend is served on port 5500 |
| CORS error in the console | Serve from `127.0.0.1:5500` or `localhost:5500`, or update the backend CORS list |
| `502 Bad Gateway` on chat | Check the backend terminal for the traceback (usually an invalid API key, quota or model issue) |
| Upload rejected | File must be a real PDF, 10 MB or smaller, with extractable text |