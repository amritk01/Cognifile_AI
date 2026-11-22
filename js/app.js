
import { initializeUpload } from "./upload.js";
import { initializeChat, resetChat } from "./chat.js";

// Initialize Cognifile AI
document.addEventListener("DOMContentLoaded", () => {
    initializeUpload(resetChat);
    initializeChat();

    console.log("Cognifile AI frontend initialized");
});
