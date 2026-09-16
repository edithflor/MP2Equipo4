import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f3-04-invalid-boxes.feature")


@pytest.fixture
def context():
    return {
        "coco": {"images": [{"id": 1, "width": 100, "height": 100}], "annotations": []},
        "result": None,
        "expected_id": None,
    }


@given("width < 0")
def step_width_negative(context):
    context["coco"]["annotations"].append(
        {"id": 101, "image_id": 1, "bbox": [10, 10, -5, 20], "area": 0}
    )
    context["expected_id"] = 101


@when("corro el analizador")
def step_run_analyzer(context):
    from dataset_quality.invalid_boxes import analyze_invalid_boxes

    context["result"] = analyze_invalid_boxes(context["coco"])


@then("se reporta como inválida")
def step_report_invalid(context):
    assert context["result"] is not None
    invalid_ids = [ann["id"] for ann in context["result"]["invalid_annotations"]]
    assert context["expected_id"] in invalid_ids


@given("height 0 o negativo")
def step_height_zero(context):
    context["coco"]["annotations"].append(
        {"id": 102, "image_id": 1, "bbox": [10, 10, 20, 0], "area": 0}
    )
    context["expected_id"] = 102


@then("se reporta")
def step_report_general(context):
    if context["result"] is None:
        step_run_analyzer(context)
    invalid_ids = [ann["id"] for ann in context["result"]["invalid_annotations"]]
    assert context["expected_id"] in invalid_ids


@given("una caja que se sale de width/height de su image")
def step_out_of_bounds(context):
    context["coco"]["annotations"].append(
        {"id": 103, "image_id": 1, "bbox": [90, 90, 20, 20], "area": 400}
    )
    context["expected_id"] = 103


@given("bbox 10x10 y area 999")
def step_incoherent_area(context):
    context["coco"]["annotations"].append(
        {"id": 104, "image_id": 1, "bbox": [0, 0, 10, 10], "area": 999}
    )
    context["expected_id"] = 104
