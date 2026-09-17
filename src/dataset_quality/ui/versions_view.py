import json
from pathlib import Path

import streamlit as st


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def render_versions() -> None:
    st.divider()
    st.title("Versions")
    st.markdown("Historial de versiones y comparación del dataset.")

    versions_path = Path("metadata/versions.json")
    diff_path = Path("metadata/diff-v0.1.0-v1.0.0.json")

    versions_data = load_json(versions_path)
    diff_data = load_json(diff_path)

    versions = versions_data.get("versions", [])

    if not versions:
        st.warning("No hay versiones registradas.")
        return

    st.subheader("Timeline")

    for version in versions:
        version_name = version.get("version", "unknown")
        environment = version.get("environment", "unknown")

        with st.container(border=True):
            st.write(f"### {version_name}")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**DEV:** {environment}")

            with col2:
                if environment == "PROD":
                    st.write("**PROD:** disponible")
                else:
                    st.write("**PROD:** no promocionado")

    if diff_data:
        st.subheader("Diff entre versiones")

        st.write(f"Comparación: **{diff_data.get('from')} → {diff_data.get('to')}**")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Imágenes añadidas",
                diff_data.get("images_added", 0),
            )

        with col2:
            st.metric(
                "Cajas añadidas",
                diff_data.get("boxes_added", 0),
            )

        with col3:
            st.metric(
                "Cambio objetos pequeños",
                f"{diff_data.get('small_objects_percentage_change', 0):.3f} pp",
            )

        before = diff_data.get("classes_below_minimum_before", [])
        after = diff_data.get("classes_below_minimum_after", [])

        st.write(
            "**Clases bajo mínimo antes:**",
            ", ".join(before) if before else "Ninguna",
        )

        st.write(
            "**Clases bajo mínimo después:**",
            ", ".join(after) if after else "Ninguna",
        )
