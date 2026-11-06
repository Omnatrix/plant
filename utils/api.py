import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACTIVE_GEMINI_MODELS = (
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
)


def _get_api_key(var_name: str) -> str:
    """Safely extracts and strips environment variables."""
    return os.getenv(var_name, "").strip().strip("'\"")


def identify_plant_disease_api(image_bytes: bytes) -> str:
    """
    Sends the image to Kindwise Crop Health or Plant.id API to identify crop diseases and pests.
    Automatically handles both Crop.health API keys and Plant.id API keys.
    """
    api_key = _get_api_key("PLANT_ID_API_KEY")
    if not api_key:
        return "Error: Plant.id / Crop.health API key is missing from the .env file."

    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "images": [f"data:image/jpeg;base64,{base64_image}"],
    }

    crop_url = "https://crop.kindwise.com/api/v1/identification"
    try:
        response = requests.post(crop_url, headers=headers, json=payload, timeout=25)

        # Fallback to api.plant.id if Crop.health returned 401
        if response.status_code == 401:
            plant_url = (
                "https://api.plant.id/v3/health_assessment"
                "?details=disease_details&modifiers=disease_model=full,symptoms=true"
            )
            response = requests.post(plant_url, headers=headers, json=payload, timeout=25)

        if response.status_code in [200, 201]:
            result = response.json().get("result", {})

            # Check if healthy
            is_healthy_obj = result.get("is_healthy")
            if (isinstance(is_healthy_obj, dict) and is_healthy_obj.get("binary") is True) or is_healthy_obj is True:
                return "Healthy Plant"

            # Extract diseases or pests
            disease_data = result.get("disease", {})
            suggestions = disease_data.get("suggestions") or result.get("classification", {}).get("suggestions", [])

            if suggestions:
                top_item = suggestions[0]
                name = top_item.get("name", "Unknown Disease Pathogen")
                scientific = top_item.get("scientific_name")
                if scientific and scientific.lower() != name.lower():
                    return f"{name} ({scientific})"
                return name

            return "Healthy Plant"
        return f"API Error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Network Request Failed: {str(e)}"


