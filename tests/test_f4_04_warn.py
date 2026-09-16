from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from pytest_bdd import given, scenarios, then, when

from dataset_quality.gate import main

ROOT = Path(__file__).parents[1]

scenarios("../features/f4-04-warn.feature")


def _coco_with_small_object() -> dict:
    images = []
    annotations = []
    for category_id in (1, 2):
        for index in range(300):
            image_id = category_id * 1_000 + index
            images.append({"id": image_id, "width": 100, "height": 100})
            bbox = [0, 0, 10, 10] if image_id == 1_000 else [0, 0, 40, 40]
            annotations.append(
                {
                    "id": image_id,
                    "image_id": image_id,
                    "category_id": category_id,
                    "bbox": bbox,
                    "area": bbox[2] * bbox[3],
                }
            )
    return {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": "uno"}, {"id": 2, "name": "dos"}],
    }


@pytest.fixture
def context(tmp_path: Path) -> dict:
    return {
        "coco_path": tmp_path / "coco.json",
        "policy_path": tmp_path / "quality.yaml",
        "output_path": tmp_path / "quality.json",
    }


@given("checks en warn y ninguno en fail")
def only_warns_are_configured(context: dict) -> None:
    policy = yaml.safe_load((ROOT / "quality.yaml").read_text(encoding="utf-8"))
    policy["small_objects_percentage"]["threshold"] = 0
    policy["small_objects_percentage"]["severity"] = "warn"
    context["coco_path"].write_text(json.dumps(_coco_with_small_object()), encoding="utf-8")
    context["policy_path"].write_text(yaml.safe_dump(policy), encoding="utf-8")


@when("corro el gate")
def run_gate_with_warns(context: dict) -> None:
    context["exit_code"] = main(
        [
            "--coco",
            str(context["coco_path"]),
            "--policy",
            str(context["policy_path"]),
            "--output",
            str(context["output_path"]),
            "--images-dir",
            str(context["coco_path"].parent / "no-images"),
        ]
    )
    context["quality"] = json.loads(context["output_path"].read_text(encoding="utf-8"))


@then("exit es 0")
def warns_keep_a_zero_exit(context: dict) -> None:
    assert context["exit_code"] == 0


@then("quality.json registra los warn")
def quality_json_keeps_warns(context: dict) -> None:
    assert context["quality"]["small_objects_percentage"]["status"] == "warn"


@then("observed vs threshold siguen presentes")
def warned_check_keeps_evidence(context: dict) -> None:
    check = context["quality"]["small_objects_percentage"]
    assert check["observed"] > check["threshold"]
    assert check["offending_samples"] == [1_000]


def test_warn_is_green_while_fail_is_red(tmp_path: Path) -> None:
    context = {
        "coco_path": tmp_path / "coco.json",
        "policy_path": tmp_path / "quality.yaml",
        "output_path": tmp_path / "quality.json",
    }
    only_warns_are_configured(context)

    warn_exit = main(
        [
            "--coco",
            str(context["coco_path"]),
            "--policy",
            str(context["policy_path"]),
            "--output",
            str(context["output_path"]),
        ]
    )
    policy = yaml.safe_load(context["policy_path"].read_text(encoding="utf-8"))
    policy["min_images_per_class"]["threshold"] = 99_999
    context["policy_path"].write_text(yaml.safe_dump(policy), encoding="utf-8")
    fail_exit = main(
        [
            "--coco",
            str(context["coco_path"]),
            "--policy",
            str(context["policy_path"]),
            "--output",
            str(context["output_path"]),
        ]
    )

    assert warn_exit == 0
    assert fail_exit != 0
