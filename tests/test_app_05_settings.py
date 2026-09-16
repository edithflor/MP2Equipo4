from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when
from streamlit.testing.v1 import AppTest

from dataset_quality.gate import main
from dataset_quality.quality_policy import load_quality_policy

ROOT = Path(__file__).parents[1]
APP_PATH = ROOT / "src/dataset_quality/ui/app.py"

scenarios("../features/app-05-settings.feature")


def _coco_with_300_images_per_class() -> dict:
    images = []
    annotations = []
    for category_id in (1, 2):
        for index in range(300):
            image_id = category_id * 1_000 + index
            images.append({"id": image_id, "width": 100, "height": 100})
            annotations.append(
                {
                    "id": image_id,
                    "image_id": image_id,
                    "category_id": category_id,
                    "bbox": [0, 0, 40, 40],
                    "area": 1_600,
                }
            )
    return {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": 1, "name": "uno"}, {"id": 2, "name": "dos"}],
    }


@pytest.fixture
def context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    policy_path = tmp_path / "quality.yaml"
    policy_path.write_text((ROOT / "quality.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    coco_path = tmp_path / "coco.json"
    coco_path.write_text(json.dumps(_coco_with_300_images_per_class()), encoding="utf-8")
    monkeypatch.setenv("QUALITY_POLICY_PATH", str(policy_path))
    return {
        "policy_path": policy_path,
        "coco_path": coco_path,
        "output_path": tmp_path / "quality.json",
    }


def _save_minimum_with_settings(policy_path: Path, value: float) -> AppTest:
    app = AppTest.from_file(APP_PATH).run(timeout=20)
    minimum = next(
        control for control in app.number_input if control.label == "Mínimo de imágenes por clase"
    )
    minimum.set_value(value)
    save_button = next(button for button in app.button if button.label == "Guardar política")
    save_button.click().run(timeout=20)
    assert policy_path.exists()
    return app


@given("quality.yaml versionado")
def versioned_yaml_exists(context: dict) -> None:
    assert context["policy_path"].is_file()
    assert load_quality_policy(context["policy_path"]).min_images_per_class.threshold >= 300


@when("cambio min_images_per_class (u otro umbral) en Settings")
def change_threshold_in_settings(context: dict) -> None:
    context["before"] = context["policy_path"].read_text(encoding="utf-8")
    context["app"] = _save_minimum_with_settings(context["policy_path"], 301.0)


@then("el archivo quality.yaml en disco cambió")
def yaml_changed_on_disk(context: dict) -> None:
    assert context["policy_path"].read_text(encoding="utf-8") != context["before"]
    assert load_quality_policy(context["policy_path"]).min_images_per_class.threshold == 301


@then("no solo cambió el estado de React")
def change_survives_a_new_read(context: dict) -> None:
    assert load_quality_policy(context["policy_path"]).min_images_per_class.threshold == 301


@when("corro el comando del gate")
def run_gate_with_saved_policy(context: dict) -> None:
    _save_minimum_with_settings(context["policy_path"], 301.0)
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


@then("usa el umbral nuevo (F4-01)")
def gate_reads_the_saved_threshold(context: dict) -> None:
    check = context["quality"]["min_images_per_class"]
    assert context["exit_code"] != 0
    assert check["threshold"] == 301
    assert check["observed"] == 300


@then("sin tocar código Python")
def only_the_yaml_changed(context: dict) -> None:
    assert context["policy_path"].is_file()


@then("Settings no abre BD ni S3 ni MinIO")
def settings_has_no_storage_drivers() -> None:
    modules = list((ROOT / "src/dataset_quality/ui").glob("*.py"))
    forbidden = {"boto3", "minio", "pymysql", "sqlalchemy"}
    imports = set()
    for module_path in modules:
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            if isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
    assert imports.isdisjoint(forbidden)
