/**
 * AgriSmart System - Client-Side Application Controller
 * Handles SPA navigation, real-time multilingual translations,
 * crop disease diagnosis, voice recording, speech-to-text, and audio narration.
 */

document.addEventListener("DOMContentLoaded", () => {
    // State management
    const state = {
        currentLang: "English",
        currentPage: "home",
        chatMessages: [],
        selectedImageFile: null,
        mediaRecorder: null,
        audioChunks: [],
        isRecording: false,
        translations: {}
    };

    // DOM Elements
    const elements = {
        langSelect: document.getElementById("lang-select"),
        viewHome: document.getElementById("view-home"),
        viewDisease: document.getElementById("view-disease"),
        viewChatbot: document.getElementById("view-chatbot"),
        btnLaunchDisease: document.getElementById("btn-launch-disease"),
        btnLaunchBot: document.getElementById("btn-launch-bot"),
        navLogo: document.getElementById("nav-logo"),
        fileInput: document.getElementById("leaf-file-input"),
        dropZone: document.getElementById("upload-dropzone"),
        previewContainer: document.getElementById("preview-container"),
        previewImg: document.getElementById("preview-img"),
        btnRunDiagnosis: document.getElementById("btn-run-diagnosis"),
        diagnosisSpinner: document.getElementById("diagnosis-spinner"),
        diagnosisBtnText: document.getElementById("diagnosis-btn-text"),
        resultContainer: document.getElementById("result-container"),
        resultStatus: document.getElementById("result-status"),
        resultDiseaseName: document.getElementById("result-disease-name"),
        treatmentReport: document.getElementById("treatment-report"),
        chatHistory: document.getElementById("chat-history"),
        chatInput: document.getElementById("chat-input"),
        btnSendMessage: document.getElementById("btn-send-message"),
        btnRecordVoice: document.getElementById("btn-record-voice"),
        voiceStatus: document.getElementById("voice-status"),
        voiceFileInput: document.getElementById("voice-file-input")
    };

    // --- NAVIGATION CONTROLLER ---
    function navigateTo(pageId) {
        state.currentPage = pageId;
        document.querySelectorAll(".view-panel").forEach(panel => panel.classList.remove("active"));
        
        if (pageId === "home") {
            elements.viewHome.classList.add("active");
        } else if (pageId === "disease") {
            elements.viewDisease.classList.add("active");
        } else if (pageId === "chatbot") {
            elements.viewChatbot.classList.add("active");
            scrollToBottom();
        }
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    document.querySelectorAll(".btn-back").forEach(btn => {
        btn.addEventListener("click", () => navigateTo("home"));
    });

    elements.btnLaunchDisease?.addEventListener("click", () => navigateTo("disease"));
    elements.btnLaunchBot?.addEventListener("click", () => navigateTo("chatbot"));
    elements.navLogo?.addEventListener("click", () => navigateTo("home"));

    // --- TRANSLATION CONTROLLER ---
    async function loadTranslations(lang) {
        state.currentLang = lang;
        try {
            const response = await fetch("/api/translate-ui", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ lang })
            });
            if (response.ok) {
                state.translations = await response.json();
                applyTranslations();
            }
        } catch (err) {
            console.error("Translation fetch error:", err);
        }
    }

    function _t(key) {
        return state.translations[key] || key;
    }

    function applyTranslations() {
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (state.translations[key]) {
                el.textContent = state.translations[key];
            }
        });

        document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
            const key = el.getAttribute("data-i18n-placeholder");
            if (state.translations[key]) {
                el.placeholder = state.translations[key];
            }
        });
    }

    elements.langSelect?.addEventListener("change", (e) => {
        loadTranslations(e.target.value);
    });

    // --- CROP DISEASE DETECTION ---
    elements.dropZone?.addEventListener("click", () => elements.fileInput.click());

    elements.dropZone?.addEventListener("dragover", (e) => {
        e.preventDefault();
        elements.dropZone.classList.add("dragover");
    });

    elements.dropZone?.addEventListener("dragleave", () => {
        elements.dropZone.classList.remove("dragover");
    });

    elements.dropZone?.addEventListener("drop", (e) => {
        e.preventDefault();
        elements.dropZone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleImageSelection(e.dataTransfer.files[0]);
        }
    });

    elements.fileInput?.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleImageSelection(e.target.files[0]);
        }
    });

    function handleImageSelection(file) {
        state.selectedImageFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            elements.previewImg.src = e.target.result;
            elements.previewContainer.style.display = "block";
            elements.resultContainer.style.display = "none";
        };
        reader.readAsDataURL(file);
    }

    elements.btnRunDiagnosis?.addEventListener("click", async () => {
        if (!state.selectedImageFile) return;

        elements.btnRunDiagnosis.disabled = true;
        elements.diagnosisSpinner.style.display = "inline-block";
        elements.diagnosisBtnText.textContent = _t("Analyzing specimen through botanical diagnostic database...");

        const formData = new FormData();
        formData.append("image", state.selectedImageFile);
        formData.append("lang", state.currentLang);

        try {
            const response = await fetch("/api/diagnose", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            elements.resultContainer.style.display = "block";

            if (data.status === "healthy") {
                elements.resultStatus.className = "result-card healthy";
                elements.resultStatus.style.display = "block";
                elements.resultStatus.innerHTML = `<strong>🌱 ${data.message}</strong>`;
                elements.resultDiseaseName.style.display = "none";
                elements.treatmentReport.style.display = "none";
            } else if (data.status === "infected") {
                elements.resultStatus.className = "result-card infected";
                elements.resultStatus.style.display = "block";
                elements.resultStatus.innerHTML = `<strong>⚠️ ${data.message}</strong>`;

                elements.resultDiseaseName.style.display = "block";
                elements.resultDiseaseName.innerHTML = `${_t("Diagnosed Crop Disease")}: <strong>${data.translated_disease || data.disease}</strong>`;

                elements.treatmentReport.style.display = "block";
                elements.treatmentReport.innerHTML = data.treatment_html || data.treatment_markdown;
            } else {
                elements.resultStatus.className = "result-card infected";
                elements.resultStatus.style.display = "block";
                elements.resultStatus.innerHTML = `<strong>❌ ${data.message || "Diagnosis Failed"}</strong>`;
                elements.resultDiseaseName.style.display = "none";
                elements.treatmentReport.style.display = "none";
            }
        } catch (err) {
            elements.resultContainer.style.display = "block";
            elements.resultStatus.className = "result-card infected";
            elements.resultStatus.style.display = "block";
            elements.resultStatus.innerHTML = `<strong>Network Error: ${err.message}</strong>`;
        } finally {
            elements.btnRunDiagnosis.disabled = false;
            elements.diagnosisSpinner.style.display = "none";
            elements.diagnosisBtnText.textContent = _t("Run Disease Diagnosis Engine");
        }
    });

    // --- AGRIBOT CONVERSATIONAL CHATBOT ---
    function appendChatMessage(role, content) {
        state.chatMessages.push({ role, content });

        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${role}`;

        const senderTag = document.createElement("div");
        senderTag.className = "chat-sender-tag";
        senderTag.textContent = role === "user" ? "Farmer" : "AgriBot Assistant";
        bubble.appendChild(senderTag);

        const contentDiv = document.createElement("div");
        contentDiv.innerHTML = content.replace(/\n/g, "<br>");
        bubble.appendChild(contentDiv);

        if (role === "assistant") {
            const actionsDiv = document.createElement("div");
            actionsDiv.className = "chat-actions";

            const ttsBtn = document.createElement("button");
            ttsBtn.className = "btn-tts";
            ttsBtn.innerHTML = "🔊 " + _t("Listen to Response");
            ttsBtn.addEventListener("click", () => playTts(content, ttsBtn));

            actionsDiv.appendChild(ttsBtn);
            bubble.appendChild(actionsDiv);
        }

        elements.chatHistory.appendChild(bubble);
        scrollToBottom();
    }

    function scrollToBottom() {
        elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
    }

    async function sendChatMessage(text) {
        const messageText = text || elements.chatInput.value.trim();
        if (!messageText) return;

        appendChatMessage("user", messageText);
        elements.chatInput.value = "";

        const typingBubble = document.createElement("div");
        typingBubble.className = "chat-bubble assistant";
        typingBubble.id = "typing-indicator";
        typingBubble.innerHTML = `<span class="spinner" style="border-top-color: var(--accent-emerald);"></span> <em>Analyzing agricultural knowledge arrays...</em>`;
        elements.chatHistory.appendChild(typingBubble);
        scrollToBottom();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    messages: state.chatMessages,
                    lang: state.currentLang
                })
            });

            const data = await response.json();
            typingBubble.remove();

            if (data.reply) {
                appendChatMessage("assistant", data.reply);
            } else {
                appendChatMessage("assistant", `Error: ${data.error || "Failed to get response"}`);
            }
        } catch (err) {
            typingBubble.remove();
            appendChatMessage("assistant", `Connection error: ${err.message}`);
        }
    }

    elements.btnSendMessage?.addEventListener("click", () => sendChatMessage());
    elements.chatInput?.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            sendChatMessage();
        }
    });

    // --- TEXT TO SPEECH ---
    async function playTts(text, buttonElement) {
        const originalText = buttonElement.innerHTML;
        buttonElement.disabled = true;
        buttonElement.innerHTML = `<span class="spinner"></span> ${_t("Generating audio narration...")}`;

        try {
            const response = await fetch("/api/tts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text, lang: state.currentLang })
            });

            if (response.ok) {
                const blob = await response.blob();
                const audioUrl = URL.createObjectURL(blob);
                const audio = new Audio(audioUrl);
                audio.play();
                audio.onended = () => {
                    buttonElement.disabled = false;
                    buttonElement.innerHTML = originalText;
                };
            } else {
                alert("TTS Audio generation failed.");
                buttonElement.disabled = false;
                buttonElement.innerHTML = originalText;
            }
        } catch (err) {
            console.error("TTS Error:", err);
            buttonElement.disabled = false;
            buttonElement.innerHTML = originalText;
        }
    }

    // --- VOICE RECORDING & TRANSCRIPTION ---
    elements.btnRecordVoice?.addEventListener("click", async () => {
        if (!state.isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    async function startRecording() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Microphone recording is not supported in this browser. Please upload an audio file instead.");
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            state.audioChunks = [];
            state.mediaRecorder = new MediaRecorder(stream);

            state.mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) state.audioChunks.push(e.data);
            };

            state.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(state.audioChunks, { type: "audio/webm" });
                stream.getTracks().forEach(track => track.stop());
                await submitAudioTranscription(audioBlob);
            };

            state.mediaRecorder.start();
            state.isRecording = true;
            elements.btnRecordVoice.classList.add("recording");
            elements.btnRecordVoice.innerHTML = "⏹️ Stop Recording";
            elements.voiceStatus.textContent = "Listening... Speak now";
        } catch (err) {
            console.error("Microphone access error:", err);
            alert("Microphone permission denied or unavailable. You can use audio file upload below.");
        }
    }

    function stopRecording() {
        if (state.mediaRecorder && state.isRecording) {
            state.mediaRecorder.stop();
            state.isRecording = false;
            elements.btnRecordVoice.classList.remove("recording");
            elements.btnRecordVoice.innerHTML = "🎙️ Start Voice Input";
            elements.voiceStatus.textContent = "Processing speech transcription via Gemini...";
        }
    }

    elements.voiceFileInput?.addEventListener("change", async (e) => {
        if (e.target.files && e.target.files[0]) {
            elements.voiceStatus.textContent = "Processing speech transcription via Gemini...";
            await submitAudioTranscription(e.target.files[0]);
        }
    });

    async function submitAudioTranscription(audioBlob) {
        const formData = new FormData();
        formData.append("audio", audioBlob, "voice_input.webm");

        try {
            const response = await fetch("/api/transcribe", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            if (data.transcription) {
                elements.voiceStatus.textContent = `Recognized: "${data.transcription}"`;
                sendChatMessage(data.transcription);
            } else {
                elements.voiceStatus.textContent = data.error || "No speech could be recognized.";
            }
        } catch (err) {
            elements.voiceStatus.textContent = `Transcription failed: ${err.message}`;
        }
    }

    // Initialize with default welcoming message
    appendChatMessage(
        "assistant",
        "Welcome! I am your AI Agronomy Assistant. How can I assist you with your crops and farming decisions today?"
    );

    // Initial translation load
    loadTranslations("English");
});

