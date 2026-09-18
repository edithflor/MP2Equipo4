import json

from dataset_quality.mcp.copilot import answer_dataset_question


def test_release_answer_uses_tool_data(tmp_path):
    quality = tmp_path / "quality.json"
    versions = tmp_path / "versions.json"
    diff = tmp_path / "diff.json"

    quality.write_text(
        json.dumps(
            {
                "min_images_per_class": {
                    "status": "fail",
                    "observed": 250,
                    "threshold": 300,
                    "offending_samples": [],
                }
            }
        ),
        encoding="utf-8",
    )

    versions.write_text(
        json.dumps(
            {
                "versions": [
                    {"version": "v0.1.0", "environment": "DEV"},
                    {"version": "v1.0.0", "environment": "DEV"},
                ]
            }
        ),
        encoding="utf-8",
    )

    diff.write_text(
        json.dumps(
            {
                "from": "v0.1.0",
                "to": "v1.0.0",
            }
        ),
        encoding="utf-8",
    )

    result = answer_dataset_question(
        "¿Por qué está bloqueado el release?",
        quality_path=str(quality),
        versions_path=str(versions),
        diff_path=str(diff),
    )

    assert "250" in result["answer"]
    assert "300" in result["answer"]
    assert result["dataset_version"] == "v1.0.0"
    assert "get_quality_report" in result["tools_used"]


def test_mutating_source_changes_answer(tmp_path):
    quality = tmp_path / "quality.json"
    versions = tmp_path / "versions.json"
    diff = tmp_path / "diff.json"

    versions.write_text(
        json.dumps(
            {
                "versions": [
                    {"version": "v1.0.0", "environment": "DEV"},
                ]
            }
        ),
        encoding="utf-8",
    )

    diff.write_text(
        json.dumps(
            {
                "from": "v0.1.0",
                "to": "v1.0.0",
            }
        ),
        encoding="utf-8",
    )

    quality.write_text(
        json.dumps(
            {
                "min_images_per_class": {
                    "status": "fail",
                    "observed": 250,
                    "threshold": 300,
                }
            }
        ),
        encoding="utf-8",
    )

    first = answer_dataset_question(
        "estado del release",
        quality_path=str(quality),
        versions_path=str(versions),
        diff_path=str(diff),
    )

    quality.write_text(
        json.dumps(
            {
                "min_images_per_class": {
                    "status": "pass",
                    "observed": 355,
                    "threshold": 300,
                }
            }
        ),
        encoding="utf-8",
    )

    second = answer_dataset_question(
        "estado del release",
        quality_path=str(quality),
        versions_path=str(versions),
        diff_path=str(diff),
    )

    assert first["answer"] != second["answer"]
    assert "250" in first["answer"]
    assert "355" in second["answer"]


def test_out_of_domain_question_does_not_invent():
    result = answer_dataset_question("¿Cuánto mide la Torre Eiffel?")

    assert "No puedo responder" in result["answer"]
    assert result["tools_used"] == []
    assert result["dataset_version"] == "unknown"

