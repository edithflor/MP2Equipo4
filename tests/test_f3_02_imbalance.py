import pytest
from dataset_quality.imbalance import analyze_class_imbalance
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f3-02-class-imbalance.feature")


@pytest.fixture
def context():
    return {
        "coco": {"categories": [], "images": [], "annotations": []},
        "result": {},
        "min_images": 300,
    }


@given("clase A con 400 imágenes y B con 100")
def step_given_classes(context):
    context["coco"]["categories"] = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
    annotations = []
    for i in range(1, 401):
        annotations.append({"image_id": i, "category_id": 1, "bbox": [0, 0, 10, 10]})
    for i in range(401, 501):
        annotations.append({"image_id": i, "category_id": 2, "bbox": [0, 0, 10, 10]})
    context["coco"]["annotations"] = annotations


@when("corro el analizador")
def step_run_analyzer(context):
    context["result"] = analyze_class_imbalance(context["coco"], min_images=context["min_images"])


@then("el ratio es 4.0")
def step_check_ratio(context):
    assert context["result"].get("ratio") == 4.0


@given("min_images_per_class = 300")
def step_min_images(context):
    context["min_images"] = 300


@given("una clase con 250 imágenes distintas")
def step_class_under_min(context):
    context["coco"]["categories"] = [{"id": 3, "name": "C"}]
    annotations = []
    for i in range(1, 251):
        annotations.append({"image_id": i, "category_id": 3, "bbox": [0, 0, 10, 10]})
    context["coco"]["annotations"] = annotations


@then("esa clase aparece bajo el mínimo")
def step_check_under_min(context):
    if not context["result"]:
        context["result"] = analyze_class_imbalance(
            context["coco"], min_images=context["min_images"]
        )
    assert "C" in context["result"].get("classes_under_minimum", [])


@given("una imagen con 7 cajas de la misma clase")
def step_7_boxes(context):
    context["coco"]["categories"] = [{"id": 4, "name": "D"}]
    context["coco"]["annotations"] = [
        {"image_id": 999, "category_id": 4, "bbox": [0, 0, 10, 10]} for _ in range(7)
    ]


@then("aporta 1 a esa clase")
def step_check_contribution(context):
    if not context["result"]:
        context["result"] = analyze_class_imbalance(
            context["coco"], min_images=context["min_images"]
        )
    assert context["result"].get("class_counts", {}).get("D") == 1
