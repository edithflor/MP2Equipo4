"""Settings de Streamlit para persistir la política quality.yaml local."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from dataset_quality.config import QualityPolicyConfig
from dataset_quality.quality_policy import load_quality_policy, save_quality_policy

RULE_LABELS = {
    "min_images_per_class": "Mínimo de imágenes por clase",
    "small_objects_percentage": "Máximo porcentaje de objetos pequeños",
    "class_imbalance_ratio": "Máxima razón de desbalance",
    "duplicate_pairs": "Máximo de pares duplicados",
    "invalid_boxes": "Máximo de cajas inválidas",
    "spatial_bias_percentage": "Máximo sesgo espacial (%)",
}


def render_settings(policy_path: str | Path) -> None:
    """Muestra y guarda umbrales en el YAML, sin abrir BD, S3 ni MinIO."""
    path = Path(policy_path)
    policy = load_quality_policy(path)

    st.divider()
    st.header("Settings")
    st.caption(f"Política persistida en: {path}")

    with st.form("quality-policy-settings"):
        updated_rules: dict[str, dict[str, float | str]] = {}
        for name, label in RULE_LABELS.items():
            rule = getattr(policy, name)
            columns = st.columns(2)
            updated_rules[name] = {
                "threshold": columns[0].number_input(
                    label,
                    min_value=0.0,
                    value=float(rule.threshold),
                    key=f"{name}-threshold",
                ),
                "severity": columns[1].selectbox(
                    f"Severidad: {label}",
                    options=["warn", "fail"],
                    index=0 if rule.severity == "warn" else 1,
                    key=f"{name}-severity",
                ),
            }

        save_clicked = st.form_submit_button("Guardar política")

    if save_clicked:
        updated_data = policy.model_dump(mode="json")
        updated_data.update(updated_rules)
        updated_policy = QualityPolicyConfig.model_validate(updated_data)
        save_quality_policy(updated_policy, path)
        st.success("Política guardada en quality.yaml. La siguiente corrida del gate la utilizará.")
