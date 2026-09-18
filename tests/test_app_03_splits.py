from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when
from streamlit.testing.v1 import AppTest

from dataset_quality.ui.splits_view import (
    compute_class_distribution_by_split,
    load_split_contract_or_json,
)
from dataset_splitting.pipeline import create_split_contract

ROOT = Path(__file__).parents[1]
APP_PATH = ROOT / "src/dataset_quality/ui/app.py"

scenarios("../features/app-03-splits.feature")


@pytest.fixture
def context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    coco = {
        "categories": [{"id": 1, "name": "A"}],
        "images": [{"id": i, "file_name": f"img_{i}.jpg"} for i in range(1, 101)],
        "annotations": [
            {"id": i, "image_id": i, "category_id": 1, "bbox": [0, 0, 10, 10], "area": 100}
            for i in range(1, 101)
        ],
    }

    config = {"train_ratio": 0.70, "val_ratio": 0.15, "test_ratio": 0.15, "seed": 42}

    # Primero creamos el split para ver qué imágenes están en el mismo split
    from dataset_splitting.stratified import generate_stratified_splits

    initial_splits = generate_stratified_splits(
        coco, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42
    )
    # Seleccionamos dos imágenes de train para garantizar 0 leaked pairs
    img1, img2 = initial_splits["train"][0], initial_splits["train"][1]
    phash_pairs = [{"image1": img1, "image2": img2, "distance": 0}]


    contract = create_split_contract(coco, config, phash_pairs)

    splits_file = tmp_path / "splits.json"
    splits_file.write_text(json.dumps(contract), encoding="utf-8")

    monkeypatch.setenv("SPLITS_REPORT_PATH", str(splits_file))
    monkeypatch.setenv("OVERVIEW_GATE_STATUS", "pass")

    return {
        "coco": coco,
        "config": config,
        "phash_pairs": phash_pairs,
        "contract": contract,
        "splits_file": splits_file,
        "app": None,
    }



@given("splits.json de una corrida real")
def given_splits_real_run(context: dict) -> None:
    assert context["splits_file"].exists()
    loaded = load_split_contract_or_json(context["splits_file"])
    assert loaded is not None
    assert "splits" in loaded


@when("abro Splits")
def open_splits(context: dict) -> None:
    app = AppTest.from_file(APP_PATH).run(timeout=20)
    assert not app.exception
    context["app"] = app


@then("veo conteos por clase en train, val y test")
def check_counts_displayed(context: dict) -> None:
    distribution = compute_class_distribution_by_split(
        context["coco"], context["contract"]["splits"]
    )
    assert len(distribution) == len(context["coco"]["categories"])
    for item in distribution:
        assert "train" in item
        assert "val" in item
        assert "test" in item
        assert item["train"] + item["val"] + item["test"] == item["total"]



@then("coinciden con F5-01 / F5-04")
def check_counts_match_f5(context: dict) -> None:
    distribution = compute_class_distribution_by_split(
        context["coco"], context["contract"]["splits"]
    )
    a_row = next(r for r in distribution if r["category"] == "A")

    assert a_row["total"] == 100
    assert a_row["train"] == 70
    assert a_row["val"] == 15
    assert a_row["test"] == 15

    splits = context["contract"]["splits"]
    assert len(splits["train"]) == 70
    assert len(splits["val"]) == 15
    assert len(splits["test"]) == 15


@then("el check de pares cruzados coincide con F5-03")
def check_leakage_matches_f5_03(context: dict) -> None:
    leakage = context["contract"]["leakage_validation"]
    assert leakage["leaked_pairs"] == 0
    assert leakage["intersection_train_val"] == 0
    assert leakage["intersection_train_test"] == 0
    assert leakage["intersection_val_test"] == 0
    assert leakage["union_matches_dataset"] is True


@then("si hay 0 leaked pairs, los pares pHash están en el mismo split")
def check_phash_pairs_same_split(context: dict) -> None:
    splits = context["contract"]["splits"]
    train_set = set(splits["train"])
    val_set = set(splits["val"])
    test_set = set(splits["test"])

    for pair in context["phash_pairs"]:
        img1 = pair["image1"]
        img2 = pair["image2"]
        same_split = (
            (img1 in train_set and img2 in train_set)
            or (img1 in val_set and img2 in val_set)
            or (img1 in test_set and img2 in test_set)
        )
        assert same_split


@then("la vista no abre BD ni MinIO ni S3")
def view_has_no_db_or_storage_drivers() -> None:
    view_path = ROOT / "src/dataset_quality/ui/splits_view.py"
    tree = ast.parse(view_path.read_text(encoding="utf-8"))
    forbidden = {"boto3", "minio", "pymysql", "sqlalchemy"}

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert imports.isdisjoint(
        forbidden
    ), f"Importaciones prohibidas encontradas: {imports & forbidden}"



@given("un gate en fail")
def given_gate_fail(monkeypatch: pytest.MonkeyPatch, context: dict) -> None:
    monkeypatch.setenv("OVERVIEW_GATE_STATUS", "fail")


@then('esta pantalla muestra "no hay split / bloqueado", no un train/val/test fake')
def check_screen_blocked_on_gate_fail(context: dict) -> None:
    app = AppTest.from_file(APP_PATH).run(timeout=20)
    error_texts = [err.value for err in app.error]
    assert any("no hay split / bloqueado" in txt for txt in error_texts)

