import json
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios("../features/f2-02-coco-ingest.feature")


@pytest.fixture
def context(tmp_path):
    return {
        "tmp_path": tmp_path,
        "input_path": tmp_path / "input.json",
        "output_path": tmp_path / "validated.json",
    }


@given("un JSON COCO que pasa F2-01")
def valid_coco(context):
    fixture = Path(__file__).parent / "fixtures" / "mp1-coco.json"
    context["input_path"].write_text(
        fixture.read_text(encoding="utf-8"),
        encoding="utf-8",
    )


@given("un JSON con bbox de 3 elementos")
def invalid_coco(context):
    fixture = Path(__file__).parent / "fixtures" / "mp1-coco.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    payload["annotations"][0]["bbox"] = [10, 20, 30]
    context["input_path"].write_text(
        json.dumps(payload),
        encoding="utf-8",
    )


@given("configuro rutas de ingesta por variables de entorno")
def configure_env(context, monkeypatch):
    monkeypatch.setenv("COCO_INPUT_PATH", str(context["input_path"]))
    monkeypatch.setenv("COCO_VALIDATED_PATH", str(context["output_path"]))


@when("corro la ingesta")
def run_ingest(context, monkeypatch):
    monkeypatch.setenv("COCO_INPUT_PATH", str(context["input_path"]))
    monkeypatch.setenv("COCO_VALIDATED_PATH", str(context["output_path"]))

    from dataset_quality.ingest import main

    context["exit_code"] = main()


@then("termina 0")
def exits_zero(context):
    assert context["exit_code"] == 0


@then("queda un artefacto de entrada para analizadores")
def artifact_exists(context):
    assert context["output_path"].exists()


@then("no se versionan las imágenes en git")
def no_images_written(context):
    image_files = list(context["tmp_path"].glob("*.jpg"))
    assert image_files == []


@then("termina distinto de 0")
def exits_nonzero(context):
    assert context["exit_code"] != 0


@then("el error nombra el campo")
def error_names_field(context, capsys):
    captured = capsys.readouterr()
    assert "bbox" in captured.err.lower() or "bbox" in captured.out.lower()


@then("no queda artefacto válido a medias")
def no_partial_artifact(context):
    assert not context["output_path"].exists()


@then("usa las rutas configuradas")
def uses_env_paths(context):
    assert context["output_path"].exists()
