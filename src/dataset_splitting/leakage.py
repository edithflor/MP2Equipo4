from typing import Any


def analyze_leakage(
    splits: dict[str, list[int]], all_images: list[int], phash_pairs: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Analiza las particiones para garantizar que son disjuntas
    y que no hay fuga de datos (near-duplicates en distintos splits).
    Cumple con SPEC-F5-03.
    """
    train_set = set(splits.get("train", []))
    val_set = set(splits.get("val", []))
    test_set = set(splits.get("test", []))

    all_images_set = set(all_images)
    union_set = train_set | val_set | test_set

    intersection_train_val = len(train_set & val_set)
    intersection_train_test = len(train_set & test_set)
    intersection_val_test = len(val_set & test_set)

    union_matches_dataset = union_set == all_images_set

    img_to_split = {}
    for img_id in train_set:
        img_to_split[img_id] = "train"
    for img_id in val_set:
        img_to_split[img_id] = "val"
    for img_id in test_set:
        img_to_split[img_id] = "test"

    leaked_pairs = 0
    for pair in phash_pairs:
        img1 = pair.get("image1")
        img2 = pair.get("image2")

        if (
            img1 in img_to_split
            and img2 in img_to_split
            and img_to_split[img1] != img_to_split[img2]
        ):
            leaked_pairs += 1

    return {
        "intersection_train_val": intersection_train_val,
        "intersection_train_test": intersection_train_test,
        "intersection_val_test": intersection_val_test,
        "union_matches_dataset": union_matches_dataset,
        "leaked_pairs": leaked_pairs,
    }
