import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f3-05-spatial-bias.feature")


@pytest.fixture
def context():
    return {
        "coco": {"images": [{"id": 1, "width": 100, "height": 100}], "annotations": []},
        "result": None,
        "expected": {},
    }


@given("un set de áreas conocido")
def step_known_areas(context):
    areas = [10, 20, 30, 40, 50]
    context["coco"]["annotations"] = [
        {"id": i, "image_id": 1, "bbox": [0, 0, a, 1], "area": a} for i, a in enumerate(areas)
    ]
    context["expected"] = {"mean": 30.0, "median": 30.0, "p25": 20.0, "p75": 40.0}


@when("corro el analizador")
def step_run_analyzer(context):
    from dataset_quality.spatial_bias import analyze_spatial_bias

    context["result"] = analyze_spatial_bias(context["coco"])


@then("reporta media")
def step_report_mean(context):
    assert "mean_area" in context["result"]


@then("mediana")
def step_report_median(context):
    assert "median_area" in context["result"]


@then("al menos p25 y p75 o p90")
def step_report_percentiles(context):
    assert "p25_area" in context["result"] and "p75_area" in context["result"]


@given("cajas concentradas en un cuadrante")
def step_concentrated_boxes(context):
    context["coco"]["annotations"] = [
        {"id": 101, "image_id": 1, "bbox": [10, 10, 10, 10], "area": 100},
        {"id": 102, "image_id": 1, "bbox": [20, 20, 10, 10], "area": 100},
        {"id": 103, "image_id": 1, "bbox": [30, 30, 10, 10], "area": 100},
        {"id": 104, "image_id": 1, "bbox": [80, 80, 10, 10], "area": 100},
    ]


@then("el reporte refleja esa concentración")
def step_reflects_concentration(context):
    if context["result"] is None:
        step_run_analyzer(context)

    quadrants = context["result"].get("quadrant_counts", {})
    assert quadrants.get("TL", 0) == 3
    assert quadrants.get("BR", 0) == 1


@then("no es solo la media del área")
def step_not_only_mean(context):
    assert "quadrant_counts" in context["result"]


@then("media/mediana/percentiles cuadran con el test")
def step_recalc_matches(context):
    if not context["coco"]["annotations"]:
        step_known_areas(context)
    if context["result"] is None:
        step_run_analyzer(context)

    assert context["result"]["mean_area"] == context["expected"]["mean"]
    assert context["result"]["median_area"] == context["expected"]["median"]
    assert abs(context["result"]["p25_area"] - context["expected"]["p25"]) <= 5
