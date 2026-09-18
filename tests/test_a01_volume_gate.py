import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from pytest_bdd import given, scenarios, then, when

from dataset_quality.config import QualityPolicyConfig
from dataset_quality.gate import has_failures, quality_gate
from dataset_quality.quality_policy import load_quality_policy

ROOT = Path(__file__).parents[1]
scenarios("../features/a-01-volume-gate.feature")


@pytest.fixture
def context(attach_images):
    coco = {
        "images": [{"id": i, "width": 100, "height": 100} for i in range(1, 301)],
        "categories": [{"id": 1, "name": "car"}, {"id": 2, "name": "person"}],
        "annotations": [
            {"id": i * 2 + c, "image_id": i, "category_id": c, "bbox": [0, 0, 40, 40], "area": 1600}
            for i in range(1, 301)
            for c in (1, 2)
        ],
    }
    return {"coco": coco, "images": attach_images(coco)}


@given("quality.yaml con mínimo 300 y severidad fail")
def policy():
    rule = load_quality_policy(ROOT / "quality.yaml").min_images_per_class
    assert rule.threshold == 300 and rule.severity == "fail"


@when("cuento por clase después de colapsar duplicados")
def count(context):
    context["report"] = quality_gate(context["coco"], ROOT / "quality.yaml", context["images"])


@then("con 300 el check de mínimo pasa")
def passes(context):
    check = context["report"].checks["min_images_per_class"]
    assert check.observed == 300 and check.status == "pass"


@then("al duplicar una imagen quedan 299 y el gate falla")
def duplicate_blocks(context):
    context["images"]["300"] = context["images"]["1"]
    report = quality_gate(context["coco"], ROOT / "quality.yaml", context["images"])
    check = report.checks["min_images_per_class"]
    assert check.observed == 299
    assert check.status == "fail" and has_failures(report)
    assert all(row["missing_to_threshold"] == 1 for row in report.volume["classes"])


@then("una política con mínimo 50 o severidad warn se rechaza")
def cannot_weaken():
    for changes in ({"threshold": 50}, {"severity": "warn"}):
        payload = load_quality_policy(ROOT / "quality.yaml").model_dump()
        payload["min_images_per_class"].update(changes)
        with pytest.raises(ValidationError, match="min_images_per_class"):
            QualityPolicyConfig.model_validate(payload)


@then("imágenes ausentes o corruptas no permiten liberar el dataset")
def unverifiable_blocks(context):
    for images in ({}, {"1": b"not an image"}):
        report = quality_gate(context["coco"], ROOT / "quality.yaml", images)
        assert report.checks["min_images_per_class"].status == "fail"


def test_connected_components_and_invalid_boxes():
    from dataset_quality.volume import audit_volume

    coco = {
        "images": [{"id": i, "width": 100, "height": 100} for i in range(1, 5)],
        "categories": [{"id": 1, "name": "car"}, {"id": 2, "name": "person"}],
        "annotations": [
            {"image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 10], "area": 100},
            {"image_id": 3, "category_id": 1, "bbox": [0, 0, 10, 10], "area": 100},
            {"image_id": 3, "category_id": 2, "bbox": [0, 0, 10, 10], "area": 100},
            {"image_id": 4, "category_id": 2, "bbox": [0, 0, 0, 10], "area": 0},
        ],
    }
    result = audit_volume(
        coco,
        {
            "hashed_image_ids": ["1", "2", "3", "4"],
            "pairs": [{"image1": "1", "image2": "2"}, {"image1": "2", "image2": "3"}],
        },
    )
    assert [row["after_phash"] for row in result["classes"]] == [1, 1]


def test_cli_missing_images_is_red_and_writes_evidence(context, tmp_path):
    from dataset_quality.gate import main

    source = tmp_path / "coco.json"
    source.write_text(json.dumps(context["coco"]), encoding="utf-8")
    output = tmp_path / "quality.json"
    assert (
        main(
            [
                "--coco",
                str(source),
                "--output",
                str(output),
                "--images-dir",
                str(tmp_path / "absent"),
            ]
        )
        == 1
    )
    text = (tmp_path / "volume.md").read_text(encoding="utf-8")
    assert "car" in text and "300" in text and "NO VERIFICADO" in text


def test_cli_duplicates_writes_serializable_report(context, tmp_path, attach_images):
    from dataset_quality.gate import main

    coco = context["coco"]
    images_dir = tmp_path / "images"
    attach_images(coco, images_dir)
    (images_dir / "300.png").write_bytes((images_dir / "1.png").read_bytes())
    source = tmp_path / "coco.json"
    source.write_text(json.dumps(coco), encoding="utf-8")
    output = tmp_path / "quality.json"
    result = main(["--coco", str(source), "--images-dir", str(images_dir), "--output", str(output)])
    report = json.loads(output.read_text(encoding="utf-8"))
    assert result == 1
    assert report["min_images_per_class"]["observed"] == 299
    assert report["duplicate_pairs"]["offending_samples"][0]["distance"] == 0
    assert "Estado del check mínimo: fail" in (tmp_path / "volume.md").read_text(encoding="utf-8")
