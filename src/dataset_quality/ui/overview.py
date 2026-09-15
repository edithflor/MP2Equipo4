import json
from pathlib import Path
from typing import Any


def get_overview_metrics(json_path: str | Path) -> dict[str, Any]:
    path = Path(json_path)
    if not path.exists():
        return {
            "gate_status": "unknown",
            "metrics": {"total_images": 0, "total_boxes": 0, "categories": 0, "failed_checks": 0},
        }

    with open(path, encoding="utf-8") as file:
        return json.load(file)
