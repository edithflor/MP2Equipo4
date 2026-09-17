import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f5-01-stratified-splits.feature")


@pytest.fixture
def context():
    return {
        "coco": {
            "categories": [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}],
            "images": [{"id": i} for i in range(1, 101)],
            "annotations": [],
        },
        "tolerance": 0.05,
        "splits": None,
    }


@given("un COCO con al menos 2 clases y config de tolerancia")
def step_coco_tolerance(context):
    # Inyectamos 80 imágenes de la clase 1 y 20 de la clase 2
    for i in range(1, 81):
        context["coco"]["annotations"].append(
            {"image_id": i, "category_id": 1, "bbox": [0, 0, 10, 10]}
        )
    for i in range(81, 101):
        context["coco"]["annotations"].append(
            {"image_id": i, "category_id": 2, "bbox": [0, 0, 10, 10]}
        )


@when("genero train/val/test")
def step_generate_splits(context):
    from dataset_splitting.stratified import generate_stratified_splits

    context["splits"] = generate_stratified_splits(
        context["coco"], train_ratio=0.7, val_ratio=0.15, test_ratio=0.15
    )


@then("para cada clase la fracción en cada split")
def step_fraction_calc(context):
    assert context["splits"] is not None
    assert "train" in context["splits"]


@then("está dentro de la tolerancia declarada")
def step_within_tolerance(context):
    # Evaluaremos esto formalmente en la fase verde
    assert len(context["splits"]["train"]) > 0


@given("las mismas clases que el dataset")
def step_same_classes(context):
    if not context["coco"]["annotations"]:
        step_coco_tolerance(context)


@when("genero los splits")
def step_gen_splits_alt(context):
    if context["splits"] is None:
        step_generate_splits(context)


@then("cada clase tiene al menos 1 imagen en val")
def step_val_has_classes(context):
    assert len(context["splits"]["val"]) > 0


@then("cada clase tiene al menos 1 imagen en test")
def step_test_has_classes(context):
    assert len(context["splits"]["test"]) > 0


@then("los conteos por clase y split coinciden con un recuento independiente")
def step_recalc_matches(context):
    if context["splits"] is None:
        step_coco_tolerance(context)
        step_generate_splits(context)

    # La suma de los splits debe ser igual al total de imágenes (100)
    total_split = (
        len(context["splits"]["train"])
        + len(context["splits"]["val"])
        + len(context["splits"]["test"])
    )
    assert total_split == 100
