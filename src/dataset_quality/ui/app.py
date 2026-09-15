import streamlit as st
from dataset_quality.ui.overview import get_overview_metrics


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