from typing import Any


def analyze_class_imbalance(coco_data: dict[str, Any], min_images: int = 300) -> dict[str, Any]:
    """
    Calcula el desbalance contando imágenes únicas por categoría.
    Cumple con SPEC-F3-02.
    """
    categories = {cat["id"]: cat["name"] for cat in coco_data.get("categories", [])}
    annotations = coco_data.get("annotations", [])

    class_image_sets = {}
    for ann in annotations:
        cat_id = ann.get("category_id")
        img_id = ann.get("image_id")

        if cat_id is not None and img_id is not None:
            cat_name = categories.get(cat_id, "unknown")
            if cat_name not in class_image_sets:
                class_image_sets[cat_name] = set()
            class_image_sets[cat_name].add(img_id)

    class_counts = {name: len(img_set) for name, img_set in class_image_sets.items()}

    for cat_name in categories.values():
        if cat_name not in class_counts:
            class_counts[cat_name] = 0

    classes_under_minimum = [name for name, count in class_counts.items() if count < min_images]

    ratio = 0.0
    if class_counts:
        max_count = max(class_counts.values())
        min_count = min(class_counts.values())

        if min_count > 0:
            ratio = float(max_count) / min_count
        elif max_count > 0:
            ratio = float("inf")

    return {
        "ratio": ratio,
        "classes_under_minimum": classes_under_minimum,
        "class_counts": class_counts,
    }
