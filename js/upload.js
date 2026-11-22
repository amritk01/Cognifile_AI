import { uploadPDF } from "./api.js";

const MAX_SIZE = 10 * 1024 * 1024; // matches backend limit (10 MB)

let fileInput;
let documentList;
let statusEl;
let activeDocument = null;
let onNewDocument = () => {};

// Used by chat.js to know which PDF to query
export function getActiveDocument() {
    return activeDocument;
}

export function initializeUpload(onDocumentReady) {
    fileInput = document.getElementById("pdf-file");
    documentList = document.getElementById("document-list");
    statusEl = document.getElementById("file-status");

    if (typeof onDocumentReady === "function") {
        onNewDocument = onDocumentReady;
    }

    if (!fileInput) return;

    fileInput.addEventListener("change", handleFileSelected);
}

async function handleFileSelected() {
    const file = fileInput.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
        setStatus("Only PDF files are supported.", true);
        fileInput.value = "";
        return;
    }

    if (file.size > MAX_SIZE) {
        setStatus("PDF must be 10 MB or smaller.", true);
        fileInput.value = "";
        return;
    }

    fileInput.disabled = true;
    setStatus("Uploading and indexing… this can take a moment.");

    try {
        const result = await uploadPDF(file);

        activeDocument = {
            id: result.document_id,
            name: result.filename,
            pages: result.total_pages,
        };

        renderDocument(activeDocument);
        setStatus(`Indexed ${result.total_pages} pages.`);
        onNewDocument();
    } catch (error) {
        console.error("Upload failed:", error);

        const isNetwork = error instanceof TypeError;
        setStatus(
            isNetwork
                ? "Cannot reach the server. Is the backend running on port 8000 and is CORS allowed for this origin?"
                : `Upload failed: ${error.message}`,
            true
        );
    } finally {
        fileInput.disabled = false;
        fileInput.value = ""; // allow re-selecting the same file
    }
}

function renderDocument(doc) {
    documentList.replaceChildren();

    const item = document.createElement("div");
    item.className = "document-item active";

    const icon = document.createElement("span");
    icon.className = "document-icon";
    icon.textContent = "📄";

    const name = document.createElement("span");
    name.className = "document-name";
    name.textContent = doc.name;
    name.title = `${doc.name} (${doc.pages} pages)`;

    item.append(icon, name);
    documentList.appendChild(item);
}

function setStatus(message, isError = false) {
    if (!statusEl) return;
    statusEl.textContent = message;
    statusEl.style.color = isError ? "#ef4444" : "";
}
