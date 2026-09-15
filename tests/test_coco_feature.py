"""Escenarios ejecutables de SPEC-F2-01 sobre datos extraídos del MP1."""

import ast
import inspect
import json
from pathlib import Path

from pydantic import BaseModel, ValidationError
from pytest_bdd import given, parsers, scenarios, then, when

from dataset_quality import coco as coco_module
from dataset_quality.coco import CocoAnnotation, CocoCategory, CocoDataset, CocoImage

scenarios("../features/f2-01-pydantic-coco.feature")


@given("un JSON con images, annotations, categories coherentes", target_fixture="context")
def coherent_json():
    payload = json.loads((Path(__file__).parent / "fixtures/mp1-coco.json").read_text())
    return {"payload": payload}


def parse(context):
    try:
        context["dataset"] = CocoDataset.model_validate_json(json.dumps(context["payload"]))
    except ValidationError as error:
        context["error"] = error


@when("lo parseo")
def parse_valid(context):
    parse(context)


@then("obtengo modelos v2")
def typed_models(context):
    dataset = context["dataset"]
    assert isinstance(dataset, BaseModel)
    assert len(dataset.images) == 5
    assert len(dataset.annotations) == 8
    assert all(isinstance(item, CocoImage) for item in dataset.images)
    assert all(isinstance(item, CocoCategory) for item in dataset.categories)
    assert all(isinstance(item, CocoAnnotation) for item in dataset.annotations)
    assert CocoDataset.model_fields["images"].annotation == list[CocoImage]
    assert CocoDataset.model_fields["categories"].annotation == list[CocoCategory]
    assert CocoDataset.model_fields["annotations"].annotation == list[CocoAnnotation]


@when("inyecto bbox de 3 elementos")
def invalid_bbox(context):
    context["payload"]["annotations"][0]["bbox"] = [10, 20, 30]
    parse(context)


@when("una annotation apunta a una categoría que no está")
def missing_category(context):
    context["payload"]["annotations"][0]["category_id"] = 999999
    parse(context)


@when("una annotation apunta a una imagen que no está")
def missing_image(context):
    context["payload"]["annotations"][0]["image_id"] = 999999
    parse(context)


@then(parsers.parse("falla y el error nombra {field}"))
def named_error(context, field):
    error = context["error"]
    assert isinstance(error, ValidationError)
    assert ("annotations", 0, field) in [issue["loc"] for issue in error.errors()]
    assert field in str(error)


@then("no es un KeyError crudo")
def no_raw_key_error(context):
    assert not isinstance(context["error"], KeyError)


@given("el código", target_fixture="source_tree")
def source_tree():
    return ast.parse(inspect.getsource(coco_module))


@then("no usa pydantic.v1 ni validator ni dict de v1")
def v2_only(source_tree):
    imported = set()
    for node in ast.walk(source_tree):
        if isinstance(node, ast.ImportFrom):
            assert not (node.module or "").startswith("pydantic.v1")
            imported.update(alias.name for alias in node.names)
        if isinstance(node, ast.Import):
            assert all(not alias.name.startswith("pydantic.v1") for alias in node.names)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr != "dict"
    assert "validator" not in imported
    assert {"ConfigDict", "field_validator", "model_validator"} <= imported
