"""
test_main.py
Integration tests for the FastAPI endpoints in main.py, using FastAPI's
TestClient. Detection and database calls are mocked so tests run fast
and don't require a real trained model, uploaded images, or a live DB.
"""
import io
import main
from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_health_endpoint_returns_ok(monkeypatch):
    monkeypatch.setattr(main.detection, "get_mode", lambda: "cv_heuristic")
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_mode"] == "cv_heuristic"


def test_weather_endpoint_returns_expected_fields():
    response = client.get("/api/weather?location=TestField")
    assert response.status_code == 200
    body = response.json()
    assert body["location"] == "TestField"
    assert "temperature_c" in body
    assert "humidity_pct" in body
    assert "condition" in body


def test_detect_rejects_unsupported_file_type():
    fake_file = io.BytesIO(b"not a real image")
    response = client.post(
        "/api/detect",
        files={"file": ("test.txt", fake_file, "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_detect_returns_enriched_detection_for_known_label(monkeypatch, tmp_path):
    monkeypatch.setattr(
        main.detection, "run_detection",
        lambda path, conf_threshold=0.35: [
            {"label": "corn_gray_leaf_spot", "confidence": 90.4, "box": [0, 0, 100, 100]}
        ],
    )
    monkeypatch.setattr(main.detection, "get_mode", lambda: "yolo")
    monkeypatch.setattr(main.database, "save_detection", lambda filename, detections: 1)

    fake_image = io.BytesIO(b"fake image bytes")
    response = client.post(
        "/api/detect",
        files={"file": ("leaf.jpg", fake_image, "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["model_mode"] == "yolo"
    assert len(body["detections"]) == 1

    det = body["detections"][0]
    assert det["label"] == "corn_gray_leaf_spot"
    assert det["category"] == "disease"
    assert det["disease_type"] == "Fungal disease"
    assert det["cause"] is not None
    assert "advice" in det


def test_detect_falls_back_to_ai_explain_when_recommendation_incomplete(monkeypatch):
    monkeypatch.setattr(
        main.detection, "run_detection",
        lambda path, conf_threshold=0.35: [
            {"label": "totally_unmapped_label", "confidence": 77.0, "box": [0, 0, 50, 50]}
        ],
    )
    monkeypatch.setattr(main.detection, "get_mode", lambda: "yolo")
    monkeypatch.setattr(main.database, "save_detection", lambda filename, detections: 2)
    monkeypatch.setattr(
        main, "generate_explanation",
        lambda label, confidence: {
            "disease_type": "Unknown (AI-generated)",
            "cause": "AI-generated cause text.",
            "advice": "AI-generated advice text.",
        },
    )

    fake_image = io.BytesIO(b"fake image bytes")
    response = client.post(
        "/api/detect",
        files={"file": ("leaf.jpg", fake_image, "image/jpeg")},
    )

    assert response.status_code == 200
    det = response.json()["detections"][0]
    assert det["disease_type"] == "Unknown (AI-generated)"
    assert det["cause"] == "AI-generated cause text."


def test_history_endpoint(monkeypatch):
    monkeypatch.setattr(
        main.database, "get_history",
        lambda limit=20: [{"id": 1, "image_filename": "test.jpg", "detections": []}],
    )
    response = client.get("/api/history?limit=5")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_stats_endpoint(monkeypatch):
    monkeypatch.setattr(
        main.database, "get_stats",
        lambda: {"total_scans": 10, "total_diseases": 5, "total_pests": 2, "total_weeds": 0},
    )
    response = client.get("/api/stats")
    assert response.status_code == 200
    body = response.json()
    assert body["total_scans"] == 10