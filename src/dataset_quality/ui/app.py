import json
import os
from pathlib import Path

import streamlit as st

from dataset_quality.ui.analyzers import load_coco
from dataset_quality.ui.analyzers_view import render_analyzers
from dataset_quality.ui.overview import get_overview_metrics
from dataset_quality.ui.settings_view import render_settings

st.set_page_config(page_title="Dataset Quality", layout="wide")

st.title(" Dataset Overview")
st.markdown("Resumen de las métricas de calidad y estado de la compuerta.")


data = get_overview_metrics("mocks/quality_mock.json")
metrics = data.get("metrics", {})
gate_status = data.get("gate_status", "unknown").lower()

if gate_status == "pass":
    st.success(f"**Estado de la compuerta:** {gate_status.upper()} ")
elif gate_status == "warn":
    st.warning(f"**Estado de la compuerta:** {gate_status.upper()} ")
else:
    st.error(f"**Estado de la compuerta:** {gate_status.upper()} ")


st.subheader("Métricas principales")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Imágenes", metrics.get("total_images", 0))
with col2:
    st.metric("Total Cajas", metrics.get("total_boxes", 0))
with col3:
    st.metric("Categorías", metrics.get("categories", 0))
with col4:
    st.metric("Checks Fallidos", metrics.get("failed_checks", 0))

st.divider()
st.title("Analyzers")
st.markdown("Resultados calculados por F3-01…05 sobre el COCO seleccionado.")

uploaded_coco = st.file_uploader("COCO validado", type="json")
uploaded_images = st.file_uploader(
    "Imágenes para pHash (opcional)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
)

if uploaded_coco is not None:
    coco_data = json.load(uploaded_coco)
else:
    default_coco = Path("data/validated/coco.json")
    fallback_coco = Path("tests/fixtures/mp1-coco.json")
    source = default_coco if default_coco.exists() else fallback_coco
    coco_data = load_coco(source)
    st.caption(f"Fuente COCO: {source}")

image_bytes = {image.name: image.getvalue() for image in uploaded_images}
render_analyzers(coco_data, image_bytes)

render_settings(Path(os.getenv("QUALITY_POLICY_PATH", "quality.yaml")))
