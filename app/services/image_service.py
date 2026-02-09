"""
Image Analysis Service

- Handles uploaded images
- Calls LLM for explanation
- NO Gemini SDK here
"""

import os
import logging
from typing import Dict, Optional
from PIL import Image
from app.services.ai_service import explain_image_prediction

logger = logging.getLogger(__name__)

def analyze_image(file_path: str, user_id: Optional[int] = None) -> Dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError("Image file not found")

    logger.info("Analyzing image for user_id=%s", user_id)

    # Open image safely
    Image.open(file_path).verify()

    # ---- DUMMY IMAGE MODEL (replace later) ----
    predicted_condition = "possible mild skin irritation"
    confidence = 0.60

    llm_explanation = explain_image_prediction(
        predicted_condition=predicted_condition,
        confidence=confidence,
    )

    return {
        "predicted_condition": predicted_condition,
        "confidence": confidence,
        "llm_explanation": llm_explanation,
        "note": (
            "This is an AI-generated observation only. "
            "It is NOT a medical diagnosis."
        ),
    }
