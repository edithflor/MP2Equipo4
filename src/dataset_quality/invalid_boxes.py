from typing import Any


def analyze_invalid_boxes(coco_data: dict[str, Any]) -> dict[str, Any]:

    images = {img["id"]: img for img in coco_data.get("images", [])}
    annotations = coco_data.get("annotations", [])

    invalid_annotations = []

    for ann in annotations:
        bbox = ann.get("bbox")
        if not bbox or len(bbox) < 4:
            continue

        x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
        area = ann.get("area", 0)
        img_id = ann.get("image_id")

        is_invalid = False
        reasons = []

        if w <= 0 or h <= 0:
            is_invalid = True
            reasons.append("negative_or_zero_dimensions")

        if img_id in images:
            img_w = images[img_id].get("width", float("inf"))
            img_h = images[img_id].get("height", float("inf"))

            if x < 0 or y < 0 or (x + w) > img_w or (y + h) > img_h:
                is_invalid = True
                reasons.append("out_of_bounds")

        if abs((w * h) - area) > 1.0:
            is_invalid = True
            reasons.append("incoherent_area")

        if is_invalid:
            invalid_ann = ann.copy()
            invalid_ann["invalid_reasons"] = reasons
            invalid_annotations.append(invalid_ann)

    return {"invalid_annotations": invalid_annotations}
