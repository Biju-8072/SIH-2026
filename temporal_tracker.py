"""
⏳ SIH26162 - Stage 4: Temporal & AI Fire Classification Engine
Evaluates spatial location, historical persistence, and thermal radiative power (FRP)
to classify fires into:
  1. 🚨 CRITICAL DISASTER: Uncontrolled factory explosions / structural fires.
  2. 🏭 CONTROLLED FLARE: Routine operational refinery flare stacks.
  3. 🌲 VEGETATION / BRUSHFIRE: Wildfires or rural open burns.
"""

import json
import os
import pandas as pd

HISTORY_FILE = "historical_flare_registry.json"

# Known baseline facilities with historical flare activity over 30 days
DEFAULT_HISTORICAL_REGISTRY = {
    "IND-GJ-001": {"observations_30d": 28, "avg_frp": 95.0, "flare_certified": True},
    "IND-GJ-002": {"observations_30d": 24, "avg_frp": 42.0, "flare_certified": True},
    "IND-GJ-003": {"observations_30d": 29, "avg_frp": 110.0, "flare_certified": True},
    "IND-TN-001": {"observations_30d": 22, "avg_frp": 48.0, "flare_certified": True},
    "IND-MH-001": {"observations_30d": 25, "avg_frp": 50.0, "flare_certified": True},
    "IND-WB-001": {"observations_30d": 20, "avg_frp": 60.0, "flare_certified": True},
}


def load_historical_registry() -> dict:
    """Loads 30-day temporal baseline data for industrial facilities."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_HISTORICAL_REGISTRY


def classify_fire_event(row: dict, history: dict) -> dict:
    """
    Applies multi-stage temporal and radiative decision matrix:
      - Outside industrial buffer -> VEGETATION / BRUSHFIRE
      - Inside industrial buffer:
          * If facility has known flare certification AND FRP within baseline range -> CONTROLLED FLARE
          * If FRP significantly exceeds baseline OR facility lacks flare certification -> CRITICAL DISASTER
    """
    in_zone = row.get("in_industrial_zone", False)
    frp = float(row.get("frp", 0.0))
    fac_id = row.get("facility_id", "N/A")
    fac_name = row.get("facility_name", "Unknown Area")
    has_flares = row.get("has_flare_stacks", False)
    base_max = float(row.get("expected_baseline_max_mw", 100.0))

    # Case A: Fire is in rural/forest territory outside industrial boundaries
    if not in_zone:
        return {
            "classification": "VEGETATION / BRUSHFIRE",
            "risk_level": "MEDIUM RISK (Forestry Notification)",
            "analysis": f"Accidental wildland vegetation burn ({frp:.1f} MW) in open/rural corridor.",
            "recommended_action": "Notify State Forest Department & Local Fire Station.",
            "color_code": "#ffb62e",
            "is_emergency": False
        }

    # Case B: Fire is inside an industrial complex
    fac_history = history.get(fac_id, {})
    days_active = fac_history.get("observations_30d", 0)
    is_flare_certified = fac_history.get("flare_certified", False) or has_flares

    # Check for catastrophic surge: FRP > 1.5x expected baseline or > 250 MW
    is_extreme_heat = frp > (base_max * 1.5) or frp >= 250.0

    # If it's a known certified flare location operating within expected thermal bounds
    if is_flare_certified and not is_extreme_heat and days_active >= 10:
        return {
            "classification": "CONTROLLED FLARE",
            "risk_level": "LOW RISK (Routine Flare Monitored)",
            "analysis": f"Operational refinery flare stack at {fac_name} (Persistent {days_active}/30 days).",
            "recommended_action": "Autonomous telemetry logging. Normal industrial operation.",
            "color_code": "#00e5a0",
            "is_emergency": False
        }

    # Otherwise, it's an uncontained industrial disaster
    return {
        "classification": "CRITICAL DISASTER",
        "risk_level": "CRITICAL ACTION REQUIRED",
        "analysis": f"🚨 MASSIVE UNCONTAINED FIRE / EXPLOSION THREAT at {fac_name} (FRP: {frp:.1f} MW)!",
        "recommended_action": "TRIGGER ALPHA-RED SIREN! Dispatch Hazmat Teams & Fire Brigades!",
        "color_code": "#ff4161",
        "is_emergency": True
    }


def run_temporal_classification(
    cross_referenced_df: pd.DataFrame = None,
    input_file: str = "cross_referenced_hotspots.csv",
    output_validated_file: str = "time_series_validated_alerts.csv",
    output_classified_file: str = "classified_fire_alerts.csv"
) -> pd.DataFrame:
    """
    Executes the temporal classification pipeline and saves standardized alert logs.
    """
    if cross_referenced_df is None:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Missing '{input_file}'. Run Stage 3 first.")
        cross_referenced_df = pd.read_csv(input_file)

    history = load_historical_registry()
    print(f"⏳ Running temporal & AI classification on {len(cross_referenced_df)} hotspots...")

    classified_records = []

    for _, row in cross_referenced_df.iterrows():
        row_dict = row.to_dict()
        classification_result = classify_fire_event(row_dict, history)
        
        merged = {**row_dict, **classification_result}
        classified_records.append(merged)

    df_result = pd.DataFrame(classified_records)

    # Legacy schema compatibility columns for existing components
    df_result["Lat"] = df_result["latitude"]
    df_result["Lon"] = df_result["longitude"]
    df_result["Radiative Power (FRP)"] = df_result["frp"]
    df_result["System Analysis"] = df_result["analysis"]
    df_result["Risk Priority Tag"] = df_result["risk_level"]

    # Save to both standard file names to maintain 100% interoperability
    df_result.to_csv(output_validated_file, index=False)
    df_result.to_csv(output_classified_file, index=False)
    
    print(f"✅ Classification complete. Saved {len(df_result)} alerts to '{output_validated_file}'.")
    return df_result


if __name__ == "__main__":
    df = run_temporal_classification()
    print(df[["latitude", "longitude", "frp", "facility_name", "classification", "risk_level"]])