def get_default_treatment_protocol(disease_label: str, target_lang: str = "English") -> str:
    """Provides a verified agronomic treatment and management protocol in English or regional Indian languages."""
    if target_lang == "Hindi":
        return f"""### 🛡️ **{disease_label.title()}** के लिए विशेष उपचार एवं रोकथाम रणनीति

#### 🌿 1. प्राकृतिक एवं जैविक उपचार
- **नीम तेल का छिड़काव:** 5 मिलीलीटर शुद्ध नीम का तेल + 2 मिलीलीटर हल्का साबुन प्रति 1 लीटर पानी में घोलें। सुबह या शाम को पत्तियों के ऊपर और नीचे अच्छी तरह छिड़कें (हर 7-10 दिनों में)।
- **बायो-फंगीसाइड:** फंगल बीजाणुओं को रोकने के लिए *ट्राइकोडर्मा विरिडे (Trichoderma viride)* (2-3 ग्राम प्रति लीटर) का छिड़काव करें।
- **बेकिंग सोडा घोल:** 5 ग्राम बेकिंग सोडा को 1 लीटर पानी में मिलाकर पत्ती की सतह का पीएच बदलें।

#### 🧪 2. अनुशंसित रासायनिक कीटनाशक व कवकनाशी
- **कॉपर ऑक्सीक्लोराइड (50% WP @ 2.5-3.0 ग्राम/लीटर)** या **मैंकोजेब (75% WP @ 2 ग्राम/लीटर)** सुरक्षात्मक परत बनाने के लिए।
- **एज़ोक्सिस्ट्रोबिन (23% SC @ 1 मिली/लीटर)** या **डिफेनोकोनाज़ोल (25% EC @ 0.5-1 मिली/लीटर)** आंतरिक संक्रमण के इलाज के लिए।

#### 🚜 3. दीर्घकालिक रोकथाम एवं कृषि पद्धतियां
- **स्वच्छता:** संक्रमित पत्तियों को तुरंत काटकर खेत से दूर जला दें या गड्ढे में दबा दें।
- **ड्रिप सिंचाई:** पत्तियों को गीला रखने से बचें; अधिक नमी फंगस को बढ़ाती है।
- **फसल चक्र:** 2 से 3 मौसम तक गैर-मेजबान फसलों का फसल चक्र अपनाएं।
"""
    elif target_lang == "Bengali":
        return f"""### 🛡️ **{disease_label.title()}** এর জন্য বিশেষ চিকিৎসা ও প্রতিরোধ কৌশল

#### 🌿 ১. প্রাকৃতিক ও জৈব প্রতিকার
- **নিম তেলের স্প্রে:** প্রতি ১ লিটার জলে ৫ মিলি নিম তেল + ২ মিলি তরল সাবান মিশিয়ে পাতার উভয় পাশে স্প্রে করুন।
- **জৈব ছত্রাকনাশক:** রোগ বিস্তার রোধ করতে *ট্রাইকোডার্মা ভিরিডি* (২-৩ গ্রাম/লিটার) প্রয়োগ করুন।

#### 🧪 ২. প্রস্তাবিত রাসায়নিক ছত্রাকনাশক
- **কপার অক্সিক্লোরাইড (৫০% WP @ ২.৫-৩ গ্রাম/লিটার)** অথবা **ম্যানকোজেব (৭৫% WP @ ২ গ্রাম/লিটার)**।
- **অ্যাজোক্সিস্ট্রবিন (২৩% SC @ ১ মিলি/লিটার)**।

#### 🚜 ৩. প্রতিরোধমূলক ব্যবস্থা
- আক্রান্ত পাতা ছাঁটাই করে নিরাপদে ধ্বংস করুন।
- জমিতে জল জমতে দেবেন না।
"""
    elif target_lang == "Telugu":
        return f"""### 🛡️ **{disease_label.title()}** కొరకు ప్రత్యేక చికిత్స మరియు నివారణ వ్యూహం

#### 🌿 1. సహజ & సేంద్రీయ నివారణలు
- **వేప నూనె స్ప్రే:** 1 లీటరు నీటికి 5 మి.లీ వేప నూనె + 2 మి.లీ సబ్బు ద్రావణం కలిపి ఆకులపై పిచికారీ చేయండి.
- **జీవ నియంత్రణ:** *ట్రైకోడెర్మా విరిడే* (2-3 గ్రా/లీ) ఉపయోగించండి.

#### 🧪 2. సిఫార్సు చేయబడిన రసాయన మందులు
- **కాపర్ ఆక్సిక్లోరైడ్ (50% WP @ 2.5-3.0 గ్రా/లీ)** లేదా **మాంకోజెబ్ (75% WP @ 2 గ్రా/లీ)**.
- **అజోక్సిస్ట్రోబిన్ (23% SC @ 1 మి.లీ/లీ)**.

#### 🚜 3. దీర్ఘకాలిక నివారణ పద్ధతులు
- తెగులు సోకిన ఆకులను కత్తిరించి నాశనం చేయండి.
- డ్రిప్ ఇరిగేషన్ పద్ధతిని పాటించండి.
"""
    return f"""### 🛡️ Specialized Treatment & Prevention Protocol for: **{disease_label.title()}**

#### 🌿 1. Natural & Organic Remedies
- **Neem Oil Foliar Spray:** Mix 5ml pure cold-pressed neem oil + 2ml mild liquid soap per 1 liter of water. Spray thoroughly under and over leaves in early morning or late afternoon every 7-10 days.
- **Bio-fungicide / Bio-control:** Apply *Trichoderma viride* or *Bacillus subtilis* (2-3g/L) to suppress fungal spores and soil-borne inoculums.
- **Baking Soda / Potassium Bicarbonate:** Dissolve 5g sodium/potassium bicarbonate + 1L water to alter leaf surface pH and inhibit pathogen colonization.

#### 🧪 2. Recommended Chemical Pesticides & Active Ingredients
- **Contact Fungicides:** Copper Oxychloride (50% WP @ 2.5-3.0g/L) or chemical Mancozeb (75% WP @ 2g/L) to protect healthy foliage and prevent spore germination.
- **Systemic Curative Fungicides:** Azoxystrobin (23% SC @ 1ml/L) or Difenoconazole (25% EC @ 0.5-1ml/L) for established structural leaf infections.
- *Caution:* Always observe proper pre-harvest intervals (PHI) and rotate chemical groups to avoid resistance build-up.

#### 🚜 3. Cultural & Long-Term Prevention Techniques
- **Sanitation:** Immediately prune and safely burn or bury heavily infected foliage away from the crop perimeter. Do not compost infected leaves.
- **Drip Irrigation:** Avoid overhead sprinkler irrigation to keep canopy foliage dry; wet leaf duration directly drives fungal propagation.
- **Crop Rotation & Spacing:** Practice 2-to-3 season non-host crop rotation. Maintain recommended crop row spacing for optimal air circulation.
"""


def analyze_disease_with_llm(disease_label: str, target_lang: str = "English") -> str:
    """
    Constructs comprehensive treatment protocols using Google Gemini API,
    written natively in the target language.
    """
    prompt = f"""
    A plant leaf sample has been diagnosed with '{disease_label}'.
    Provide a comprehensive management strategy covering:
    1. Natural / Organic Remedies: Eco-friendly solutions, biological controls, or traditional methods.
    2. Chemical Pesticides: Precise active ingredients or specific pesticide options recommended by agricultural standards.
    3. Prevention Techniques: Long-term cultural practices to avoid recurrence.
    Keep the tone highly practical and helpful for a farmer.

    CRITICAL REQUIREMENT: You MUST write your entire response natively in {target_lang} using its native script (e.g. Devanagari for Hindi, Bengali script for Bengali, Telugu script for Telugu, etc.). Do not return in English unless {target_lang} is English.
    """

    gemini_key = _get_api_key("GEMINI_API_KEY")
    if gemini_key:
        try:
            from google import genai

            client = genai.Client(api_key=gemini_key)
            for m in ACTIVE_GEMINI_MODELS[:4]:
                try:
                    response = client.models.generate_content(model=m, contents=prompt)
                    if response and response.text:
                        return response.text
                except Exception:
                    continue
        except Exception:
            pass

    # Fallback to expert agronomic protocol
    return get_default_treatment_protocol(disease_label, target_lang=target_lang)
