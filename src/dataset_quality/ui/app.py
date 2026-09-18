import json
import os
from pathlib import Path

import streamlit as st

from dataset_quality.ui.analyzers import load_coco
from dataset_quality.ui.analyzers_view import render_analyzers
from dataset_quality.ui.overview import get_overview_metrics
from dataset_quality.ui.settings_view import render_settings
from dataset_quality.ui.splits_view import render_splits
from dataset_quality.ui.versions_view import render_versions

st.set_page_config(page_title="Dataset Quality", layout="wide")

st.title(" Dataset Overview")
st.markdown("Resumen de las métricas de calidad y estado de la compuerta.")


overview_path = os.getenv("OVERVIEW_QUALITY_REPORT_PATH", "mocks/quality_mock.json")
default_quality_path = Path("data/reports/quality.json")
if not os.getenv("OVERVIEW_QUALITY_REPORT_PATH") and default_quality_path.exists():
    overview_path = str(default_quality_path)

data = get_overview_metrics(overview_path)
metrics = data.get("metrics", {})

# Si se pasó calidad real con formato dict de checks de F4-03
has_check_dicts = any(isinstance(v, dict) and "status" in v for v in data.values())
if not metrics and isinstance(data, dict) and has_check_dicts:
    failed = sum(1 for v in data.values() if isinstance(v, dict) and v.get("status") == "fail")
    gate_status = "fail" if failed > 0 else "pass"
else:
    gate_status = data.get("gate_status", "unknown").lower()


gate_status = os.getenv("OVERVIEW_GATE_STATUS", gate_status).lower()


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

render_splits(
    coco_data=coco_data,
    gate_status=os.getenv("OVERVIEW_GATE_STATUS", gate_status),
    splits_path=os.getenv("SPLITS_REPORT_PATH"),
)

render_settings(Path(os.getenv("QUALITY_POLICY_PATH", "quality.yaml")))

render_versions()
