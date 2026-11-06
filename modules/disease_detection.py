from markdown_it import MarkdownIt
from utils.api import analyze_disease_with_llm, identify_plant_disease_api
from utils.translator_api import translate_text

_md = MarkdownIt()


def diagnose_crop_image(image_bytes: bytes, target_lang: str = "English") -> dict:
    """
    Diagnoses crop diseases from uploaded leaf image bytes and generates
    the corresponding management protocol in the chosen language.
    """
    detected_disease = identify_plant_disease_api(image_bytes)

    # Check for API / Network Errors
    if "Error" in detected_disease or "Failed" in detected_disease:
        return {
            "status": "error",
            "message": translate_text(detected_disease, target_lang),
        }

    # Check for healthy plant
    if detected_disease == "Healthy Plant":
        return {
            "status": "healthy",
            "disease": "Healthy Plant",
            "translated_disease": translate_text("Healthy Plant", target_lang),
            "message": translate_text(
                "Analysis complete! No pathogenic elements found. The plant appears healthy.",
                target_lang,
            ),
        }

    # Pathogenic infection detected
    treatment_markdown = analyze_disease_with_llm(detected_disease, target_lang=target_lang)
    treatment_html = _md.render(treatment_markdown)

    return {
        "status": "infected",
        "disease": detected_disease,
        "translated_disease": translate_text(detected_disease, target_lang),
        "message": translate_text("Analysis complete! Pathogenic infection detected.", target_lang),
        "treatment_markdown": treatment_markdown,
        "treatment_html": treatment_html,
    }
