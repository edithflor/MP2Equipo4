from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dataset_quality.imbalance import analyze_class_imbalance
from dataset_quality.invalid_boxes import analyze_invalid_boxes
from dataset_quality.phash import analyze_duplicates
from dataset_quality.small_objects import analyze_small_objects
from dataset_quality.spatial_bias import analyze_spatial_bias

TAB_SPECS = (
    ("small_objects", "Objetos pequeños"),
    ("class_imbalance", "Desbalance"),
    ("duplicates", "Duplicados"),
    ("invalid_boxes", "Cajas inválidas"),
    ("spatial_bias", "Sesgo espacial"),
)


def load_coco(path: str | Path) -> dict[str, Any]:
    """Carga el COCO local que ya pasó por la ingesta; no abre servicios externos."""
    with Path(path).open(encoding="utf-8") as source:
        return json.load(source)


def _image_names(coco_data: dict[str, Any]) -> dict[Any, str]:
    return {
        image.get("id"): image.get("file_name", f"image-{image.get('id')}")
        for image in coco_data.get("images", [])
    }


def _annotation_quadrant(annotation: dict[str, Any], image: dict[str, Any]) -> str | None:
    bbox = annotation.get("bbox", [])
    width = image.get("width", 0)
    height = image.get("height", 0)
    if len(bbox) < 4 or width <= 0 or height <= 0:
        return None
    center_x = bbox[0] + bbox[2] / 2
    center_y = bbox[1] + bbox[3] / 2
    vertical = "T" if center_y < height / 2 else "B"
    horizontal = "L" if center_x < width / 2 else "R"
    return vertical + horizontal


def build_analyzer_report(
    coco_data: dict[str, Any], image_bytes: dict[str, bytes] | None = None
) -> dict[str, dict[str, Any]]:
    """Ejecuta F3-01…05 y adapta sus resultados para la UI sin inventar series."""
    names = _image_names(coco_data)
    images_by_id = {image.get("id"): image for image in coco_data.get("images", [])}

    small = analyze_small_objects(coco_data)
    small_offenders = [
        {"image_id": image_id, "file_name": names.get(image_id, "desconocida")}
        for image_id in sorted(small["offender_images"], key=str)
    ]

    imbalance = analyze_class_imbalance(coco_data)
    imbalance_offenders = [
        {"class_name": name, "image_count": imbalance["class_counts"][name]}
        for name in imbalance["classes_under_minimum"]
    ]

    duplicates = analyze_duplicates(image_bytes or {})
    duplicate_offenders = [
        {
            **pair,
            "file_name_1": names.get(pair["image1"], pair["image1"]),
            "file_name_2": names.get(pair["image2"], pair["image2"]),
        }
        for pair in duplicates["pairs"]
    ]

    invalid = analyze_invalid_boxes(coco_data)
    invalid_offenders = [
        {
            "annotation_id": annotation.get("id"),
            "image_id": annotation.get("image_id"),
            "file_name": names.get(annotation.get("image_id"), "desconocida"),
            "reasons": ", ".join(annotation["invalid_reasons"]),
        }
        for annotation in invalid["invalid_annotations"]
    ]

    spatial = analyze_spatial_bias(coco_data)
    dominant_quadrant = max(spatial["quadrant_counts"], key=spatial["quadrant_counts"].get)
    spatial_samples = []
    for annotation in coco_data.get("annotations", []):
        image_id = annotation.get("image_id")
        image = images_by_id.get(image_id)
        quadrant = _annotation_quadrant(annotation, image) if image else None
        if quadrant == dominant_quadrant:
            spatial_samples.append(
                {
                    "annotation_id": annotation.get("id"),
                    "image_id": image_id,
                    "file_name": names.get(image_id, "desconocida"),
                    "quadrant": quadrant,
                }
            )

    return {
        "small_objects": {
            "metrics": small,
            "chart": {"porcentaje": small["percentage"]},
            "offenders": small_offenders,
        },
        "class_imbalance": {
            "metrics": {"ratio": imbalance["ratio"]},
            "chart": imbalance["class_counts"],
            "offenders": imbalance_offenders,
        },
        "duplicates": {
            "metrics": {"pair_count": len(duplicates["pairs"])},
            "chart": {"pares": len(duplicates["pairs"])},
            "offenders": duplicate_offenders,
        },
        "invalid_boxes": {
            "metrics": {"invalid_count": len(invalid["invalid_annotations"])},
            "chart": {"cajas_inválidas": len(invalid["invalid_annotations"])},
            "offenders": invalid_offenders,
        },
        "spatial_bias": {
            "metrics": {
                "mean_area": spatial["mean_area"],
                "median_area": spatial["median_area"],
                "p25_area": spatial["p25_area"],
                "p75_area": spatial["p75_area"],
            },
            "chart": spatial["quadrant_counts"],
            "offenders": spatial_samples,
        },
    }
