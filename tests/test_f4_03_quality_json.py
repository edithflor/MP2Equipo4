from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from PIL import Image
from pytest_bdd import scenarios, then, when

from dataset_quality.gate import load_image_bytes, main, quality_gate
from dataset_quality.imbalance import analyze_class_imbalance
from dataset_quality.invalid_boxes import analyze_invalid_boxes
from dataset_quality.phash import analyze_duplicates
from dataset_quality.quality_policy import CHECK_DIRECTIONS
from dataset_quality.small_objects import analyze_small_objects
from dataset_quality.spatial_bias import analyze_spatial_bias
from dataset_quality.ui.overview import get_overview_metrics

ROOT = Path(__file__).parents[1]
COCO_PATH = ROOT / "tests/fixtures/mp1-coco.json"

scenarios("../features/f4-03-quality-json.feature")


@pytest.fixture
def context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    output_path = tmp_path / "configured" / "quality.json"
    monkeypatch.setenv("QUALITY_REPORT_PATH", str(output_path))
    monkeypatch.setenv("COCO_IMAGES_PATH", str(tmp_path / "no-images"))
    return {"output_path": output_path}


@when("corre el gate")
def run_gate(context: dict) -> None:
    context["exit_code"] = main(["--coco", str(COCO_PATH), "--policy", str(ROOT / "quality.yaml")])
    context["quality"] = json.loads(context["output_path"].read_text(encoding="utf-8"))


@then("quality.json lista cada check")
def quality_json_lists_every_check(context: dict) -> None:
    assert set(context["quality"]) == set(CHECK_DIRECTIONS)
    assert get_overview_metrics(context["output_path"]) == context["quality"]


@then("incluye observed")
def every_check_has_observed(context: dict) -> None:
    assert all("observed" in check for check in context["quality"].values())


@then("incluye threshold")
def every_check_has_threshold(context: dict) -> None:
    assert all("threshold" in check for check in context["quality"].values())


@then("incluye ids ofensores o lista vacía")
def every_check_has_offending_samples(context: dict) -> None:
    assert all(
        isinstance(check.get("offending_samples"), list) for check in context["quality"].values()
    )
    assert all(
        any("id" in key for key in sample) or "image1" in sample
        for check in context["quality"].values()
        for sample in check["offending_samples"]
        if isinstance(sample, dict)
    )


@then("los valores observed cuadran con F3-01..05 sobre el mismo COCO")
def observed_values_match_f3(context: dict) -> None:
    coco_data = json.loads(COCO_PATH.read_text(encoding="utf-8"))
    imbalance = analyze_class_imbalance(coco_data, min_images=0)
    small = analyze_small_objects(coco_data)
    duplicates = analyze_duplicates({})
    invalid = analyze_invalid_boxes(coco_data)
    spatial = analyze_spatial_bias(coco_data)
    quadrant_counts = spatial["quadrant_counts"]
    total_quadrants = sum(quadrant_counts.values())

    expected = {
        "min_images_per_class": min(imbalance["class_counts"].values()),
        "small_objects_percentage": small["percentage"],
        "class_imbalance_ratio": imbalance["ratio"],
        "duplicate_pairs": len(duplicates["pairs"]),
        "invalid_boxes": len(invalid["invalid_annotations"]),
        "spatial_bias_percentage": max(quadrant_counts.values()) / total_quadrants * 100,
    }

    assert {name: check["observed"] for name, check in context["quality"].items()} == expected


def test_report_is_written_even_when_gate_fails(tmp_path: Path) -> None:
    output_path = tmp_path / "quality.json"

    exit_code = main(
        [
            "--coco",
            str(COCO_PATH),
            "--policy",
            str(ROOT / "quality.yaml"),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code != 0
    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding="utf-8"))


def test_duplicate_observed_and_offenders_match_phash(tmp_path: Path) -> None:
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), "red").save(buffer, format="PNG")
    for name in ("one.png", "two.png"):
        (images_dir / name).write_bytes(buffer.getvalue())

    coco_data = {
        "images": [
            {"id": 1, "file_name": "one.png", "width": 32, "height": 32},
            {"id": 2, "file_name": "two.png", "width": 32, "height": 32},
        ],
        "categories": [],
        "annotations": [],
    }
    image_bytes = load_image_bytes(coco_data, images_dir)

    report = quality_gate(coco_data, ROOT / "quality.yaml", image_bytes)
    direct_f3 = analyze_duplicates(image_bytes)

    assert report.checks["duplicate_pairs"].observed == len(direct_f3["pairs"])
    assert report.checks["duplicate_pairs"].offending_samples == direct_f3["pairs"]
