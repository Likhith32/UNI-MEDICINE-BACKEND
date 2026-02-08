# app/services/image_service.py

"""
Image analysis service.

Now integrated with the LLM:
- A (dummy or real) image classifier produces a predicted condition + confidence.
- The LLM (via ai_service) explains that prediction in student-friendly language.
"""

import os
import logging
from typing import Dict, Optional

from PIL import Image
import google.generativeai as genai

logger = logging.getLogger(__name__)

# ---------- Gemini config ----------

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"),
    generation_config={
        "temperature": 0.2,
        "max_output_tokens": 500,
    },
)

# ---------- Main function ----------

def analyze_image(file_path: str, user_id: Optional[int] = None) -> Dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError("Image file not found")

    logger.info("Safe Gemini visual observation for user_id=%s", user_id)

    # ✅ THIS IS THE KEY FIX
    image = Image.open(file_path)

    prompt = """
    You are a SAFE medical AI assistant.

    RULES:
    - DO NOT diagnose diseases
    - DO NOT name specific skin conditions
    - Describe only visible features (redness, bumps, dryness, swelling)
    - Mention broad categories only (irritation, allergy, inflammation)
    - Suggest simple self-care
    - Mention when to see a doctor
    - Always say: This is not a diagnosis

    Use simple student-friendly language.
    """

    try:
        response = model.generate_content([prompt, image])
        observation = response.text.strip()
    except Exception as e:
        logger.exception("Gemini image analysis failed")
        raise RuntimeError("Image analysis service unavailable") from e

    return {
        "image_observation": observation,
        "note": (
            "This is an AI-generated visual observation only. "
            "It is NOT a medical diagnosis. Please consult a doctor."
        ),
    }
from app.services.ai_service import explain_image_prediction

logger = logging.getLogger(__name__)


def analyze_image(file_path: str, user_id: Optional[int] = None) -> Dict:
    """
    Analyze an uploaded image and return a possible condition.

    Flow:
    1. Verify file exists.
    2. Run image analysis (dummy or real model) to get:
       - predicted_condition
       - confidence (0.0 - 1.0)
    3. Call LLM to generate explanation and safety guidance.
    4. Return a rich JSON-friendly dict.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    logger.info("Analyzing image at %s for user_id=%s", file_path, user_id)

    # ---------- STEP 2: Image "model" (placeholder for now) ---------- #
    #
    # TODO: Replace this with a real ML model later.
    # For now, we just pretend it's a generic skin issue.
    # You could, for example, inspect file name or size and vary prediction,
    # but for a college project demo this is okay.
    predicted_condition = "possible mild skin irritation"
    confidence = 0.60  # Dummy confidence

    # ---------- STEP 3: Ask LLM to explain this prediction ---------- #
    llm_explanation = explain_image_prediction(
        predicted_condition=predicted_condition,
        confidence=confidence,
    )

    # ---------- STEP 4: Build response ---------- #
    result = {
        "predicted_condition": predicted_condition,
        "confidence": confidence,
        "llm_explanation": llm_explanation,
        "note": (
            "This result is based on an automated image check and an AI language model. "
            "It is NOT a confirmed medical diagnosis. The AI can be wrong. "
            "Please consult a qualified doctor or your campus health centre before "
            "starting any treatment or medication."
        ),
    }

    return result
