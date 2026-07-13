"""
test_ai_explain.py
Tests that ai_explain.py handles missing API keys and API failures
gracefully (returns None instead of crashing), and correctly parses a
successful response.
"""
import json
from types import SimpleNamespace

import ai_explain


def test_returns_none_when_no_api_key(monkeypatch):
    monkeypatch.setattr(ai_explain, "API_KEY", None)
    monkeypatch.setattr(ai_explain, "_client", None)
    result = ai_explain.generate_explanation("corn_gray_leaf_spot", 90.4)
    assert result is None


def test_returns_none_on_api_error(monkeypatch):
    """Simulates the exact failure we hit in production: a billing/API error."""
    monkeypatch.setattr(ai_explain, "API_KEY", "fake-key-for-test")

    class FakeClientThatFails:
        class messages:
            @staticmethod
            def create(**kwargs):
                raise Exception(
                    "Error code: 400 - invalid_request_error: "
                    "Your credit balance is too low to access the Anthropic API."
                )

    monkeypatch.setattr(ai_explain, "_client", FakeClientThatFails())
    result = ai_explain.generate_explanation("tomato_leaf_bacterial_spot", 43.1)
    assert result is None


def test_returns_parsed_dict_on_success(monkeypatch):
    monkeypatch.setattr(ai_explain, "API_KEY", "fake-key-for-test")

    fake_json_response = json.dumps({
        "disease_type": "Fungal (Early Blight)",
        "cause": "Caused by Alternaria solani.",
        "advice": "Apply a copper-based fungicide.",
    })

    class FakeClientThatSucceeds:
        class messages:
            @staticmethod
            def create(**kwargs):
                fake_content_block = SimpleNamespace(text=fake_json_response)
                return SimpleNamespace(content=[fake_content_block])

    monkeypatch.setattr(ai_explain, "_client", FakeClientThatSucceeds())
    result = ai_explain.generate_explanation("tomato_early_blight_leaf", 88.0)

    assert result is not None
    assert result["disease_type"] == "Fungal (Early Blight)"
    assert result["cause"] == "Caused by Alternaria solani."
    assert result["advice"] == "Apply a copper-based fungicide."


def test_strips_markdown_fences_from_response(monkeypatch):
    monkeypatch.setattr(ai_explain, "API_KEY", "fake-key-for-test")

    fenced_response = "```json\n" + json.dumps({
        "disease_type": "Healthy",
        "cause": None,
        "advice": "Continue normal care.",
    }) + "\n```"

    class FakeClientWithFences:
        class messages:
            @staticmethod
            def create(**kwargs):
                fake_content_block = SimpleNamespace(text=fenced_response)
                return SimpleNamespace(content=[fake_content_block])

    monkeypatch.setattr(ai_explain, "_client", FakeClientWithFences())
    result = ai_explain.generate_explanation("apple_leaf", 99.0)

    assert result is not None
    assert result["disease_type"] == "Healthy"