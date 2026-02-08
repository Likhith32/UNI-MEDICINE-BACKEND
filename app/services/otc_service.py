# app/services/otc_service.py

import json
import os

from typing import List, Dict

_OTC_DATA = None


def _load_otc_data() -> List[Dict]:
    global _OTC_DATA
    if _OTC_DATA is not None:
        return _OTC_DATA

    base_dir = os.path.dirname(os.path.dirname(__file__))  # app/
    data_path = os.path.join(base_dir, "data", "otc_conditions.json")

    with open(data_path, "r", encoding="utf-8") as f:
        _OTC_DATA = json.load(f)

    return _OTC_DATA


def find_best_matches(symptom_text: str, top_k: int = 3) -> List[Dict]:
    """
    Very simple scorer:
    - lowercase everything
    - for each condition, count how many of its common_symptoms
      words/phrases appear in the user's text
    - return top_k with score > 0
    """
    text = (symptom_text or "").lower()
    data = _load_otc_data()

    scored = []
    for cond in data:
        score = 0
        for s in cond.get("common_symptoms", []):
            if any(word in text for word in s.lower().split()):
                score += 1

        if score > 0:
            scored.append((score, cond))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for score, c in scored[:top_k]]
