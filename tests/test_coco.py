import json
from copy import deepcopy

import pytest
from pydantic import ValidationError

from dataset_quality.coco import CocoDataset


@pytest.fixture
def coco():
    """Muestra sintética con la forma del exportador MP1; no acredita A-01."""
    return {
        "info": {"description": "MP1", "version": "1.0", "year": 2026},
        "licenses": [{"id": 1, "name": "Uso interno", "url": ""}],
        "images": [{"id": 1, "file_name": "foto.jpg", "width": 640, "height": 480}],
        "categories": [{"id": 1, "name": "persona", "supercategory": "object"}],
        "annotations": [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "bbox": [10, 20, 100, 50],
                "area": 5000,
                "iscrowd": 0,
                "segmentation": [],
            }
        ],
    }


def test_mp1_json_round_trip(coco):
    dataset = CocoDataset.model_validate_json(json.dumps(coco))
    assert dataset.annotations[0].bbox == [10, 20, 100, 50]
    assert CocoDataset.model_validate_json(dataset.model_dump_json()) == dataset
    assert CocoDataset.model_validate(coco) == dataset


@pytest.mark.parametrize("collection", ["images", "categories", "annotations"])
def test_required_collections(coco, collection):
    del coco[collection]
    with pytest.raises(ValidationError) as error:
        CocoDataset.model_validate(coco)
    assert error.value.errors()[0]["loc"] == (collection,)


@pytest.mark.parametrize("collection", ["images", "categories", "annotations"])
def test_duplicate_ids_report_position(coco, collection):
    coco[collection].append(deepcopy(coco[collection][0]))
    with pytest.raises(ValidationError) as error:
        CocoDataset.model_validate(coco)
    assert error.value.errors()[0]["loc"] == (collection, 1, "id")


@pytest.mark.parametrize("field", ["image_id", "category_id"])
def test_missing_references_report_annotation(coco, field):
    coco["annotations"][0][field] = 999
    with pytest.raises(ValidationError) as error:
        CocoDataset.model_validate(coco)
    assert error.value.errors()[0]["loc"] == ("annotations", 0, field)


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", "1"),
        ("id", True),
        ("id", 1.5),
        ("id", -1),
        ("bbox", [1, 2, 3]),
        ("bbox", [1, 2, 3, 4, 5]),
        ("bbox", [0, 0, "10", 20]),
        ("bbox", [0, 0, True, 20]),
        ("bbox", [0, 0, float("nan"), 20]),
        ("area", float("inf")),
        ("iscrowd", True),
        ("iscrowd", 2),
    ],
)
def test_malformed_annotation_reports_field(coco, field, value):
    coco["annotations"][0][field] = value
    with pytest.raises(ValidationError) as error:
        CocoDataset.model_validate(coco)
    assert error.value.errors()[0]["loc"][:3] == ("annotations", 0, field)


@pytest.mark.parametrize("field,value", [("width", 0), ("height", -1), ("file_name", " ")])
def test_invalid_image(coco, field, value):
    coco["images"][0][field] = value
    with pytest.raises(ValidationError) as error:
        CocoDataset.model_validate(coco)
    assert error.value.errors()[0]["loc"] == ("images", 0, field)


def test_empty_dataset_is_structurally_valid():
    dataset = CocoDataset.model_validate({"images": [], "categories": [], "annotations": []})
    assert dataset.annotations == []


def test_quality_defects_are_preserved_for_analyzers(coco):
    coco["annotations"][0].update(bbox=[-10, 900, -5, 0], area=-12)
    dataset = CocoDataset.model_validate(coco)
    assert dataset.annotations[0].bbox == [-10, 900, -5, 0]
    assert dataset.annotations[0].area == -12


def test_optional_coco_metadata_is_preserved(coco):
    coco["images"][0]["coco_url"] = "https://example.test/foto.jpg"
    dataset = CocoDataset.model_validate(coco)
    assert dataset.model_dump()["images"][0]["coco_url"] == coco["images"][0]["coco_url"]


def test_malformed_json():
    with pytest.raises(ValidationError) as error:
        CocoDataset.model_validate_json('{"images":')
    assert error.value.errors()[0]["type"] == "json_invalid"
