"""CLI de la compuerta de calidad; F4-02 decide el código de salida."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from dataset_quality.quality_policy import (
    QualityGateReport,
    analyze_quality_inputs,
    collect_offending_samples,
    evaluate_quality_policy,
    load_quality_policy,
)

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


def quality_gate(
    coco_data: dict[str, Any],
    policy_path: str | Path,
    image_bytes: dict[str, bytes] | None = None,
) -> QualityGateReport:
    """Evalúa el COCO sin ejecutar etapas posteriores del pipeline."""
    policy = load_quality_policy(policy_path)
    observations = analyze_quality_inputs(coco_data, image_bytes)
    offenders = collect_offending_samples(coco_data, policy, observations, image_bytes)
    return evaluate_quality_policy(policy, observations, offenders)


def load_image_bytes(coco_data: dict[str, Any], images_dir: str | Path) -> dict[str, bytes]:
    """Carga las imágenes referenciadas por el COCO para el check pHash."""
    directory = Path(images_dir)
    if not directory.is_dir():
        return {}

    images: dict[str, bytes] = {}
    for image in coco_data.get("images", []):
        file_name = image.get("file_name")
        if not file_name:
            continue
        image_path = directory / file_name
        if image_path.is_file():
            images[str(image.get("id"))] = image_path.read_bytes()
    return images


def has_failures(report: QualityGateReport) -> bool:
    return any(check.status == "fail" for check in report.checks.values())


def format_gate_report(report: QualityGateReport) -> str:
    """Muestra cada resultado y destaca en rojo los checks bloqueantes."""
    lines = []
    for name, check in report.checks.items():
        color = RED if check.status == "fail" else GREEN
        lines.append(
            f"{color}{check.status.upper():4}{RESET} {name}: "
            f"observed={check.observed:g}, threshold={check.threshold:g}, "
            f"severity={check.severity}"
        )
    return "\n".join(lines)


def write_quality_report(report: QualityGateReport, output_path: str | Path) -> Path:
    """Escribe el contrato F1-05 en la ruta configurada."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        name: {
            "status": check.status,
            "observed": check.observed,
            "threshold": check.threshold,
            "offending_samples": check.offending_samples,
        }
        for name, check in report.checks.items()
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evalúa quality.yaml contra un COCO validado.")
    parser.add_argument("--coco", required=True, type=Path, help="Ruta al JSON COCO validado.")
    parser.add_argument(
        "--policy", default=Path("quality.yaml"), type=Path, help="Ruta a la política YAML."
    )
    parser.add_argument(
        "--output",
        default=Path(os.getenv("QUALITY_REPORT_PATH", "data/reports/quality.json")),
        type=Path,
        help="Ruta de salida para quality.json.",
    )
    parser.add_argument(
        "--images-dir",
        default=Path(os.getenv("COCO_IMAGES_PATH", "data/images")),
        type=Path,
        help="Directorio de imágenes referenciadas por el COCO para pHash.",
    )
    arguments = parser.parse_args(argv)

    coco_data = json.loads(arguments.coco.read_text(encoding="utf-8"))
    image_bytes = load_image_bytes(coco_data, arguments.images_dir)
    report = quality_gate(coco_data, arguments.policy, image_bytes)
    write_quality_report(report, arguments.output)
    print(format_gate_report(report))
    return 1 if has_failures(report) else 0


if __name__ == "__main__":
    raise SystemExit(main())
