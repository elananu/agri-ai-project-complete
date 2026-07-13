"""
main.py — Agri-AI backend
FastAPI service that powers the Smart Crop & Pest Detection System dashboard.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import random
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import database
import detection
from recommendations import get_recommendation
from ai_explain import generate_explanation

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

app = FastAPI(title="Agri-AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

database.init_db()


@app.on_event("startup")
def startup_event():
    detection.load_model()


@app.get("/api/health")
def health():
    return {"status": "ok", "model_mode": detection.get_mode()}


@app.post("/api/detect")
async def detect_image(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = UPLOAD_DIR / filename
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    raw_detections = detection.run_detection(str(dest_path))

    enriched = []
    for det in raw_detections:
        rec = get_recommendation(det["label"])

        disease_type = rec.get("disease_type")
        cause = rec.get("cause")
        advice = rec["advice"]

        # If we don't have a static cause/disease_type for this label
        # (e.g. an unmapped class, or the generic "unknown" fallback),
        # ask Claude to generate a live explanation instead.
        if rec["category"] not in ("healthy",) and (not disease_type or not cause):
            ai_result = generate_explanation(det["label"], det["confidence"])
            if ai_result:
                disease_type = ai_result.get("disease_type") or disease_type
                cause = ai_result.get("cause") or cause
                advice = ai_result.get("advice") or advice

        enriched.append({
            **det,
            "category": rec["category"],
            "risk": rec["risk"],
            "disease_type": disease_type,
            "cause": cause,
            "advice": advice,
        })

    record_id = database.save_detection(filename, enriched)

    return {
        "id": record_id,
        "image_url": f"/uploads/{filename}",
        "model_mode": detection.get_mode(),
        "detections": enriched,
    }


@app.get("/api/history")
def history(limit: int = 20):
    return database.get_history(limit=limit)


@app.get("/api/stats")
def stats():
    return database.get_stats()


@app.get("/api/weather")
def weather(location: str = "Field Site"):
    """
    Placeholder weather endpoint so the dashboard's weather widget has
    data to display without requiring a third-party API key. Swap this
    out for a real weather API (e.g. OpenWeatherMap) if desired.
    """
    return {
        "location": location,
        "temperature_c": round(random.uniform(22, 34), 1),
        "humidity_pct": random.randint(45, 85),
        "wind_kmh": round(random.uniform(4, 18), 1),
        "rainfall_mm": round(random.uniform(0, 5), 1),
        "condition": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"]),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)