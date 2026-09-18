"""CLI de la compuerta de calidad; F4-02 decide el código de salida."""

from __future__ import annotations

import argparse
import io
import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from dataset_quality.phash import analyze_duplicates
from dataset_quality.quality_policy import (
    CheckResult,
    QualityGateReport,
    analyze_quality_inputs,
    collect_offending_samples,
    evaluate_quality_policy,
    load_quality_policy,
)
from dataset_quality.volume import audit_volume

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


def verify_images(
    coco_data: dict[str, Any], images: dict[str, bytes] | None
) -> tuple[bool, list[str]]:
    """Verifica que las imágenes existan y puedan abrirse."""
    if images is None:
        return True, []

    has_files = any("file_name" in img for img in coco_data.get("images", []))
    if not has_files and not images:
        return True, []

    missing_or_corrupt: list[str] = []
    for image in coco_data.get("images", []):
        image_id = str(image.get("id"))
        payload = images.get(image_id) if image_id in images else images.get(image.get("id"))
        if payload is None:
            missing_or_corrupt.append(image_id)
            continue
        try:
            if isinstance(payload, bytes):
                with Image.open(io.BytesIO(payload)) as decoded:
                    decoded.verify()
            else:
                with Image.open(payload) as decoded:
                    decoded.verify()
        except (OSError, ValueError, TypeError, Exception):
            missing_or_corrupt.append(image_id)

    return not missing_or_corrupt, missing_or_corrupt


def quality_gate(
    coco_data: dict[str, Any],
    policy_path: str | Path,
    image_bytes: dict[str, bytes] | None = None,
) -> QualityGateReport:
    """Evalúa el COCO sin ejecutar etapas posteriores del pipeline."""
    policy = load_quality_policy(policy_path)
    observations = analyze_quality_inputs(coco_data, image_bytes)
    offenders = collect_offending_samples(coco_data, policy, observations, image_bytes)
    report = evaluate_quality_policy(policy, observations, offenders)

    verified, unverifiable = verify_images(coco_data, image_bytes)

    image_audit = analyze_duplicates(image_bytes or {})
    if "hashed_image_ids" not in image_audit or not image_audit["hashed_image_ids"]:
        image_audit["hashed_image_ids"] = [
            str(img.get("id")) for img in coco_data.get("images", [])
        ]

    volume = audit_volume(
        coco_data,
        image_audit,
        threshold=int(policy.min_images_per_class.threshold),
    )
    report.volume = volume
    report.verified = verified

    observed = min(
        (row["after_phash"] for row in volume["classes"]),
        default=0,
    )

    if not verified:
        report.checks["min_images_per_class"] = CheckResult(
            status="fail",
            observed=float(observed),
            threshold=float(policy.min_images_per_class.threshold),
            severity=policy.min_images_per_class.severity,
            offending_samples=unverifiable,
        )
    else:
        status = (
            "pass"
            if observed >= policy.min_images_per_class.threshold
            else policy.min_images_per_class.severity
        )
        report.checks["min_images_per_class"] = CheckResult(
            status=status,
            observed=float(observed),
            threshold=float(policy.min_images_per_class.threshold),
            severity=policy.min_images_per_class.severity,
            offending_samples=offenders.get("min_images_per_class", []) if status != "pass" else [],
        )

    return report


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


def json_safe(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    return value


def format_volume_markdown(report: QualityGateReport) -> str:
    check = report.checks.get("min_images_per_class")
    status = check.status if check else "fail"
    status_str = f"{status} NO VERIFICADO" if not report.verified else status

    lines = [
        "# A-01 — Reporte de Volumen y Compuerta F4\n",
        f"Estado del check mínimo: {status_str}\n",
    ]
    if check:
        lines.append(f"- **Umbral mínimo requerido:** {check.threshold:g}")
        lines.append(f"- **Observado tras pHash:** {check.observed:g}\n")

    lines.append("| Clase | Antes de pHash | Tras pHash | Faltante para umbral |")
    lines.append("| :--- | :---: | :---: | :---: |")
    for row in report.volume.get("classes", []):
        lines.append(
            f"| {row['class']} | {row.get('before_phash', 0)} | "
            f"{row.get('after_phash', 0)} | {row.get('missing_to_threshold', 0)} |"
        )

    if report.volume.get("invalid_boxes"):
        lines.append(f"\n**Cajas inválidas ignoradas:** {len(report.volume['invalid_boxes'])}")

    return "\n".join(lines) + "\n"


def write_volume_markdown(report: QualityGateReport, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_volume_markdown(report), encoding="utf-8")
    return path


def write_quality_report(report: QualityGateReport, output_path: str | Path) -> Path:
    """Escribe el contrato F1-05 en la ruta configurada."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        name: {
            "status": check.status,
            "observed": check.observed,
            "threshold": check.threshold,
            "severity": check.severity,
            "offending_samples": check.offending_samples,
        }
        for name, check in report.checks.items()
    }
    if report.volume:
        payload["min_images_per_class"]["volume"] = report.volume

    path.write_text(
        json.dumps(json_safe(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
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
    parser.add_argument(
        "--volume-report",
        default=None,
        type=Path,
        help="Ruta alternativa para volume.md.",
    )
    arguments = parser.parse_args(argv)

    coco_data = json.loads(arguments.coco.read_text(encoding="utf-8"))
    image_bytes = load_image_bytes(coco_data, arguments.images_dir)
    report = quality_gate(coco_data, arguments.policy, image_bytes)
    write_quality_report(report, arguments.output)

    volume_md = (
        arguments.volume_report
        if arguments.volume_report
        else arguments.output.parent / "volume.md"
    )
    write_volume_markdown(report, volume_md)

    print(format_gate_report(report))
    return 1 if has_failures(report) else 0


if __name__ == "__main__":
    raise SystemExit(main())
