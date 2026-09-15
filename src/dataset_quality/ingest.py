"""Ingesta del COCO validado para el pipeline de calidad."""

import sys
from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from dataset_quality.coco import CocoDataset


class IngestSettings(BaseSettings):
    """Configuración de ingesta obtenida desde variables de entorno."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    coco_input_path: Path = Path("data/raw/annotations_coco.json")
    coco_validated_path: Path = Path("data/validated/coco.json")
    minio_bucket: str = "dataset-dev"


def ingest_coco(input_path: Path, output_path: Path) -> Path:
    """Valida un COCO y genera el artefacto consumido por los analizadores."""

    raw_coco = input_path.read_bytes()
    dataset = CocoDataset.model_validate_json(raw_coco)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    temporary_path.write_text(
        dataset.model_dump_json(indent=2),
        encoding="utf-8",
    )
    temporary_path.replace(output_path)

    return output_path


def main() -> int:
    """Ejecuta la ingesta y devuelve un código de salida."""

    settings = IngestSettings()

    try:
        artifact = ingest_coco(
            settings.coco_input_path,
            settings.coco_validated_path,
        )
    except (OSError, ValidationError) as error:
        print(error, file=sys.stderr)
        return 1

    print(f"COCO validado: {artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
