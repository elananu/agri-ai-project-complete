"""
prepare_dataset.py
Converts the PlantDoc object-detection dataset (CSV + Pascal-VOC-style
bounding boxes) into YOLOv8 training format:

    dataset/
      images/train/*.jpg
      images/val/*.jpg
      labels/train/*.txt
      labels/val/*.txt
    data.yaml

Usage:
    1. Download the dataset:
       git clone https://github.com/pratikkayal/PlantDoc-Object-Detection-Dataset.git plantdoc_raw

    2. Run this script:
       python prepare_dataset.py --source plantdoc_raw --out dataset

    3. Train:
       python train.py --data dataset/data.yaml
"""

import argparse
import csv
import shutil
from pathlib import Path
from collections import defaultdict


def slugify(name: str) -> str:
    return (
        name.strip().lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("__", "_")
    )


def load_annotations(csv_path: Path):
    """Returns dict: filename -> list of (class_name, xmin, ymin, xmax, ymax, width, height)"""
    by_file = defaultdict(list)
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                by_file[row["filename"]].append((
                    row["class"].strip(),
                    float(row["xmin"]), float(row["ymin"]),
                    float(row["xmax"]), float(row["ymax"]),
                    float(row["width"]), float(row["height"]),
                ))
            except (KeyError, ValueError):
                continue
    return by_file


def convert_split(image_dir: Path, csv_path: Path, out_images: Path, out_labels: Path, class_to_id: dict):
    from PIL import Image

    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    annotations = load_annotations(csv_path)
    written, skipped = 0, 0

    for filename, boxes in annotations.items():
        src_img = image_dir / filename
        if not src_img.exists():
            skipped += 1
            continue

        # Some CSV rows have bad/zero width or height — fall back to the
        # image's real dimensions read directly from the file.
        real_w, real_h = None, None
        try:
            with Image.open(src_img) as im:
                real_w, real_h = im.size
        except Exception:
            skipped += 1
            continue

        shutil.copy2(src_img, out_images / filename)

        lines = []
        for class_name, xmin, ymin, xmax, ymax, iw, ih in boxes:
            if iw <= 0 or ih <= 0:
                iw, ih = real_w, real_h

            slug = slugify(class_name)
            if slug not in class_to_id:
                continue
            cls_id = class_to_id[slug]

            # clamp + normalize to YOLO format (x_center, y_center, w, h) in [0,1]
            xmin, xmax = max(0, min(xmin, xmax)), min(iw, max(xmin, xmax))
            ymin, ymax = max(0, min(ymin, ymax)), min(ih, max(ymin, ymax))
            x_c = ((xmin + xmax) / 2) / iw
            y_c = ((ymin + ymax) / 2) / ih
            bw = (xmax - xmin) / iw
            bh = (ymax - ymin) / ih
            if bw <= 0 or bh <= 0:
                continue
            lines.append(f"{cls_id} {x_c:.6f} {y_c:.6f} {bw:.6f} {bh:.6f}")

        label_path = out_labels / (Path(filename).stem + ".txt")
        label_path.write_text("\n".join(lines), encoding="utf-8")
        written += 1

    return written, skipped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to cloned PlantDoc-Object-Detection-Dataset repo")
    parser.add_argument("--out", default="dataset", help="Output dataset directory")
    args = parser.parse_args()

    source = Path(args.source)
    out = Path(args.out)

    train_csv = source / "train_labels.csv"
    test_csv = source / "test_labels.csv"
    train_dir = source / "TRAIN"
    test_dir = source / "TEST"

    # Build unified class list from both splits
    all_classes = set()
    for csv_path in (train_csv, test_csv):
        anns = load_annotations(csv_path)
        for boxes in anns.values():
            for class_name, *_ in boxes:
                all_classes.add(slugify(class_name))
    class_list = sorted(all_classes)
    class_to_id = {c: i for i, c in enumerate(class_list)}

    print(f"Found {len(class_list)} classes:")
    for c in class_list:
        print(f"  {class_to_id[c]}: {c}")

    w1, s1 = convert_split(train_dir, train_csv, out / "images" / "train", out / "labels" / "train", class_to_id)
    w2, s2 = convert_split(test_dir, test_csv, out / "images" / "val", out / "labels" / "val", class_to_id)

    print(f"\nTrain: {w1} images written, {s1} skipped (missing file)")
    print(f"Val:   {w2} images written, {s2} skipped (missing file)")

    data_yaml = out / "data.yaml"
    data_yaml.write_text(
        "path: " + str(out.resolve()) + "\n"
        "train: images/train\n"
        "val: images/val\n"
        f"nc: {len(class_list)}\n"
        "names: " + str(class_list) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {data_yaml}")
    print("Next: python train.py --data " + str(data_yaml))


if __name__ == "__main__":
    main()
