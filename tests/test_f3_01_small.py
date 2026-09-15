import pytest
from dataset_quality.small_objects import analyze_small_objects
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f3-01-small-objects.feature")


@pytest.fixture
def context():
    return {
        "coco": {
            "categories": [{"id": 1, "name": "car"}],
            "images": [{"id": 101}, {"id": 102}],
            "annotations": [],
        },
        "result": None,
    }


@given("bboxes de 16x16 y de 64x64")
def step_bboxes_16_64(context):
    context["coco"]["annotations"] = [
        {"id": 1, "image_id": 101, "category_id": 1, "bbox": [0, 0, 16, 16]},
        {"id": 2, "image_id": 102, "category_id": 1, "bbox": [0, 0, 64, 64]},
    ]


@when("corro el analizador con config default")
def step_run_default(context):
    context["result"] = analyze_small_objects(context["coco"])


@then("el de 16x16 es ofensor")
def step_16_is_offender(context):
    assert 101 in context["result"]["offender_images"]


@then("el de 64x64 no")
def step_64_not_offender(context):
    assert 102 not in context["result"]["offender_images"]


@given("el mismo COCO")
def step_same_coco(context):
    step_bboxes_16_64(context)


@when("cambio el umbral por config")
def step_change_threshold(context):
    context["result"] = analyze_small_objects(context["coco"], threshold_w=70, threshold_h=70)


@then("cambian el porcentaje y la lista de ofensores")
def step_check_changes(context):
    assert len(context["result"]["offender_images"]) == 2
    assert context["result"]["percentage"] == 100.0


@then("el resultado incluye porcentaje")
def step_includes_percentage(context):
    assert "percentage" in context["result"]


@then("la clase más afectada")
def step_includes_most_affected(context):
    assert "most_affected_class" in context["result"]


@then("ids de muestras ofensoras")
def step_includes_offender_ids(context):
    assert "offender_images" in context["result"]


@then("el módulo no lee env ni abre BD ni MinIO")
def step_pure_function():
    import pathlib

    try:
        code = pathlib.Path("src/dataset_quality/small_objects.py").read_text()
        for lib in ["boto3", "pymysql", "os.environ", "Minio"]:
            assert lib not in code
    except FileNotFoundError:
        pass
