import pytest
from pytest_bdd import given, scenarios, then

from dataset_quality.volume import count_images_per_class

scenarios("../features/f2-04-volume-count.feature")


@pytest.fixture
def coco_data():
    """Estado inicial falso para las pruebas."""
    return {
        "categories": [{"id": 1, "name": "car"}, {"id": 2, "name": "person"}],
        "images": [{"id": 1}],
        "annotations": [],
    }


@given("1 imagen con 7 cajas de car")
def step_7_boxes_car(coco_data):
    coco_data["annotations"] = [
        {"image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 10]} for _ in range(7)
    ]


@then("car tiene 1 imagen")
def step_check_1_car(coco_data):
    assert count_images_per_class(coco_data).get("car", 0) == 1


@given("1 imagen con car y person")
def step_car_and_person(coco_data):
    coco_data["annotations"] = [
        {"image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 10]},
        {"image_id": 1, "category_id": 2, "bbox": [0, 0, 10, 10]},
    ]


@then("suma 1 a car y 1 a person")
def step_check_car_person(coco_data):
    result = count_images_per_class(coco_data)
    assert result.get("car", 0) == 1
    assert result.get("person", 0) == 1


@given("una image sin annotations")
def step_no_annotations(coco_data):
    coco_data["annotations"] = []


@then("no suma a ninguna clase")
def step_no_classes(coco_data):
    result = count_images_per_class(coco_data)
    assert len(result) == 0 or all(v == 0 for v in result.values())


@given("una sola caja con width <= 0")
def step_degenerate_box(coco_data):
    coco_data["annotations"] = [{"image_id": 1, "category_id": 1, "bbox": [0, 0, 0, 10]}]


@then("esa imagen no suma a esa clase")
def step_no_degenerate(coco_data):
    assert count_images_per_class(coco_data).get("car", 0) == 0
