def count_images_per_class(coco_data: dict) -> dict[str, int]:
    """
    Cuenta imágenes distintas por clase, ignorando cajas degeneradas (width o height <= 0).
    """
    cat_map = {cat["id"]: cat["name"] for cat in coco_data.get("categories", [])}

    counts = {}
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
            if cat_name not in counts:
                counts[cat_name] = set()
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
