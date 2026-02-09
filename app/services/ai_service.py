"""
Gemini AI Service (TEXT ONLY)

- Uses google-genai (NEW SDK)
- Safe medical assistant
- Used by chatbot + image explanation
"""

import os
import textwrap
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# ---------------- CONFIG ----------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

if not GEMINI_API_KEY:
    logger.error("❌ GEMINI_API_KEY not set")

client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------- SYSTEM PROMPT ----------------

SYSTEM_PROMPT = textwrap.dedent("""
You are a SAFE AI medical assistant for university students.

RULES:
- You are NOT a doctor
- DO NOT diagnose diseases
- DO NOT prescribe medicines
- Give only general guidance
- Always include a disclaimer
- Encourage consulting a doctor

STYLE:
- Simple language
- Bullet points
- Calm & reassuring
""").strip()

# ---------------- CHATBOT ----------------

def chat_with_ai(user_context: dict, message: str) -> str:
    student_name = user_context.get("name", "Student")

    prompt = f"""
{SYSTEM_PROMPT}

Student name: {student_name}

User message:
\"\"\"{message}\"\"\"

Respond with:
1. Possible common causes (not diagnosis)
2. Safe self-care tips
3. Red-flag symptoms
4. Clear disclaimer
"""

    return _call_gemini(prompt)

# ---------------- IMAGE EXPLANATION ----------------

def explain_image_prediction(predicted_condition: str, confidence: float) -> str:
    prompt = f"""
{SYSTEM_PROMPT}

An image model predicted:
Condition: {predicted_condition}
Confidence: {confidence:.2f}

Explain:
- What this MAY indicate
- Why image models can be wrong
- When to see a doctor
- Disclaimer
"""
    return _call_gemini(prompt)

# ---------------- INTERNAL ----------------

def _call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "AI service not configured. Please consult a doctor."

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

    except Exception:
        logger.exception("Gemini API failed")
        return "AI service temporarily unavailable."
