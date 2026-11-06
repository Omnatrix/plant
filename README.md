# 🌱 AgriSmart System

AgriSmart is an AI-powered agricultural technology platform focused on crop health diagnostics and multilingual advisory services for farmers.

---

## ✨ Key Features

*   **🍂 Crop Disease Detection:** Upload leaf specimen photographs to instantly detect crop pathogens and structural infections via the Plant.id botanical vision engine, followed by dynamic, AI-generated organic and chemical treatment protocols.
*   **🤖 AgriBot Conversational Assistant:** An expert agronomy chatbot powered by Google Gemini with integrated multimodal voice input and native speech synthesis (gTTS), providing actionable farming, treatment, and crop care advice.
*   **🌍 Universal Multilingual Support:** Comprehensive support across all 22 Scheduled Official Languages of India + English via an offline high-accuracy dictionary and dynamic translation.

---

## 🛠️ Technology Stack

*   **Frontend:** HTML5, Modern CSS3, Vanilla JavaScript (Fast SPA)
*   **Backend & Server:** Starlette & Uvicorn (Python ASGI)
*   **AI Engine:** Google Gemini API (`gemini-3.1-flash-lite`, `gemini-3.5-flash`)
*   **Plant Pathology API:** Kindwise Crop.health / Plant.id API
*   **Speech Synthesis:** gTTS (Google Text-to-Speech)
*   **Translation Engine:** Pre-computed 22-language translation map + fallback

---

## 🚀 Installation & Usage

**1. Clone the repository**
```bash
git clone https://github.com/Ankit-84/AgriSmart_System.git
cd AgriSmart_System
```

**2. Set up your environment variables**
Create a `.env` file in the root directory and add your API keys:
```env
GEMINI_API_KEY="your_gemini_api_key"
PLANT_ID_API_KEY="your_crop_health_or_plant_id_api_key"
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the application**
```bash
python app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.
