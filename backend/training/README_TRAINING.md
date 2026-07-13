# Training a Real Multi-Crop Detection Model

This gives Agri-AI **species-level** detection (real diseases/pests per
crop) instead of the generic CV-heuristic fallback. It uses the
**PlantDoc** dataset — 2,569 real field images, 29 classes, across
**13 crop species** (apple, corn, tomato, potato, grape, cherry, peach,
bell pepper, blueberry, raspberry, soyabean, squash, strawberry) — with
genuine bounding-box annotations (not a classification-only dataset).

> This exact pipeline (download → convert → train) was tested end-to-end
> while building this project: 2,342 train / 236 val images converted
> successfully with 0 malformed labels.

## 1. Install training dependencies

```bash
cd agri-ai/backend
pip install -r requirements.txt
```

(`ultralytics` and `Pillow`, needed for training, are already in
`requirements.txt`.)

## 2. Dataset — already prepared ✅

The `dataset/` folder in this training directory is already filled in
for you (2,342 train / 236 val images, YOLO-format labels, `data.yaml`
with all 29 classes). You can skip straight to step 4 (Train).

If you ever need to regenerate it from the raw PlantDoc CSVs instead:

```bash
cd agri-ai/backend/training
git clone https://github.com/pratikkayal/PlantDoc-Object-Detection-Dataset.git plantdoc_raw
python prepare_dataset.py --source plantdoc_raw --out dataset
```

## 4. Train

```bash
python train.py --data dataset/data.yaml --epochs 60 --model yolov8n.pt
```

- `yolov8n.pt` (nano) trains fastest and is fine for a first pass /
  CPU-only machines. Use `yolov8s.pt` or `yolov8m.pt` for higher accuracy
  if you have a GPU.
- Training 60 epochs on ~2,300 images takes roughly 20–40 minutes on a
  modern GPU, or several hours on CPU only. Lower `--epochs` for a
  quicker first test run.

## 5. Deploy the trained model into the app

```bash
cp runs/detect/train/weights/best.pt ../models/best.pt
```

Restart the backend (`uvicorn main:app --reload --port 8000`). It will
automatically detect `backend/models/best.pt`, load it, and the
dashboard badge switches from **"🔬 Real-Time CV Analysis"** to
**"🎯 Custom YOLOv8 Model"** — now giving real species-level results
(e.g. "Corn Gray Leaf Spot 91%" instead of generic "dark spot").

## Notes

- `recommendations.py` is already pre-filled with treatment advice for
  all 29 PlantDoc classes across every included crop.
- Want a single-crop model instead (e.g. corn only)? Filter
  `train_labels.csv`/`test_labels.csv` to rows where `class` starts with
  `Corn` before running `prepare_dataset.py`, or edit the script to
  filter by class prefix.
- Want higher accuracy on your specific fields? Add your own labeled
  images (using a tool like [LabelImg](https://github.com/heartexlabs/labelImg)
  or [Roboflow](https://roboflow.com)) into the `dataset/images` and
  `dataset/labels` folders in the same YOLO format before training —
  more real, local examples will outperform PlantDoc alone.
