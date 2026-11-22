
const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

// Handle API responses
async function handleResponse(response) {
    let data;

    try {
        data = await response.json();
    } catch (_) {
        throw new Error(
            `Server returned an invalid response (${response.status})`
        );
    }

    if (!response.ok) {
        let message = `Request failed (${response.status})`;

        if (typeof data.detail === "string") {
            message = data.detail;
        } else if (Array.isArray(data.detail)) {
            message = data.detail.map(d => d.msg).join(", ");
        }

        throw new Error(message);
    }

    return data;
}

// Upload PDF and index it in ChromaDB
export async function uploadPDF(file) {
    const formData = new FormData();

    // Must match FastAPI parameter: file
    formData.append("file", file);

    const response = await fetch(
        `${API_BASE_URL}/documents/upload`,
        {
            method: "POST",
            body: formData
        }
    );

    return handleResponse(response);
}

// Ask questions about an indexed PDF
export async function sendChatMessage(question, documentId) {
    const response = await fetch(
        `${API_BASE_URL}/chat`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                document_id: documentId
            })
        }
    );

    return handleResponse(response);
}
