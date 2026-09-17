from typing import Any

from dataset_splitting.leakage import analyze_leakage
from dataset_splitting.stratified import generate_stratified_splits


def create_split_contract(
    coco_data: dict[str, Any],
    config: dict[str, Any],
    phash_pairs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Orquesta la partición del dataset, valida las proporciones
    y genera un contrato de datos con metadatos y validación de fugas.
    Cumple con SPEC-F5-04.
    """
    train_ratio = config.get("train_ratio", 0.70)
    val_ratio = config.get("val_ratio", 0.15)
    test_ratio = config.get("test_ratio", 0.15)
    seed = config.get("seed", 42)

    total_ratio = train_ratio + val_ratio + test_ratio
    if abs(total_ratio - 1.0) > 1e-6:
        raise ValueError(f"Las proporciones deben sumar 1.0, pero suman {total_ratio}")

    splits = generate_stratified_splits(
        coco_data=coco_data,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        seed=seed,
    )

    all_images = [img["id"] for img in coco_data.get("images", []) if "id" in img]

    if phash_pairs is None:
        phash_pairs = []

    leakage_report = analyze_leakage(splits, all_images, phash_pairs)

    return {
        "metadata": {
            "train_ratio": train_ratio,
            "val_ratio": val_ratio,
            "test_ratio": test_ratio,
            "seed": seed,
            "total_images_processed": len(all_images),
        },
        "splits": splits,
        "leakage_validation": leakage_report,
    }
