
import { sendChatMessage } from "./api.js";
import { getActiveDocument } from "./upload.js";

let chatMessages;
let messageInput;
let chatForm;
let isSending = false;

export function initializeChat() {
    chatForm = document.getElementById("chat-form");
    messageInput = document.getElementById("message-input");
    chatMessages = document.getElementById("chat-messages");

    if (!chatForm || !messageInput || !chatMessages) return;

    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (isSending) return;

        const question = messageInput.value.trim();
        const activeDoc = getActiveDocument();

        if (!question) return;

        if (!activeDoc) {
            alert("Please upload a PDF first.");
            return;
        }

        addMessage(question, "user");

        messageInput.value = "";
        isSending = true;

        const sendButton = chatForm.querySelector(
            'button[type="submit"]'
        );

        if (sendButton) sendButton.disabled = true;

        showLoading();

        try {
            const result = await sendChatMessage(
                question,
                activeDoc.id
            );

            hideLoading();

            // Supports common answer field names.
            // Confirm exact field in ChatResponse schema.
            const answer =
                result.answer ??
                result.response ??
                result.message;

            if (typeof answer !== "string") {
                throw new Error(
                    "Chat response has no supported answer field."
                );
            }

            addMessage(answer, "ai", result.sources);

        } catch (error) {
            hideLoading();

            console.error("Chat request failed:", error);

            addMessage(
                `Unable to get an AI response: ${error.message}`,
                "ai"
            );

        } finally {
            isSending = false;

            if (sendButton) sendButton.disabled = false;

            messageInput.focus();
        }
    });
}

// Add user or AI message
function addMessage(text, type, sources = []) {
    const welcome = chatMessages.querySelector(":scope > p");

    if (welcome) welcome.remove();

    const messageElement = document.createElement("div");

    messageElement.className =
        `message ${type === "user" ? "user-message" : "ai-message"}`;

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = text;

    messageElement.appendChild(content);

    // Display page references if backend provides them
    if (type === "ai" && Array.isArray(sources)) {
        const pages = [
            ...new Set(
                sources
                    .map(source =>
                        source.page ?? source.page_number
                    )
                    .filter(page => page !== undefined && page !== null)
            )
        ];

        if (pages.length > 0) {
            const sourceElement = document.createElement("div");

            sourceElement.className = "message-source";
            sourceElement.textContent =
                `Source: Page ${pages.join(", ")}`;

            messageElement.appendChild(sourceElement);
        }
    }

    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// Loading indicator
function showLoading() {
    hideLoading();

    const loading = document.createElement("div");

    loading.id = "ai-loading";
    loading.className = "loading-message";

    loading.innerHTML = `
        <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    chatMessages.appendChild(loading);
    scrollToBottom();
}

function hideLoading() {
    document.getElementById("ai-loading")?.remove();
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Reset chat when a different PDF is uploaded
export function resetChat() {
    if (!chatMessages) return;

    chatMessages.replaceChildren();

    const welcome = document.createElement("p");
    welcome.textContent = "PDF ready! Ask your first question.";

    chatMessages.appendChild(welcome);
}
