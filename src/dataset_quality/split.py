"""Genera un split reproducible del coco validado usando estratificación F5"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dataset_splitting.stratified import generate_stratified_splits


def split_coco(
    coco_path: Path,
    output_dir: Path,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> None:
    coco_data: dict[str, Any] = json.loads(coco_path.read_text(encoding="utf-8"))

    test_ratio = max(0.0, 1.0 - train_ratio - val_ratio)

    splits_ids = generate_stratified_splits(
        coco_data, train_ratio=train_ratio, val_ratio=val_ratio, test_ratio=test_ratio, seed=seed
    )

    images = list(coco_data.get("images", []))
    annotations = list(coco_data.get("annotations", []))
    img_by_id = {img["id"]: img for img in images if "id" in img}

    output_dir.mkdir(parents=True, exist_ok=True)

    for split_name, img_ids in splits_ids.items():
        split_images = [img_by_id[img_id] for img_id in img_ids if img_id in img_by_id]
        valid_ids = set(img_ids)
        split_annotations = [ann for ann in annotations if ann.get("image_id") in valid_ids]

        payload = {
            key: value for key, value in coco_data.items() if key not in {"images", "annotations"}
        }
        payload["images"] = split_images
        payload["annotations"] = split_annotations

        output_path = output_dir / f"{split_name}.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Divide un COCO validado con F5.")
    parser.add_argument("--coco", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    split_coco(
        coco_path=args.coco,
        output_dir=args.output_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
