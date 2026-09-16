from collections import defaultdict
from typing import Any


def generate_stratified_splits(
    coco_data: dict[str, Any],
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> dict[str, list[int]]:
    """
    Genera particiones estratificadas asegurando proporciones por clase
    y garantizando presencia en val/test.
    Cumple con SPEC-F5-01.
    """
    annotations = coco_data.get("annotations", [])
    images = coco_data.get("images", [])

    img_to_cat = {}
    for ann in annotations:
        img_id = ann.get("image_id")
        cat_id = ann.get("category_id")

        if img_id is not None and cat_id is not None and img_id not in img_to_cat:
            img_to_cat[img_id] = cat_id

    cat_to_imgs = defaultdict(list)
    for img_id, cat_id in img_to_cat.items():
        cat_to_imgs[cat_id].append(img_id)

    splits = {"train": [], "val": [], "test": []}

    for imgs in cat_to_imgs.values():
        imgs.sort()
        n_total = len(imgs)
        n_val = (
            max(1, int(round(n_total * val_ratio))) if n_total >= 3 else (1 if n_total == 2 else 0)
        )
        n_test = max(1, int(round(n_total * test_ratio))) if n_total >= 3 else 0
        n_train = max(0, n_total - n_val - n_test)

        if n_train == 0 and n_total >= 2:
            n_val = n_total // 2
            n_test = n_total - n_val

        splits["train"].extend(imgs[:n_train])
        splits["val"].extend(imgs[n_train : n_train + n_val])
        splits["test"].extend(imgs[n_train + n_val :])
    annotated_imgs = set(img_to_cat.keys())
    all_imgs = {img["id"] for img in images if "id" in img}
    splits["train"].extend(sorted(list(all_imgs - annotated_imgs)))

    return splits
