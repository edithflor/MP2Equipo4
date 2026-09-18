from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from pytest_bdd import given, scenarios, then, when

from dataset_quality.gate import has_failures, quality_gate
from dataset_quality.pipeline import continue_after_gate

ROOT = Path(__file__).parents[1]

scenarios("../features/f4-02-gate-blocks.feature")


@pytest.fixture
def context() -> dict:
    return {}


def _passing_coco() -> dict:
    images = []
    annotations = []
    for category_id in (1, 2):
        for index in range(300):
            image_id = category_id * 1_000 + index
            images.append({"id": image_id, "width": 100, "height": 100})
            x, y = ((index % 4) % 2) * 50, ((index % 4) // 2) * 50
            annotations.append(
                {
                    "id": image_id,
                    "image_id": image_id,
                    "category_id": category_id,
                    "bbox": [x, y, 40, 40],
                    "area": 1_600,
                }
            )
    return {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": "uno"}, {"id": 2, "name": "dos"}],
    }


def _impossible_policy(path: Path) -> None:
    policy = yaml.safe_load((ROOT / "quality.yaml").read_text(encoding="utf-8"))
    policy["min_images_per_class"]["threshold"] = 99_999
    path.write_text(yaml.safe_dump(policy), encoding="utf-8")


def _run_gate(coco_path: Path, policy_path: Path) -> subprocess.CompletedProcess[str]:
    environment = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dataset_quality.gate",
            "--coco",
            str(coco_path),
            "--policy",
            str(policy_path),
            "--output",
            str(coco_path.parent / "quality.json"),
            "--images-dir",
            str(coco_path.parent / "no-images"),
        ],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def _failed_report(tmp_path: Path):
    policy_path = tmp_path / "quality.yaml"
    _impossible_policy(policy_path)
    return quality_gate(_passing_coco(), policy_path)


@given("un fail inducido (umbral imposible)")
def induced_fail(context: dict, tmp_path: Path) -> None:
    context["coco_path"] = tmp_path / "coco.json"
    context["policy_path"] = tmp_path / "quality.yaml"
    context["coco_path"].write_text(json.dumps(_passing_coco()), encoding="utf-8")
    _impossible_policy(context["policy_path"])


@when("corro el comando del gate")
def execute_gate_command(context: dict) -> None:
    context["process"] = _run_gate(context["coco_path"], context["policy_path"])


@then("el exit code es distinto de 0")
def gate_returns_nonzero(context: dict) -> None:
    assert context["process"].returncode != 0
    assert "FAIL" in context["process"].stdout


@given("el orquestador (CLI o dvc.yaml)")
def orchestrator_is_ready(context: dict, tmp_path: Path) -> None:
    context["report"] = _failed_report(tmp_path)
    context["stages"] = []


@when("el gate falla")
def failed_gate_stops_orchestration(context: dict) -> None:
    context["continued"] = continue_after_gate(
        context["report"],
        split=lambda: context["stages"].append("split"),
        export=lambda: context["stages"].append("export"),
        promote_prod=lambda: context["stages"].append("prod"),
    )


@then("split no se ejecuta")
def split_is_not_executed(context: dict) -> None:
    assert context["continued"] is False
    assert "split" not in context["stages"]


@then("no hay promoción a PROD")
def prod_is_not_promoted(context: dict) -> None:
    assert "prod" not in context["stages"]


@then("no se continúa el pipeline después de un fail")
def fail_never_continues_pipeline(tmp_path: Path) -> None:
    stages: list[str] = []
    continued = continue_after_gate(
        _failed_report(tmp_path),
        split=lambda: stages.append("split"),
        export=lambda: stages.append("export"),
        promote_prod=lambda: stages.append("prod"),
    )

    assert continued is False
    assert stages == []


def test_gate_returns_zero_for_a_passing_policy(tmp_path: Path) -> None:
    coco_path = tmp_path / "coco.json"
    coco_path.write_text(json.dumps(_passing_coco()), encoding="utf-8")

    process = _run_gate(coco_path, ROOT / "quality.yaml")

    assert process.returncode == 0
    assert "PASS" in process.stdout


def test_only_warns_allow_following_stages(tmp_path: Path) -> None:
    policy_path = tmp_path / "quality.yaml"
    policy = yaml.safe_load((ROOT / "quality.yaml").read_text(encoding="utf-8"))
    policy["min_images_per_class"]["threshold"] = 300
    policy["small_objects_percentage"]["threshold"] = 0
    policy_path.write_text(yaml.safe_dump(policy), encoding="utf-8")
    coco_data = _passing_coco()
    coco_data["annotations"][0]["bbox"] = [0, 0, 10, 10]
    coco_data["annotations"][0]["area"] = 100
    report = quality_gate(coco_data, policy_path)
    stages: list[str] = []

    continued = continue_after_gate(
        report,
        split=lambda: stages.append("split"),
        export=lambda: stages.append("export"),
        promote_prod=lambda: stages.append("prod"),
    )

    assert not has_failures(report)
    assert continued is True
    assert stages == ["split", "export", "prod"]
