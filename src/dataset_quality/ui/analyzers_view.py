from __future__ import annotations

from typing import Any

import streamlit as st

from dataset_quality.ui.analyzers import TAB_SPECS, build_analyzer_report


def _offender_table(rows: list[dict[str, Any]], empty_message: str) -> None:
    st.markdown("#### Muestras ofensoras")
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.success(empty_message)


def render_analyzers(coco_data: dict[str, Any], image_bytes: dict[str, bytes]) -> None:
    report = build_analyzer_report(coco_data, image_bytes)
    tabs = st.tabs([label for _, label in TAB_SPECS])

    with tabs[0]:
        section = report["small_objects"]
        st.metric("Objetos pequeños", f"{section['metrics']['percentage']:.2f}%")
        st.caption(f"Clase más afectada: {section['metrics']['most_affected_class'] or 'ninguna'}")
        st.bar_chart(section["chart"])
        _offender_table(section["offenders"], "No se detectaron objetos pequeños.")

    with tabs[1]:
        section = report["class_imbalance"]
        ratio = section["metrics"]["ratio"]
        st.metric("Razón máximo/mínimo", "∞" if ratio == float("inf") else f"{ratio:.2f}")
        st.bar_chart(section["chart"])
        _offender_table(section["offenders"], "Todas las clases cumplen el mínimo.")

    with tabs[2]:
        section = report["duplicates"]
        st.metric("Pares near-duplicate", section["metrics"]["pair_count"])
        st.caption("Carga las imágenes del COCO para calcular pHash; no se usan series de ejemplo.")
        st.bar_chart(section["chart"])
        _offender_table(section["offenders"], "No se detectaron pares duplicados.")

    with tabs[3]:
        section = report["invalid_boxes"]
        st.metric("Cajas inválidas", section["metrics"]["invalid_count"])
        st.bar_chart(section["chart"])
        _offender_table(section["offenders"], "No se detectaron cajas inválidas.")

    with tabs[4]:
        section = report["spatial_bias"]
        metric_columns = st.columns(4)
        for column, (label, value) in zip(metric_columns, section["metrics"].items(), strict=True):
            column.metric(label.replace("_", " ").title(), f"{value:.2f}")
        st.bar_chart(section["chart"])
        _offender_table(
            section["offenders"], "No existen anotaciones para obtener muestras espaciales."
        )
