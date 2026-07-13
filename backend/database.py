"""
database.py
Simple SQLite persistence layer for detection history and dashboard stats.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "agri_ai.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            detections_json TEXT NOT NULL,
            disease_count INTEGER DEFAULT 0,
            pest_count INTEGER DEFAULT 0,
            weed_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_detection(image_filename: str, detections: list):
    disease_count = sum(1 for d in detections if d.get("category") == "disease")
    pest_count = sum(1 for d in detections if d.get("category") == "pest")
    weed_count = sum(1 for d in detections if d.get("category") == "weed")

    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO detections
           (image_filename, detections_json, disease_count, pest_count, weed_count, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            image_filename,
            json.dumps(detections),
            disease_count,
            pest_count,
            weed_count,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    record_id = cur.lastrowid
    conn.close()
    return record_id


def get_history(limit: int = 20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM detections ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "image_filename": row["image_filename"],
            "detections": json.loads(row["detections_json"]),
            "disease_count": row["disease_count"],
            "pest_count": row["pest_count"],
            "weed_count": row["weed_count"],
            "created_at": row["created_at"],
        })
    return history


def get_stats():
    conn = get_conn()
    row = conn.execute(
        """SELECT
             COUNT(*) as total_scans,
             COALESCE(SUM(disease_count), 0) as total_diseases,
             COALESCE(SUM(pest_count), 0) as total_pests,
             COALESCE(SUM(weed_count), 0) as total_weeds
           FROM detections"""
    ).fetchone()
    conn.close()
    return {
        "total_scans": row["total_scans"],
        "total_diseases": row["total_diseases"],
        "total_pests": row["total_pests"],
        "total_weeds": row["total_weeds"],
    }
