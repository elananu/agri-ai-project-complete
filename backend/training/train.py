"""
train.py
Trains a real YOLOv8 object-detection model on the prepared dataset.

Usage:
    python train.py --data dataset/data.yaml --epochs 60 --model yolov8n.pt

After training completes, copy the resulting best weights into the app:
    cp runs/detect/train/weights/best.pt ../models/best.pt
"""

import argparse
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to data.yaml produced by prepare_dataset.py")
    parser.add_argument("--model", default="yolov8n.pt", help="Base model to fine-tune (yolov8n/s/m.pt)")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    args = parser.parse_args()

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=15,
    )

    metrics = model.val()
    print("\nValidation metrics:", metrics.results_dict)
    print("\nTraining complete. Best weights saved under runs/detect/train*/weights/best.pt")
    print("Copy them into your app with:")
    print("  cp runs/detect/train/weights/best.pt ../models/best.pt")


if __name__ == "__main__":
    main()
