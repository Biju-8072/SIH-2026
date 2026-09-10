"""
💥 SIH26162 - Hackathon Emergency Scenario Simulator
Injects simulated critical disasters or resets telemetry to test the detection
and alerting pipeline in real-time during live demonstrations.
"""

import json
import os
import pandas as pd


def inject_disaster_scenario(scenario_type: str = "explosion") -> pd.DataFrame:
    """
    Injects a severe thermal anomaly into 'live_hotspots.csv' and updates facility registry.
    Scenarios:
      - 'explosion': Massive catastrophic chemical explosion at Hazira Chemical Belt (520 MW).
      - 'tank_fire': Storage tank rupture at Jamnagar (410 MW).
      - 'baseline': Safe baseline with operational flares and routine vegetation burns.
    """
    if scenario_type == "explosion":
        print("💥 Simulating: Severe Chemical Storage Explosion at Hazira Complex...")
        simulated = [
            {
                "latitude": 21.1660,
                "longitude": 72.6930,
                "acq_date": "2026-09-08",
                "acq_time": "1432",
                "frp": 520.8,  # Massive emergency spike!
                "confidence": "high",
                "satellite": "VIIRS-SNPP",
                "note": "SIMULATED HAZARDOUS CHEMICAL DETONATION"
            },
            {
                "latitude": 22.3072,
                "longitude": 73.1812,
                "acq_date": "2026-09-08",
                "acq_time": "1200",
                "frp": 95.0,
                "confidence": "nominal",
                "satellite": "VIIRS-SNPP",
                "note": "Routine Vadodara Flare Stack"
            },
            {
                "latitude": 24.5854,
                "longitude": 75.4800,
                "acq_date": "2026-09-08",
                "acq_time": "1315",
                "frp": 25.4,
                "confidence": "nominal",
                "satellite": "VIIRS-SNPP",
                "note": "Rajasthan Open Agricultural Burn"
            }
        ]
    elif scenario_type == "tank_fire":
        print("💥 Simulating: Massive Hydrocarbon Tank Fire at Jamnagar...")
        simulated = [
            {
                "latitude": 22.4720,
                "longitude": 70.0590,
                "acq_date": "2026-09-08",
                "acq_time": "1510",
                "frp": 415.6,
                "confidence": "high",
                "satellite": "VIIRS-SNPP",
                "note": "SIMULATED CRUDE OIL TANK FIRE"
            },
            {
                "latitude": 21.1645,
                "longitude": 72.6908,
                "acq_date": "2026-09-08",
                "acq_time": "1400",
                "frp": 42.0,
                "confidence": "nominal",
                "satellite": "VIIRS-SNPP",
                "note": "Routine Hazira Flare"
            }
        ]
    else:  # 'baseline'
        print("🔄 Resetting telemetry to normal baseline (all routine operations)...")
        from fetch_firms import DEFAULT_SIMULATION_HOTSPOTS
        simulated = DEFAULT_SIMULATION_HOTSPOTS

    df = pd.DataFrame(simulated)
    df.to_csv("live_hotspots.csv", index=False)
    print(f"✅ Injected {len(df)} records into 'live_hotspots.csv'.")
    return df


if __name__ == "__main__":
    import sys
    scenario = sys.argv[1] if len(sys.argv) > 1 else "explosion"
    inject_disaster_scenario(scenario)
    print("🔥 Incident ready! Run 'python pipeline.py' to process.")
