import io
import os
from gtts import gTTS

# Map all 22 Indian UI languages to optimal gTTS phonetic language codes
GTTS_LANG_MAP = {
    "English": "en",
    "Assamese": "bn",
    "Bengali": "bn",
    "Bodo": "hi",
    "Dogri": "hi",
    "Gujarati": "gu",
    "Hindi": "hi",
    "Kannada": "kn",
    "Kashmiri": "ur",
    "Konkani": "mr",
    "Maithili": "hi",
    "Malayalam": "ml",
    "Manipuri (Meitei)": "bn",
    "Marathi": "mr",
    "Nepali": "ne",
    "Odia (Oriya)": "hi",
    "Punjabi": "pa",
    "Sanskrit": "hi",
    "Santali": "hi",
    "Sindhi": "ur",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur",
}

ACTIVE_GEMINI_MODELS = (
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-flash-latest",
)


def _get_gemini_client():
    """Retrieve an authenticated Google GenAI client."""
    from google import genai

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip().strip("'\"")
    if not gemini_key:
        return None
    return genai.Client(api_key=gemini_key)


def call_gemini_chat(messages: list[dict], current_lang: str = "English") -> str:
    """Generates chat responses using Google GenAI SDK with active Gemini models."""
    client = _get_gemini_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is not configured.")

    system_instruction = (
        "You are an expert agronomy consultant assisting Indian farmers. "
        "Give clear, direct advice on crop care, plant diseases, fertilizer dosing, and soil treatment. "
        "Keep answers structural, precise, and practical. "
        f"CRITICAL RULE: If the user communicates in {current_lang} or a regional Indian language, "
        "you must reply in that exact same language using the native script."
    )

    # Format message history into a clean conversation prompt
    prompt_lines = [f"System Instruction: {system_instruction}\n", "Conversation History:"]
    for msg in messages:
        if msg.get("role") != "system":
            sender = "Farmer" if msg.get("role") == "user" else "AgriBot"
            prompt_lines.append(f"{sender}: {msg.get('content', '')}")
    prompt_lines.append("AgriBot:")
    prompt = "\n".join(prompt_lines)

    last_err = None
    for model_name in ACTIVE_GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            continue

    raise last_err or RuntimeError("All Gemini models were unavailable.")


def transcribe_audio_with_gemini(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """Transcribes user voice input into text using Google Gemini Multimodal API."""
    from google.genai import types

    client = _get_gemini_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is not configured.")

    part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
    prompt = (
        "Accurately transcribe the spoken words in this audio into text. "
        "Transcribe in the language spoken. Return ONLY the transcribed text without extra commentary, quotes, or notes."
    )

    last_err = None
    for model_name in ACTIVE_GEMINI_MODELS[:4]:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[part, prompt],
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            last_err = e
            continue

    raise last_err or RuntimeError("Voice transcription with Gemini failed.")


def generate_tts_audio(text: str, current_lang: str = "English") -> bytes:
    """Generates MP3 audio narration bytes using gTTS."""
    tts_lang_code = GTTS_LANG_MAP.get(current_lang, "hi" if current_lang != "English" else "en")
    tts = gTTS(text=text, lang=tts_lang_code, slow=False)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    return buffer.getvalue()
