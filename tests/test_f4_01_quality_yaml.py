from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError
from pytest_bdd import given, scenarios, then, when

from dataset_quality.config import QualityPolicyConfig
from dataset_quality.quality_policy import (
    CHECK_DIRECTIONS,
    analyze_quality_inputs,
    evaluate_quality_policy,
    load_quality_policy,
)

scenarios("../features/f4-01-quality-yaml.feature")


def _passing_coco() -> dict:
    images = []
    annotations = []
    for category_id in (1, 2):
        for index in range(300):
            image_id = category_id * 1_000 + index
            images.append(
                {
                    "id": image_id,
                    "file_name": f"class-{category_id}-{index}.jpg",
                    "width": 100,
                    "height": 100,
                }
            )
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


@pytest.fixture
def context(tmp_path: Path) -> dict:
    coco_data = _passing_coco()
    return {
        "path": tmp_path / "quality.yaml",
        "observations": analyze_quality_inputs(coco_data),
        "policy": load_quality_policy(),
        "validation_error": None,
    }


@given("quality.yaml")
def quality_yaml_exists(context: dict) -> None:
    assert context["policy"].min_images_per_class.threshold >= 300


@then("min_images_per_class >= 300")
def course_minimum_is_enforced(context: dict) -> None:
    assert context["policy"].min_images_per_class.threshold >= 300


@then("su severidad es fail")
def course_minimum_is_a_failure(context: dict) -> None:
    assert context["policy"].min_images_per_class.severity == "fail"


@given("un dataset que pasaba")
def dataset_passes_current_policy(context: dict) -> None:
    report = evaluate_quality_policy(context["policy"], context["observations"])
    assert all(check.status == "pass" for check in report.checks.values())


@when("pongo min_images_per_class: 99999")
def increase_minimum_in_yaml(context: dict) -> None:
    raw_policy = yaml.safe_load(Path("quality.yaml").read_text(encoding="utf-8"))
    raw_policy["min_images_per_class"]["threshold"] = 99_999
    context["path"].write_text(yaml.safe_dump(raw_policy), encoding="utf-8")
    context["policy"] = load_quality_policy(context["path"])


@then("ese check falla")
def raised_minimum_fails_without_a_code_change(context: dict) -> None:
    report = evaluate_quality_policy(context["policy"], context["observations"])
    assert report.checks["min_images_per_class"].status == "fail"


@then("no cambié código Python")
def only_yaml_changed(context: dict) -> None:
    assert context["path"].exists()


@when("el YAML está malformado")
def invalid_yaml_schema_is_loaded(context: dict) -> None:
    raw_policy = yaml.safe_load(Path("quality.yaml").read_text(encoding="utf-8"))
    raw_policy["min_images_per_class"]["threshold"] = "no-es-un-número"
    context["path"].write_text(yaml.safe_dump(raw_policy), encoding="utf-8")
    with pytest.raises(ValidationError) as error:
        load_quality_policy(context["path"])
    context["validation_error"] = error.value


@then("pydantic nombra el campo")
def pydantic_reports_invalid_field(context: dict) -> None:
    assert "min_images_per_class.threshold" in str(context["validation_error"])


@then("no se usa el dict crudo de yaml.safe_load como config")
def config_is_a_validated_model(context: dict) -> None:
    assert isinstance(context["policy"], QualityPolicyConfig)


def test_policy_has_a_configurable_check_for_each_f3_analyzer() -> None:
    assert set(QualityPolicyConfig.model_fields) - {"version"} == set(CHECK_DIRECTIONS)


def test_check_severity_controls_gate_result() -> None:
    policy = load_quality_policy()
    observations = {name: 0.0 for name in CHECK_DIRECTIONS}
    observations["min_images_per_class"] = 299.0

    report = evaluate_quality_policy(policy, observations)

    assert report.checks["min_images_per_class"].status == "fail"
