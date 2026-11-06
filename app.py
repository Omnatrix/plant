import os
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import uvicorn

from modules.chatbot import call_gemini_chat, generate_tts_audio, transcribe_audio_with_gemini
from modules.disease_detection import diagnose_crop_image
from utils.translator_api import LANGUAGES, get_ui_translations

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


async def home_view(request):
    """Renders the main single-page application dashboard."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"languages": LANGUAGES},
    )


async def translate_ui_api(request):
    """Returns pre-computed dictionary translations for real-time UI localization."""
    try:
        body = await request.json()
        target_lang = body.get("lang", "English")
        translations = get_ui_translations(target_lang)
        return JSONResponse(translations)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def diagnose_api(request):
    """Analyzes an uploaded leaf image and returns disease diagnosis and treatment protocols."""
    try:
        form = await request.form()
        image_file = form.get("image")
        lang = form.get("lang", "English")

        if not image_file:
            return JSONResponse({"status": "error", "message": "No leaf image provided."}, status_code=400)

        image_bytes = await image_file.read()
        result = diagnose_crop_image(image_bytes, target_lang=lang)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


async def chat_api(request):
    """Processes conversational messages with the AgriBot agronomy assistant."""
    try:
        body = await request.json()
        messages = body.get("messages", [])
        lang = body.get("lang", "English")

        if not messages:
            return JSONResponse({"error": "Empty message array."}, status_code=400)

        reply = call_gemini_chat(messages, current_lang=lang)
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def transcribe_api(request):
    """Transcribes spoken user audio into text using Google Gemini Multimodal API."""
    try:
        form = await request.form()
        audio_file = form.get("audio")

        if not audio_file:
            return JSONResponse({"error": "No audio file provided."}, status_code=400)

        audio_bytes = await audio_file.read()
        mime_type = audio_file.content_type or "audio/wav"
        transcription = transcribe_audio_with_gemini(audio_bytes, mime_type=mime_type)

        return JSONResponse({"transcription": transcription})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def tts_api(request):
    """Generates streaming MP3 audio narration using gTTS for assistant responses."""
    try:
        body = await request.json()
        text = body.get("text", "")
        lang = body.get("lang", "English")

        if not text:
            return JSONResponse({"error": "No text provided for audio narration."}, status_code=400)

        audio_bytes = generate_tts_audio(text, current_lang=lang)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ASGI Application Route Definitions
routes = [
    Route("/", endpoint=home_view, methods=["GET"]),
    Route("/api/translate-ui", endpoint=translate_ui_api, methods=["POST"]),
    Route("/api/diagnose", endpoint=diagnose_api, methods=["POST"]),
    Route("/api/chat", endpoint=chat_api, methods=["POST"]),
    Route("/api/transcribe", endpoint=transcribe_api, methods=["POST"]),
    Route("/api/tts", endpoint=tts_api, methods=["POST"]),
    Mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static"),
]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8501))
    print(f"🌱 AgriSmart System starting at http://localhost:{port}")
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=True)
