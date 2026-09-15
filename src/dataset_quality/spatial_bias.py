import statistics
from typing import Any


def analyze_spatial_bias(coco_data: dict[str, Any]) -> dict[str, Any]:
    """
    Calcula estadísticas descriptivas (media, mediana, percentiles)
    y detecta sesgos espaciales dividiendo la imagen en cuadrantes.
    Cumple con SPEC-F3-05.
    """
    annotations = coco_data.get("annotations", [])
    images = {img["id"]: img for img in coco_data.get("images", [])}

    areas = []
    quadrant_counts = {"TL": 0, "TR": 0, "BL": 0, "BR": 0}

    for ann in annotations:
        area = ann.get("area")
        if area is not None:
            areas.append(area)

        bbox = ann.get("bbox")
        img_id = ann.get("image_id")

        if bbox and len(bbox) >= 4 and img_id in images:
            x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]

            cx = x + (w / 2.0)
            cy = y + (h / 2.0)

            img_w = images[img_id].get("width", 0)
            img_h = images[img_id].get("height", 0)

            if img_w > 0 and img_h > 0:
                mid_w = img_w / 2.0
                mid_h = img_h / 2.0

                if cy < mid_h:
                    if cx < mid_w:
                        quadrant_counts["TL"] += 1
                    else:
                        quadrant_counts["TR"] += 1
                else:
                    if cx < mid_w:
                        quadrant_counts["BL"] += 1
                    else:
                        quadrant_counts["BR"] += 1

    result = {
        "mean_area": 0.0,
        "median_area": 0.0,
        "p25_area": 0.0,
        "p75_area": 0.0,
        "quadrant_counts": quadrant_counts,
    }

    if areas:
        result["mean_area"] = statistics.mean(areas)
        result["median_area"] = statistics.median(areas)

        if len(areas) >= 2:
            quarts = statistics.quantiles(areas, n=4, method="inclusive")
            result["p25_area"] = float(quarts[0])
            result["p75_area"] = float(quarts[2])
        elif len(areas) == 1:
            result["p25_area"] = float(areas[0])
            result["p75_area"] = float(areas[0])

    return result
