from collections import Counter
from typing import Any


def analyze_small_objects(
    coco_data: dict[str, Any], threshold_w: int = 32, threshold_h: int = 32
) -> dict[str, Any]:
    """
    Analiza un diccionario COCO para detectar objetos pequeños.
    Cumple con SPEC-F3-01: Función pura, umbral configurable, reporta ofensores.
    """
    annotations = coco_data.get("annotations", [])
    categories = {cat["id"]: cat["name"] for cat in coco_data.get("categories", [])}

    total_boxes = 0
    small_boxes = 0
    offender_images = set()
    class_counts = Counter()

    for ann in annotations:
        bbox = ann.get("bbox", [])
        if len(bbox) < 4:
            continue

        total_boxes += 1
        w, h = bbox[2], bbox[3]

        if w < threshold_w or h < threshold_h:
            small_boxes += 1
            img_id = ann.get("image_id")
            if img_id is not None:
                offender_images.add(img_id)

            cat_name = categories.get(ann.get("category_id"), "unknown")
            class_counts[cat_name] += 1  # Refactor: Sintaxis mucho más limpia

    percentage = (small_boxes / total_boxes * 100.0) if total_boxes > 0 else 0.0

    return {
        "percentage": percentage,
        "most_affected_class": max(class_counts, key=class_counts.get) if class_counts else None,
        "offender_images": list(offender_images),
    }
