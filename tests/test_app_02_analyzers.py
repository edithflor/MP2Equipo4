from __future__ import annotations

import ast
import copy
import io
import json
from pathlib import Path

import pytest
from PIL import Image
from pytest_bdd import given, scenarios, then, when
from streamlit.testing.v1 import AppTest

from dataset_quality.ui.analyzers import TAB_SPECS, build_analyzer_report

scenarios("../features/app-02-analyzers.feature")


def test_streamlit_renders_five_analyzer_tabs_without_errors() -> None:
    app_path = Path(__file__).parents[1] / "src/dataset_quality/ui/app.py"
    app = AppTest.from_file(app_path).run(timeout=20)

    assert not app.exception
    assert [tab.label for tab in app.tabs] == [label for _, label in TAB_SPECS]


@pytest.fixture
def context() -> dict:
    coco = json.loads((Path(__file__).parent / "fixtures/mp1-coco.json").read_text())
    return {"coco": coco, "report": None, "original_report": None}


@then("existen las cinco rutas o tabs")
def five_tabs_exist() -> None:
    assert [key for key, _ in TAB_SPECS] == [
        "small_objects",
        "class_imbalance",
        "duplicates",
        "invalid_boxes",
        "spatial_bias",
    ]


@then("no es un único placeholder")
def tabs_are_not_placeholder(context: dict) -> None:
    report = build_analyzer_report(context["coco"])
    assert len(report) == 5
    assert len({id(section) for section in report.values()}) == 5


@given("la salida de F3 o quality.json")
def f3_output(context: dict) -> None:
    context["report"] = build_analyzer_report(context["coco"])


@then("cada pestaña muestra gráfica o tabla coherente con ese analizador")
def every_tab_has_real_data(context: dict) -> None:
    for key, _ in TAB_SPECS:
        section = context["report"][key]
        assert "chart" in section
        assert "metrics" in section


@then("las muestras ofensoras se pueden abrir o listar")
def offenders_are_listable(context: dict) -> None:
    for key, _ in TAB_SPECS:
        assert isinstance(context["report"][key]["offenders"], list)


@when("cambio datos y regenero el reporte")
def mutate_coco(context: dict) -> None:
    context["original_report"] = build_analyzer_report(context["coco"])
    mutated = copy.deepcopy(context["coco"])
    mutated["annotations"].append(
        {
            "id": 999,
            "image_id": 1,
            "category_id": 1,
            "bbox": [1, 1, 4, 4],
            "area": 16,
        }
    )
    context["report"] = build_analyzer_report(mutated)


@then("la UI no sigue mostrando series fijas")
def report_changes_with_data(context: dict) -> None:
    assert (
        context["report"]["small_objects"]["chart"]
        != context["original_report"]["small_objects"]["chart"]
    )
    assert (
        context["report"]["class_imbalance"]["chart"]
        != context["original_report"]["class_imbalance"]["chart"]
    )


@then("no importa boto3, Minio ni pymysql en las vistas")
def no_drivers_in_views() -> None:
    ui_root = Path("src/dataset_quality/ui")
    forbidden = {"boto3", "minio", "pymysql", "sqlalchemy"}
    for path in ui_root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            (node.module or "").split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        assert not imports.intersection(forbidden), f"Driver prohibido en {path}"


def test_duplicate_tab_uses_real_phash_output() -> None:
    image = Image.new("RGB", (64, 64), "red")
    first = io.BytesIO()
    second = io.BytesIO()
    image.save(first, format="PNG")
    image.save(second, format="JPEG")
    coco = {
        "images": [
            {"id": "a.png", "file_name": "a.png", "width": 64, "height": 64},
            {"id": "b.jpg", "file_name": "b.jpg", "width": 64, "height": 64},
        ],
        "categories": [],
        "annotations": [],
    }

    report = build_analyzer_report(coco, {"a.png": first.getvalue(), "b.jpg": second.getvalue()})

    assert report["duplicates"]["metrics"]["pair_count"] == 1
    assert report["duplicates"]["offenders"][0]["image1"] == "a.png"
