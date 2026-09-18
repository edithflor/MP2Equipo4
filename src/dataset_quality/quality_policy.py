"""Carga y evaluación pura de la política versionada ``quality.yaml``."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field

from dataset_quality.config import QualityPolicyConfig, RuleConfig
from dataset_quality.imbalance import analyze_class_imbalance
from dataset_quality.invalid_boxes import analyze_invalid_boxes
from dataset_quality.phash import analyze_duplicates
from dataset_quality.small_objects import analyze_small_objects
from dataset_quality.spatial_bias import analyze_spatial_bias

CheckDirection = Literal["minimum", "maximum"]

CHECK_DIRECTIONS: dict[str, CheckDirection] = {
    "min_images_per_class": "minimum",
    "small_objects_percentage": "maximum",
    "class_imbalance_ratio": "maximum",
    "duplicate_pairs": "maximum",
    "invalid_boxes": "maximum",
    "spatial_bias_percentage": "maximum",
}


class CheckResult(BaseModel):
    status: Literal["pass", "warn", "fail"]
    observed: float
    threshold: float
    severity: Literal["warn", "fail"]
    offending_samples: list[Any] = Field(default_factory=list)


class QualityGateReport(BaseModel):
    checks: dict[str, CheckResult]
    volume: dict[str, Any] = Field(default_factory=dict)
    verified: bool = True


def load_quality_policy(path: str | Path = "quality.yaml") -> QualityPolicyConfig:
    """Carga YAML y lo convierte de inmediato a un modelo Pydantic validado."""
    with Path(path).open(encoding="utf-8") as source:
        raw_policy = yaml.safe_load(source)
    return QualityPolicyConfig.model_validate(raw_policy)


def save_quality_policy(policy: QualityPolicyConfig, path: str | Path = "quality.yaml") -> Path:
    """Persiste únicamente una política ya validada por Pydantic."""
    destination = Path(path)
    destination.write_text(
        yaml.safe_dump(policy.model_dump(mode="json"), sort_keys=False), encoding="utf-8"
    )
    return destination


def analyze_quality_inputs(
    coco_data: dict[str, Any], image_bytes: dict[str, bytes] | None = None
) -> dict[str, float]:
    """Reduce las salidas de F2/F3 a los valores que evalúa la política."""
    imbalance = analyze_class_imbalance(coco_data, min_images=0)
    small_objects = analyze_small_objects(coco_data)
    duplicates = analyze_duplicates(image_bytes or {})
    invalid_boxes = analyze_invalid_boxes(coco_data)
    spatial_bias = analyze_spatial_bias(coco_data)

    counts = imbalance["class_counts"].values()
    minimum_images = min(counts, default=0)
    quadrant_counts = spatial_bias["quadrant_counts"].values()
    total_quadrants = sum(quadrant_counts)
    dominant_quadrant_percentage = (
        max(quadrant_counts, default=0) / total_quadrants * 100 if total_quadrants else 0.0
    )

    return {
        "min_images_per_class": float(minimum_images),
        "small_objects_percentage": float(small_objects["percentage"]),
        "class_imbalance_ratio": float(imbalance["ratio"]),
        "duplicate_pairs": float(len(duplicates["pairs"])),
        "invalid_boxes": float(len(invalid_boxes["invalid_annotations"])),
        "spatial_bias_percentage": dominant_quadrant_percentage,
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


def collect_offending_samples(
    coco_data: dict[str, Any],
    policy: QualityPolicyConfig,
    observations: dict[str, float],
    image_bytes: dict[str, bytes] | None = None,
) -> dict[str, list[Any]]:
    """Obtiene evidencia navegable usando las mismas funciones de F3."""
    categories = {category["id"]: category["name"] for category in coco_data.get("categories", [])}
    imbalance = analyze_class_imbalance(
        coco_data, min_images=int(policy.min_images_per_class.threshold)
    )
    small_objects = analyze_small_objects(coco_data)
    duplicates = analyze_duplicates(image_bytes or {})
    invalid_boxes = analyze_invalid_boxes(coco_data)
    spatial_bias = analyze_spatial_bias(coco_data)

    under_minimum = set(imbalance["classes_under_minimum"])
    minimum_samples = [
        {"category_id": category_id, "category": name}
        for category_id, name in categories.items()
        if name in under_minimum
    ]

    lowest_count = min(imbalance["class_counts"].values(), default=0)
    imbalance_samples = [
        {"category_id": category_id, "category": name, "observed": count}
        for category_id, name in categories.items()
        for count in [imbalance["class_counts"].get(name, 0)]
        if count == lowest_count
    ]

    quadrant_counts = spatial_bias["quadrant_counts"]
    dominant_quadrant = max(quadrant_counts, key=quadrant_counts.get)
    images = {image["id"]: image for image in coco_data.get("images", [])}
    spatial_image_ids = sorted(
        {
            annotation.get("image_id")
            for annotation in coco_data.get("annotations", [])
            if annotation.get("image_id") in images
            and _annotation_quadrant(annotation, images[annotation["image_id"]])
            == dominant_quadrant
        },
        key=str,
    )

    candidates: dict[str, list[Any]] = {
        "min_images_per_class": minimum_samples,
        "small_objects_percentage": sorted(small_objects["offender_images"], key=str),
        "class_imbalance_ratio": imbalance_samples,
        "duplicate_pairs": duplicates["pairs"],
        "invalid_boxes": [
            {
                "annotation_id": annotation.get("id"),
                "image_id": annotation.get("image_id"),
                "reasons": annotation["invalid_reasons"],
            }
            for annotation in invalid_boxes["invalid_annotations"]
        ],
        "spatial_bias_percentage": spatial_image_ids,
    }

    return {
        name: samples
        if (
            observations[name] < getattr(policy, name).threshold
            if CHECK_DIRECTIONS[name] == "minimum"
            else observations[name] > getattr(policy, name).threshold
        )
        else []
        for name, samples in candidates.items()
    }


def evaluate_quality_policy(
    policy: QualityPolicyConfig,
    observations: dict[str, float],
    offending_samples: dict[str, list[Any]] | None = None,
) -> QualityGateReport:
    """Evalúa observaciones contra YAML; no decide códigos de salida (F4-02)."""
    checks: dict[str, CheckResult] = {}
    for name, direction in CHECK_DIRECTIONS.items():
        rule: RuleConfig = getattr(policy, name)
        observed = observations[name]
        passes = (
            observed >= rule.threshold if direction == "minimum" else observed <= rule.threshold
        )
        checks[name] = CheckResult(
            status="pass" if passes else rule.severity,
            observed=observed,
            threshold=rule.threshold,
            severity=rule.severity,
            offending_samples=(offending_samples or {}).get(name, []),
        )
    return QualityGateReport(checks=checks)
