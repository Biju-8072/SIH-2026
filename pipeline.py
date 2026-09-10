"""
🚀 SIH26162: Master Industrial Fire Surveillance Pipeline Orchestrator
Executes all 5 detection and classification stages in clean, synchronized sequence:
  Stage 1: Satellite Data Acquisition (NASA FIRMS / Calibrated Indian Hotspots)
  Stage 2: Industrial Zoning Infrastructure Mapping (OSM / Facility Registry)
  Stage 3: Haversine Proximity Cross-Referencing & Buffer Intersections
  Stage 4: Temporal & Radiative Power AI Classification
  Stage 5: Multi-Channel Emergency Siren Alerting
"""

import sys
import time
import warnings
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

from fetch_firms import fetch_firms_data
from fetch_osm import fetch_osm_zones
from cross_reference import cross_reference_hotspots
from temporal_tracker import run_temporal_classification
from dispatch_alerts import dispatch_emergency_alerts


def run_full_pipeline(
    force_sandbox: bool = False,
    reuse_existing: bool = False,
    dispatch_alerts: bool = True,
    progress_callback = None
) -> pd.DataFrame:
    """
    Executes the complete SIH26162 surveillance and detection pipeline.
    Optionally accepts a progress_callback(percentage, message) for Streamlit UI integration.
    """
    start_time = time.time()
    print("\n" + "=" * 65)
    print("🛰️ SIH26162: INITIATING INDUSTRIAL FIRE DETECTION PIPELINE")
    print("=" * 65)

    def report_step(pct: int, msg: str):
        print(f"[{pct:3d}%] {msg}")
        if progress_callback:
            progress_callback(pct, msg)

    # -------------------------------------------------------------
    # Stage 1: Ingest Hotspots
    # -------------------------------------------------------------
    report_step(15, "Stage 1/5: Ingesting satellite thermal anomalies (FRP)...")
    hotspots_df = fetch_firms_data(
        output_file="live_hotspots.csv",
        force_sandbox=force_sandbox,
        reuse_existing=reuse_existing
    )

    # -------------------------------------------------------------
    # Stage 2: Industrial Zoning & Asset Mapping
    # -------------------------------------------------------------
    report_step(35, "Stage 2/5: Mapping industrial zoning infrastructure...")
    zones = fetch_osm_zones(output_file="industrial_zones.json")

    # -------------------------------------------------------------
    # Stage 3: Spatial Proximity & Collision Calculation
    # -------------------------------------------------------------
    report_step(60, "Stage 3/5: Cross-referencing coordinates with Haversine buffer...")
    cross_ref_df = cross_reference_hotspots(
        hotspots_path="live_hotspots.csv",
        zones_path="industrial_zones.json"
    )
    cross_ref_df.to_csv("cross_referenced_hotspots.csv", index=False)

    # -------------------------------------------------------------
    # Stage 4: Temporal Persistence & Thermal AI Classification
    # -------------------------------------------------------------
    report_step(85, "Stage 4/5: Running temporal classification (Flare vs Disaster vs Wildfire)...")
    validated_df = run_temporal_classification(
        cross_referenced_df=cross_ref_df,
        output_validated_file="time_series_validated_alerts.csv",
        output_classified_file="classified_fire_alerts.csv"
    )

    # -------------------------------------------------------------
    # Stage 5: Emergency Siren Alert Dispatch
    # -------------------------------------------------------------
    report_step(95, "Stage 5/5: Evaluating emergency sirens & dispatch protocols...")
    if dispatch_alerts:
        dispatched_count = dispatch_emergency_alerts("time_series_validated_alerts.csv")
    else:
        dispatched_count = 0

    elapsed = time.time() - start_time
    report_step(100, f"✅ Complete! Processed {len(validated_df)} hotspots in {elapsed:.2f}s.")
    print("=" * 65 + "\n")
    return validated_df


if __name__ == "__main__":
    force_sandbox = "--sandbox" in sys.argv
    reuse_existing = "--reuse" in sys.argv
    no_alert = "--no-alert" in sys.argv
    df = run_full_pipeline(
        force_sandbox=force_sandbox,
        reuse_existing=reuse_existing,
        dispatch_alerts=not no_alert
    )
    print("Classification Summary:")
    print(df["classification"].value_counts().to_string())
