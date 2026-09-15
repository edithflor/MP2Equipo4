from typing import Any


def _get_invalid_reasons(ann: dict[str, Any], img: dict[str, Any] | None) -> list[str]:
    """Evalúa una anotación y devuelve una lista de razones si es inválida."""
    reasons = []
    bbox = ann.get("bbox", [])

    if not bbox or len(bbox) < 4:
        return ["malformed_bbox"]

    x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
    area = ann.get("area", 0)

    if w <= 0 or h <= 0:
        reasons.append("negative_or_zero_dimensions")

    if img:
        img_w = img.get("width", float("inf"))
        img_h = img.get("height", float("inf"))
        if x < 0 or y < 0 or (x + w) > img_w or (y + h) > img_h:
            reasons.append("out_of_bounds")

    if abs((w * h) - area) > 1.0:
        reasons.append("incoherent_area")

    return reasons


def analyze_invalid_boxes(coco_data: dict[str, Any]) -> dict[str, Any]:

    images = {img["id"]: img for img in coco_data.get("images", [])}
    invalid_annotations = []

    for ann in coco_data.get("annotations", []):
        img = images.get(ann.get("image_id"))
        reasons = _get_invalid_reasons(ann, img)

        if reasons:
            invalid_ann = ann.copy()
            invalid_ann["invalid_reasons"] = reasons
            invalid_annotations.append(invalid_ann)

    return {"invalid_annotations": invalid_annotations}
