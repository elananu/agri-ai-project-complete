# 🌾 Agri-AI: Smart Crop & Pest Detection System

AI-powered farming assistant that detects crop diseases, pests, and weeds
from an uploaded image using **YOLOv8**, then provides smart treatment
recommendations through a real-time dashboard.

Stack: **FastAPI** (Python backend) + **React / Vite** (frontend) +
**Ultralytics YOLOv8** (computer vision) + **SQLite** (history/stats).

---

## 📁 Project Structure

```
agri-ai/
├── backend/
│   ├── main.py            # FastAPI app & API routes
│   ├── detection.py        # YOLOv8 inference wrapper (+ demo mock mode)
│   ├── recommendations.py  # class -> treatment advice mapping
│   ├── database.py         # SQLite history/stats
│   ├── requirements.txt
│   ├── models/             # put your trained best.pt here
│   └── uploads/             # uploaded images are stored here
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── api.js
    │   └── components/
    │       ├── UploadPanel.jsx
    │       ├── ResultsPanel.jsx
    │       ├── StatsPanel.jsx
    │       └── HistoryPanel.jsx
    ├── package.json
    └── vite.config.js
```

---

## ⚙️ Setup & Run in VS Code

### 1. Backend (FastAPI + YOLOv8)

```bash
cd agri-ai/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend runs at **http://localhost:8000**
API docs available at **http://localhost:8000/docs**

> **No trained model yet?** The backend automatically runs in
> **real-time CV analysis mode** — it uses OpenCV to genuinely inspect
> each uploaded image's actual pixels (color + texture thresholding) to
> locate dark lesion spots (possible blight/rust/bacterial disease) and
> yellow/chlorotic patches (possible pest damage or nutrient stress), then
> draws real bounding boxes around what it finds. This is **not random** —
> the same photo always produces the same result, and clean healthy leaves
> correctly come back as "healthy". It cannot identify exact pest/disease
> *species* (e.g. aphid vs. whitefly) with certainty — only a model
> trained on labeled examples can do that reliably.
>
> To get **species-level** detection: fine-tune YOLOv8 on a crop
> disease/pest/weed dataset (e.g. PlantVillage, or your own labeled
> images) with class names matching `recommendations.py` (aphid,
> whitefly, leaf_blight, powdery_mildew, weed, healthy, etc.), export the
> weights, and place the file at `backend/models/best.pt`. Restart the
> server — it will detect and load your real trained model automatically,
> switching the dashboard badge from "🔬 Real-Time CV Analysis" to
> "🎯 Custom YOLOv8 Model".

### 2. Frontend (React + Vite)

Open a **second terminal**:

```bash
cd agri-ai/frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173** and proxies API calls to the
backend automatically (see `vite.config.js`).

### 3. Open the app

Visit **http://localhost:5173** in your browser, upload a crop image, and
watch the AI detect diseases/pests/weeds with bounding boxes, confidence
scores, and treatment recommendations.

---

## 🔌 API Reference

| Method | Endpoint          | Description                                  |
|--------|-------------------|-----------------------------------------------|
| POST   | `/api/detect`     | Upload an image, run detection, get results   |
| GET    | `/api/history`    | List recent detection scans                    |
| GET    | `/api/stats`      | Aggregate dashboard stats                       |
| GET    | `/api/weather`    | Mock field weather conditions                   |
| GET    | `/api/health`     | Health check + current model mode               |

---

## 🧠 Training Your Own YOLOv8 Model (multi-crop, real dataset)

A tested, ready-to-run pipeline is included in `backend/training/` using
the **PlantDoc** dataset (29 real disease/pest/healthy classes across 13
crop species — apple, corn, tomato, potato, grape, and more), with a
CSV→YOLO converter that was verified against the actual dataset.

**See [`backend/training/README_TRAINING.md`](backend/training/README_TRAINING.md)
for the full step-by-step guide.** Quick version:

```bash
cd agri-ai/backend/training
git clone https://github.com/pratikkayal/PlantDoc-Object-Detection-Dataset.git plantdoc_raw
python prepare_dataset.py --source plantdoc_raw --out dataset
python train.py --data dataset/data.yaml --epochs 60
cp runs/detect/train/weights/best.pt ../models/best.pt
```

Restart the backend — it auto-loads your trained model and the dashboard
badge switches to "🎯 Custom YOLOv8 Model" with real species-level results.

---

## ✅ Features

- 📤 Drag-and-drop image upload
- 🤖 YOLOv8 object detection (diseases, pests, weeds)
- 💡 Automatic treatment recommendations per detected class
- 📊 Live dashboard stats (scans, diseases, pests, weeds)
- 🌦️ Field weather widget
- 🕓 Detection history with thumbnails
- 🎨 Clean dark-themed dashboard UI

---

## 📝 License

Free to use and modify for personal, academic, or commercial projects.
