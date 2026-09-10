"""
🛰️ SIH26162: AI-Based Detection & Classification of Industrial Fires
Tactical Command Center Streamlit Wrapper
Renders the pixel-perfect Analytical Tools & Real-Time Resource Allocation GUI
"""

import os
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from pipeline import run_full_pipeline
from inject_incident import inject_disaster_scenario
from ui_template import generate_dashboard_html

# Page Config
st.set_page_config(
    page_title="DT | Analytical tools & Crisis Command Center",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide Streamlit margins and header so the dashboard fills the entire viewport
st.markdown("""
<style>
header[data-testid="stHeader"] {
    display: none !important;
}
div.block-container {
    padding: 0rem !important;
    max-width: 100% !important;
}
footer {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALERTS_CSV = os.path.join(BASE_DIR, "time_series_validated_alerts.csv")
ZONES_JSON = os.path.join(BASE_DIR, "industrial_zones.json")


def get_telemetry_records():
    """Loads live alerts, bootstrapping pipeline if data missing."""
    if not os.path.exists(ALERTS_CSV):
        run_full_pipeline(force_sandbox=True, dispatch_alerts=False)

    try:
        df = pd.read_csv(ALERTS_CSV)
        df["latitude"] = pd.to_numeric(df.get("latitude", df.get("Lat")), errors="coerce")
        df["longitude"] = pd.to_numeric(df.get("longitude", df.get("Lon")), errors="coerce")
        df["frp"] = pd.to_numeric(df.get("frp", df.get("Radiative Power (FRP)", 0)), errors="coerce")
        df["classification"] = df.get("classification", "UNKNOWN").astype(str)
        df["facility_name"] = df.get("facility_name", "Industrial Complex").astype(str)
        df["analysis"] = df.get("analysis", "").astype(str)
        df["recommended_action"] = df.get("recommended_action", "").astype(str)
        clean = df.dropna(subset=["latitude", "longitude"])
        return clean.to_dict(orient="records")
    except Exception:
        return []


def get_zones_records():
    if os.path.exists(ZONES_JSON):
        try:
            with open(ZONES_JSON, "r") as f:
                data = json.load(f)
                return data.get("elements", [])
        except Exception:
            return []
    return []


alerts = get_telemetry_records()
zones = get_zones_records()

# Generate the full HTML5/CSS3/JS application
dashboard_html = generate_dashboard_html(alerts, zones)

# Also save standalone index.html so user can double-click it in any browser!
with open(os.path.join(BASE_DIR, "index.html"), "w") as f:
    f.write(dashboard_html)

# Render inside Streamlit with zero markdown syntax corruption
components.html(dashboard_html, height=980, scrolling=True)
