from dataset_quality.mcp.server import (
    get_dataset_versions,
    get_quality_report,
    get_version_diff,
)


def _current_version(versions_payload: dict) -> str:
    versions = versions_payload.get("versions", [])
    if not versions:
        return "unknown"
    return str(versions[-1].get("version", "unknown"))


def answer_dataset_question(
    question: str,
    quality_path: str = "data/reports/quality.json",
    versions_path: str = "metadata/versions.json",
    diff_path: str = "metadata/diff-v0.1.0-v1.0.0.json",
) -> dict:
    normalized = question.lower().strip()

    supported_keywords = {
        "release",
        "bloqueado",
        "bloqueada",
        "calidad",
        "quality",
        "dataset",
        "version",
        "versión",
        "imagenes",
        "imágenes",
        "clase",
        "clases",
        "duplicados",
        "boxes",
        "cajas",
        "small",
        "objetos",
        "diff",
    }

    if not any(keyword in normalized for keyword in supported_keywords):
        return {
            "answer": (
                "No puedo responder esa pregunta con las fuentes disponibles "
                "del dataset sin inventar información."
            ),
            "dataset_version": "unknown",
            "tools_used": [],
        }

    quality = get_quality_report(quality_path)
    versions = get_dataset_versions(versions_path)
    diff = get_version_diff(diff_path)

    version = _current_version(versions)

    minimum = quality.get("min_images_per_class", {})
    status = minimum.get("status", "unknown")
    observed = minimum.get("observed")
    threshold = minimum.get("threshold")

    if status == "fail":
        release_text = (
            f"El release está bloqueado por min_images_per_class: "
            f"observado={observed}, umbral={threshold}."
        )
    elif status == "pass":
        release_text = (
            f"El release no está bloqueado por min_images_per_class: "
            f"observado={observed}, umbral={threshold}."
        )
    else:
        release_text = (
            "No se puede determinar el estado del release con la métrica "
            "min_images_per_class disponible."
        )

    return {
        "answer": release_text,
        "dataset_version": version,
        "tools_used": [
            "get_quality_report",
            "get_dataset_versions",
            "get_version_diff",
        ],
        "trace": {
            "quality_status": status,
            "diff_from": diff.get("from"),
            "diff_to": diff.get("to"),
        },
    }
