import json
from pathlib import Path

from dataset_quality.ui.overview import get_overview_metrics


def test_overview_reads_from_json(tmp_path) -> None:
    mock_data = {
        "gate_status": "pass",
        "metrics": {"total_images": 999, "total_boxes": 2000, "categories": 2, "failed_checks": 0},
    }
    mock_file = tmp_path / "quality.json"
    mock_file.write_text(json.dumps(mock_data))

    data = get_overview_metrics(mock_file)

    assert data["gate_status"] == "pass"
    assert data["metrics"]["total_images"] == 999


def test_view_has_no_db_drivers() -> None:
    view_code = Path("src/dataset_quality/ui/overview.py").read_text()
    forbidden_imports = ["boto3", "pymysql", "Minio", "create_engine", "sqlalchemy"]

    for lib in forbidden_imports:
        assert lib not in view_code, f"Importación prohibida encontrada en la vista: {lib}"
