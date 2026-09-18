import json
from pathlib import Path

import pandas as pd
import streamlit as st


@st.fragment
def render_embeddings(embeddings_path: str | Path):
    path = Path(embeddings_path)
    if not path.exists():
        st.warning(f"No se encontró el artefacto precomputado de embeddings en {path}")
        return

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        st.info("El artefacto de embeddings está vacío.")
        return

    df = pd.DataFrame(data)

    st.subheader("Exploración Dimensional (Precomputada)")

    # Filtro por clase
    if "category" in df.columns:
        categories = sorted(df["category"].unique())
        selected_cats = st.multiselect("Filtrar por clase", categories, default=categories)
        df_filtered = df[df["category"].isin(selected_cats)]
    else:
        df_filtered = df

    if df_filtered.empty:
        st.info("No hay datos para mostrar con los filtros actuales.")
        return

    import altair as alt

    selector = alt.selection_point(name="selector")
    chart = (
        alt.Chart(df_filtered)
        .mark_circle(size=60)
        .encode(
            x="x",
            y="y",
            color=alt.condition(
                selector,
                "category" if "category" in df_filtered.columns else alt.value("blue"),
                alt.value("lightgray"),
            ),
            tooltip=["file_name", "category"],
        )
        .add_params(selector)
        .interactive()
    )

    event = st.altair_chart(chart, on_select="rerun", selection_mode="selector")

    if event and "selection" in event and event.selection:
        # Altair selection events format varies slightly but selection['point'] contains selected
        pass
        # Simplificaremos el evento para no fallar
