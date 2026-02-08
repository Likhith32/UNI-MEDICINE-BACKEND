"""
AI service layer using Google Gemini (FREE TIER).

- Uses google.genai (NEW SDK)
- Safe medical assistant
- Graceful failure handling
"""

import os
import textwrap
import logging
import google.genai as genai
from google.genai import types


logger = logging.getLogger(__name__)

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEY is NOT set")

client = genai.Client(api_key=GEMINI_API_KEY)

# -------------------------------------------------
# SYSTEM PROMPT
# -------------------------------------------------

SYSTEM_PROMPT = textwrap.dedent("""
You are a SAFE AI medical assistant for university students.

IMPORTANT:
- You are NOT a doctor.
- You provide health information for awareness only.
- You must NEVER replace professional medical advice.

STRICT RULES:
- NEVER give a confirmed diagnosis.
- NEVER prescribe medicines or dosages.
- ALWAYS include a medical disclaimer.
- Encourage consulting a qualified doctor when needed.

STYLE:
- Simple language
- Bullet points
- Calm and reassuring
""").strip()

# -------------------------------------------------
# PUBLIC FUNCTIONS
# -------------------------------------------------

def chat_with_ai(user_context: dict, message: str) -> str:
    student_name = user_context.get("name", "Student")

    prompt = f"""
{SYSTEM_PROMPT}

Student name: {student_name}

Symptoms described:
\"\"\"{message}\"\"\"

Respond with:
1. Possible common causes (not a diagnosis)
2. Safe self-care tips
3. Red-flag symptoms
4. Clear disclaimer
"""

    return _call_gemini(prompt)


def get_disease_info(disease_name: str) -> dict:
    disease = disease_name.strip().title()

    prompt = f"""
{SYSTEM_PROMPT}

Explain the condition: {disease}

Include:
- Short description
- Common symptoms
- Safe self-care
- When to see a doctor
- Disclaimer
"""

    explanation = _call_gemini(prompt)

    return {
        "name": disease,
        "explanation": explanation,
        "note": "This is general information only. NOT a medical diagnosis."
    }


def explain_image_prediction(predicted_condition: str, confidence: float) -> str:
    prompt = f"""
{SYSTEM_PROMPT}

An image model predicted:
Condition: {predicted_condition}
Confidence: {confidence:.2f}

Explain carefully:
- What this MAY indicate
- Why image models can be wrong
- When to see a doctor
- Disclaimer
"""

    return _call_gemini(prompt)

# -------------------------------------------------
# INTERNAL HELPER
# -------------------------------------------------

def _call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return (
            "AI service is not configured. "
            "Please consult a doctor or campus health center."
        )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=600,
            ),
        )

        return response.text.strip()

    except Exception as e:
        logger.exception("Gemini API failure")
        return (
            "AI service is temporarily unavailable. "
            "Please try again later or consult a doctor."
        )
