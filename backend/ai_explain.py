"""
ai_explain.py
Uses the Anthropic API to generate a live explanation (disease type, cause,
and prevention advice) for any detected class label — including ones not
covered in the static RECOMMENDATIONS dictionary in recommendations.py.

Falls back gracefully (returns None) if no API key is set or the call
fails, so the app keeps working offline using the static recommendations.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("ANTHROPIC_API_KEY")

_client = None


def _get_client():
    global _client
    if _client is None and API_KEY:
        import anthropic
        _client = anthropic.Anthropic(api_key=API_KEY)
    return _client


def generate_explanation(label: str, confidence: float) -> dict | None:
    """
    Calls Claude to generate a live cause + prevention explanation for the
    given detected class label. Returns a dict with disease_type, cause,
    and advice, or None if unavailable (missing key, API error, etc.)
    """
    client = _get_client()
    if client is None:
        return None

    readable_label = label.replace("_", " ")

    prompt = f"""You are an agricultural plant pathology expert. A crop
detection AI model identified this class in an uploaded leaf image:
"{readable_label}" (confidence: {confidence}%).

Respond ONLY with a JSON object (no markdown, no extra text) in this
exact format:
{{
  "disease_type": "short type e.g. 'Fungal (Early Blight)' or 'Healthy' if no disease",
  "cause": "1-2 sentences on what causes this, or null if healthy",
  "advice": "1-2 sentences of practical prevention/treatment advice, or a short healthy-care tip if healthy"
}}

Be concise, factual, and practical for a farmer to understand."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Strip accidental markdown fences if present
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        import json
        data = json.loads(text)
        return {
            "disease_type": data.get("disease_type"),
            "cause": data.get("cause"),
            "advice": data.get("advice"),
        }
    except Exception as e:
        print(f"[ai_explain] Failed to generate AI explanation: {e}")
        return None