"""Vista de Streamlit para inspeccionar las particiones (Splits) y fugas (Leakage)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import streamlit as st


def compute_class_distribution_by_split(
    coco_data: dict[str, Any], splits: dict[str, list[int]]
) -> list[dict[str, Any]]:
    """Calcula la distribución exacta de imágenes por clase en cada partición (F5-01 / F5-04)."""
    categories = {cat["id"]: cat["name"] for cat in coco_data.get("categories", [])}
    annotations = coco_data.get("annotations", [])

    img_to_cats: dict[int, set[int]] = defaultdict(set)
    for ann in annotations:
        img_id = ann.get("image_id")
        cat_id = ann.get("category_id")
        if img_id is not None and cat_id is not None:
            img_to_cats[img_id].add(cat_id)

    train_ids = set(splits.get("train", []))
    val_ids = set(splits.get("val", []))
    test_ids = set(splits.get("test", []))

    distribution: list[dict[str, Any]] = []
    for cat_id, cat_name in sorted(categories.items(), key=lambda x: x[0]):
        train_count = sum(1 for img_id in train_ids if cat_id in img_to_cats[img_id])
        val_count = sum(1 for img_id in val_ids if cat_id in img_to_cats[img_id])
        test_count = sum(1 for img_id in test_ids if cat_id in img_to_cats[img_id])
        total = train_count + val_count + test_count
        distribution.append(
            {
                "category_id": cat_id,
                "category": cat_name,
                "train": train_count,
                "val": val_count,
                "test": test_count,
                "total": total,
            }
        )
    return distribution


def load_split_contract_or_json(
    splits_path: str | Path | None = None,
) -> dict[str, Any] | None:
    """Carga splits.json si existe en disco."""
    if splits_path is None:
        default_path = Path("data/reports/splits.json")
        if default_path.exists():
            splits_path = default_path
        else:
            fallback = Path("examples/splits.json")
            if fallback.exists():
                splits_path = fallback
            else:
                return None

    path = Path(splits_path)
    if not path.exists():
        return None

    return json.loads(path.read_text(encoding="utf-8"))


def render_splits(
    coco_data: dict[str, Any] | None = None,
    split_contract: dict[str, Any] | None = None,
    gate_status: str = "pass",
    splits_path: str | Path | None = None,
) -> None:
    """
    Renderiza la vista de Splits respetando SPEC-APP-03.
    Sin drivers de MariaDB, MinIO ni S3.
    """
    st.divider()
    st.title("Splits")
    st.markdown("Distribución estratificada por clase y verificación de fugas (data leakage).")

    # Criterio de Aceptación: Si el gate está en fail, bloquea la vista
    if str(gate_status).lower() == "fail":
        st.error("no hay split / bloqueado: La compuerta de calidad falló.")
        return

    # Si no se pasó un contrato explícito, intentar cargarlo de archivo
    contract = split_contract or load_split_contract_or_json(splits_path)

    if not contract:
        st.warning("No se encontró contrato ni archivo de particiones (splits.json).")
        return

    # Extraer splits y validación de leakage
    splits = contract.get("splits")
    if not splits:
        # Formato de ejemplo {"train": 450, "val": 100, "test": 50, "leakage_detected": false}
        train_val = contract.get("train", 0)
        val_val = contract.get("val", 0)
        test_val = contract.get("test", 0)
        train_count = len(train_val) if isinstance(train_val, list) else int(train_val)
        val_count = len(val_val) if isinstance(val_val, list) else int(val_val)
        test_count = len(test_val) if isinstance(test_val, list) else int(test_val)

        leakage_val = contract.get("leakage_validation", {})
        leaked_pairs = leakage_val.get("leaked_pairs", 0)
        leakage_detected = contract.get("leakage_detected", leaked_pairs > 0)

        st.subheader("Resumen de particiones")
        col1, col2, col3 = st.columns(3)
        col1.metric("Train", train_count)
        col2.metric("Val", val_count)
        col3.metric("Test", test_count)

        st.subheader("Verificación de fuga (Leakage)")
        if not leakage_detected:
            st.success("Cero fuga detectada entre particiones.")
        else:
            st.error(f"Fuga detectada: {leaked_pairs} pares cruzados.")
        return

    # Formato completo de contrato F5 (dict con "splits", "metadata", "leakage_validation")
    train_imgs = splits.get("train", [])
    val_imgs = splits.get("val", [])
    test_imgs = splits.get("test", [])

    st.subheader("Resumen general de tamaños")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Train", len(train_imgs))
    col2.metric("Total Val", len(val_imgs))
    col3.metric("Total Test", len(test_imgs))
    total_imgs = len(train_imgs) + len(val_imgs) + len(test_imgs)
    col4.metric("Total Procesadas", total_imgs)

    st.subheader("Distribución por clase")
    if coco_data:
        dist_table = compute_class_distribution_by_split(coco_data, splits)
        st.dataframe(dist_table, hide_index=True, width="stretch")
    else:
        st.info("Cargue un COCO para desglosar el conteo por categoría.")

    st.subheader("Verificación de fuga (Leakage F5-03)")
    leakage_info = contract.get("leakage_validation", {})
    leaked_pairs = leakage_info.get("leaked_pairs", 0)

    l_col1, l_col2, l_col3, l_col4 = st.columns(4)
    l_col1.metric("Pares cruzados (leaked pairs)", leaked_pairs)
    l_col2.metric("Train ∩ Val", leakage_info.get("intersection_train_val", 0))
    l_col3.metric("Train ∩ Test", leakage_info.get("intersection_train_test", 0))
    l_col4.metric("Val ∩ Test", leakage_info.get("intersection_val_test", 0))

    if leaked_pairs == 0:
        st.success(
            "El check de pares cruzados coincide con F5-03: 0 pares fugados. "
            "Pares pHash en el mismo split."
        )
    else:
        st.error(
            f"El check de pares cruzados detectó {leaked_pairs} pares de near-duplicates "
            "en splits diferentes."
        )

