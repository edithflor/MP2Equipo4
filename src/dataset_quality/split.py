"""Genera un split reproducible del coco validado"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


def split_coco(
    coco_path: Path,
    output_dir: Path,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    seed: int = 42,
) -> None:
    """Diide imagenes coco en train-val-test conservando anotaciones asociadas"""

    if train_ratio <= 0 or val_ratio <= 0 or train_ratio + val_ratio >= 1:
        raise ValueError("Los ratios deben ser válidos y dejar espacio para test.")

    coco_data: dict[str, Any] = json.loads(coco_path.read_text(encoding="utf-8"))

    images = list(coco_data.get("images", []))
    annotations = list(coco_data.get("annotations", []))

    rng = random.Random(seed)
    rng.shuffle(images)

    total = len(images)
    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    splits = {
        "train": images[:train_end],
        "val": images[train_end:val_end],
        "test": images[val_end:],
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    for split_name, split_images in splits.items():
        image_ids = {image["id"] for image in split_images}
        split_annotations = [
            annotation
            for annotation in annotations
            if annotation.get("image_id") in image_ids
        ]

        payload = {
            key: value
            for key, value in coco_data.items()
            if key not in {"images", "annotations"}
        }
        payload["images"] = split_images
        payload["annotations"] = split_annotations

        output_path = output_dir / f"{split_name}.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Divide un COCO validado.")
    parser.add_argument("--coco", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.2)
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