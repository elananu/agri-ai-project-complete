"""
detection.py
Two detection engines:

1. "yolo"  — a real trained YOLOv8 model (backend/models/best.pt), used
   automatically if present. This gives true species-level classification
   (aphid vs whitefly vs specific disease, etc).

2. "cv_heuristic" — a REAL (non-random) computer-vision analyzer used as
   the default when no trained weights exist. It actually inspects the
   uploaded image's pixels with OpenCV: color/texture thresholding finds
   dark lesion spots (possible blight/fungal/bacterial disease) and
   yellow/chlorotic patches (possible pest damage or nutrient stress),
   draws real bounding boxes around what it finds, and reports "healthy"
   when no significant anomaly is present. Results are 100% derived from
   the actual image content — the same photo always gives the same
   result, and different photos give different results.

   NOTE: This heuristic mode cannot identify exact pest/disease *species*
   (e.g. it can't visually tell an aphid from a whitefly with certainty)
   — that requires a model trained on labeled examples. It correctly
   flags *where* and *what kind* of visual anomaly (dark spot vs.
   yellowing) exists, which is genuinely useful, but for confident
   species-level ID, train and drop in a real YOLOv8 model (see README).

To go fully "real" with species-level detection:
1. Train / fine-tune a YOLOv8 model on a crop disease/pest/weed dataset
   (e.g. PlantVillage, or your own labeled data) with classes matching
   recommendations.py (aphid, whitefly, leaf_blight, weed, etc).
2. Export the weights as best.pt and place them at backend/models/best.pt
3. Restart the backend — it will automatically load your real model.
"""

from pathlib import Path

import cv2
import numpy as np
import torch

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best.pt"

_model = None
_model_mode = "cv_heuristic"  # "yolo" once real trained weights are loaded

# Minimum anomaly area as a fraction of total image area to count as a
# detection (filters out tiny noise/specks).
MIN_AREA_FRACTION = 0.0015
# Below this total anomaly fraction, the leaf is considered healthy.
HEALTHY_THRESHOLD_FRACTION = 0.01


def load_model():
    """Lazily load a custom YOLOv8 model if trained weights exist."""
    global _model, _model_mode

    if _model is not None:
        return _model

    if MODEL_PATH.exists():
        try:
            from ultralytics import YOLO

            # Our own trained checkpoint — safe to fully trust.
            # Newer PyTorch defaults torch.load to weights_only=True,
            # which blocks loading full model objects like this one.
            _original_torch_load = torch.load

            def _patched_torch_load(*args, **kwargs):
                kwargs["weights_only"] = False
                return _original_torch_load(*args, **kwargs)

            torch.load = _patched_torch_load
            try:
                _model = YOLO(str(MODEL_PATH))
            finally:
                torch.load = _original_torch_load

            _model_mode = "yolo"
            print(f"[detection] Loaded custom trained YOLOv8 model from {MODEL_PATH}")
        except Exception as e:
            print(f"[detection] Failed to load custom model, falling back to CV heuristic mode: {e}")
            _model = None
            _model_mode = "cv_heuristic"
    else:
        print("[detection] No trained weights found at backend/models/best.pt")
        print("[detection] Running REAL computer-vision heuristic analysis (not random mock).")
        _model_mode = "cv_heuristic"

    return _model


def get_mode() -> str:
    load_model()
    return _model_mode


def run_detection(image_path: str, conf_threshold: float = 0.35):
    """
    Runs detection on the given image path.
    Returns a list of dicts: [{label, confidence, box: [x1,y1,x2,y2]}, ...]
    """
    model = load_model()

    if _model_mode == "yolo" and model is not None:
        return _run_yolo(model, image_path, conf_threshold)

    return _run_cv_heuristic(image_path)


def _run_yolo(model, image_path, conf_threshold):
    results = model.predict(source=image_path, conf=conf_threshold, verbose=False)
    detections = []
    for r in results:
        names = r.names
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = names.get(cls_id, str(cls_id))
            confidence = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            detections.append({
                "label": label,
                "confidence": round(confidence * 100, 1),
                "box": [round(v, 1) for v in xyxy],
            })
    return detections


def _merge_boxes(boxes, iou_thresh=0.2):
    """Simple greedy merge of overlapping boxes (same label group)."""
    if not boxes:
        return []
    boxes = sorted(boxes, key=lambda b: -b["area"])
    kept = []
    for b in boxes:
        merged = False
        for k in kept:
            if _iou(b["box"], k["box"]) > iou_thresh:
                merged = True
                break
        if not merged:
            kept.append(b)
    return kept


def _iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0


def _find_regions(mask, image_area, min_area_fraction=MIN_AREA_FRACTION):
    """Find bounding boxes of significant blobs in a binary mask."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = image_area * min_area_fraction

    regions = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(c)
        regions.append({
            "box": [float(x), float(y), float(x + w), float(y + h)],
            "area": float(area),
        })
    return regions


def _run_cv_heuristic(image_path: str):
    img = cv2.imread(image_path)
    if img is None:
        return []

    h, w = img.shape[:2]
    image_area = float(w * h)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # --- Dark / brown lesion spots (fungal blight, bacterial spot, rust) ---
    dark_mask_1 = cv2.inRange(hsv, (0, 30, 0), (25, 255, 110))     # brown/rust tones
    dark_mask_2 = cv2.inRange(hsv, (0, 0, 0), (180, 255, 55))       # near-black spots
    dark_mask = cv2.bitwise_or(dark_mask_1, dark_mask_2)
    dark_regions = _find_regions(dark_mask, image_area)

    # --- Yellow / chlorotic patches (nutrient stress, pest feeding damage,
    #     early powdery mildew, whitefly honeydew sooty patches) ---
    yellow_mask = cv2.inRange(hsv, (18, 60, 120), (35, 255, 255))
    yellow_regions = _find_regions(yellow_mask, image_area)

    # --- Healthy green leaf coverage, for context / confidence baseline ---
    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    green_ratio = float(np.count_nonzero(green_mask)) / image_area

    dark_regions = _merge_boxes(dark_regions)
    yellow_regions = _merge_boxes(yellow_regions)

    total_anomaly_fraction = (
        sum(r["area"] for r in dark_regions) + sum(r["area"] for r in yellow_regions)
    ) / image_area

    detections = []

    for r in dark_regions:
        x1, y1, x2, y2 = r["box"]
        aspect = (x2 - x1) / max(1.0, (y2 - y1))
        area_frac = r["area"] / image_area
        # Roughly round + small -> rust-like; larger/irregular -> blight-like
        label = "rust" if (0.6 < aspect < 1.6 and area_frac < 0.01) else "leaf_blight"
        confidence = min(96.0, 55 + area_frac * 3500)
        detections.append({
            "label": label,
            "confidence": round(confidence, 1),
            "box": [round(v, 1) for v in r["box"]],
        })

    for r in yellow_regions:
        area_frac = r["area"] / image_area
        label = "powdery_mildew" if area_frac > 0.03 else "pest_damage_yellowing"
        confidence = min(94.0, 50 + area_frac * 3000)
        detections.append({
            "label": label,
            "confidence": round(confidence, 1),
            "box": [round(v, 1) for v in r["box"]],
        })

    if total_anomaly_fraction < HEALTHY_THRESHOLD_FRACTION and green_ratio > 0.15:
        confidence = min(97.0, 75 + green_ratio * 25)
        detections = [{
            "label": "healthy",
            "confidence": round(confidence, 1),
            "box": [round(w * 0.05, 1), round(h * 0.05, 1), round(w * 0.95, 1), round(h * 0.95, 1)],
        }]

    return detections