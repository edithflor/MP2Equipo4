from collections import defaultdict
from typing import Any


def _canonical_image_ids(image_audit: dict, coco_data: dict | None = None) -> dict[str, str]:
    """Map every image ID to the first ID in its duplicate component."""
    hashed_ids = image_audit.get("hashed_image_ids")
    if hashed_ids:
        ids = {str(image_id) for image_id in hashed_ids}
    elif coco_data is not None:
        ids = {str(image.get("id")) for image in coco_data.get("images", [])}
    else:
        ids = set()
        for pair in image_audit.get("pairs", []):
            ids.add(str(pair["image1"]))
            ids.add(str(pair["image2"]))

    parent = {image_id: image_id for image_id in ids}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for pair in image_audit.get("pairs", []):
        left = str(pair["image1"])
        right = str(pair["image2"])
        if left in parent and right in parent:
            union(left, right)

    return {image_id: find(image_id) for image_id in parent}


def audit_volume(coco_data: dict, image_audit: dict, threshold: int = 300) -> dict[str, Any]:
    categories = {category["id"]: category["name"] for category in coco_data.get("categories", [])}
    canonical = _canonical_image_ids(image_audit, coco_data)
    class_images = {name: set() for name in categories.values()}
    invalid_boxes = []

    for annotation in coco_data.get("annotations", []):
        bbox = annotation.get("bbox", [])
        if len(bbox) < 4 or bbox[2] <= 0 or bbox[3] <= 0:
            invalid_boxes.append(annotation)
            continue
        image_id = str(annotation.get("image_id"))
        category_name = categories.get(annotation.get("category_id"))
        if category_name is None or image_id not in canonical:
            continue
        class_images[category_name].add(canonical[image_id])

    classes = [
        {
            "class": class_name,
            "before_phash": len(
                {
                    str(annotation["image_id"])
                    for annotation in coco_data.get("annotations", [])
                    if categories.get(annotation.get("category_id")) == class_name
                }
            ),
            "after_phash": len(image_ids),
            "missing_to_threshold": max(0, threshold - len(image_ids)),
        }
        for class_name, image_ids in sorted(class_images.items())
    ]

    return {
        "classes": classes,
        "invalid_boxes": invalid_boxes,
    }


def count_images_per_class(coco_data: dict) -> dict[str, int]:
    """
    Cuenta imágenes distintas por clase, ignorando cajas degeneradas (width o height <= 0).
    """
    cat_map = {cat["id"]: cat["name"] for cat in coco_data.get("categories", [])}

    counts = defaultdict(set)
    for ann in coco_data.get("annotations", []):
        bbox = ann.get("bbox", [0, 0, 0, 0])

        if len(bbox) >= 4:
            width, height = bbox[2], bbox[3]
            if width <= 0 or height <= 0:
                continue

        cat_id = ann.get("category_id")
        cat_name = cat_map.get(cat_id)
        img_id = ann.get("image_id")

        if cat_name and img_id is not None:
            counts[cat_name].add(img_id)

    return {name: len(image_set) for name, image_set in counts.items()}


def format_volume_table(counts: dict[str, int]) -> str:
    """Formatea el diccionario como tabla de texto: clase -> n."""
    lines = [f"{'clase':<12} | {'imágenes':<8}", f"{'-' * 12}-+-{'-' * 8}"]
    for cls_name, total in sorted(counts.items()):
        lines.append(f"{cls_name:<12} | {total:<8}")
    return "\n".join(lines)


def print_volume_report(coco_data: dict) -> None:
    """Imprime directamente en consola el reporte de conteo por clase."""
    counts = count_images_per_class(coco_data)
    print(format_volume_table(counts))
