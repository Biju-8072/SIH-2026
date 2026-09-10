"""
🚨 SIH26162 - Stage 5: Multi-Channel Emergency Alert Dispatcher
Transmits instant high-priority emergency notifications via:
  1. macOS Native Desktop Notifications with audible siren alarm.
  2. Terminal high-visibility emergency dispatch logs.
"""

import os
import platform
import subprocess
import pandas as pd


def dispatch_emergency_alerts(alerts_file: str = "time_series_validated_alerts.csv") -> int:
    """
    Scans validated alert logs for CRITICAL DISASTER emergencies and dispatches sirens.
    Returns the number of critical disasters dispatched.
    """
    if not os.path.exists(alerts_file):
        print(f"⚠️ Alert log file '{alerts_file}' not found. Run pipeline first.")
        return 0

    df = pd.read_csv(alerts_file)
    
    # Filter critical emergency events
    if "is_emergency" in df.columns:
        disasters = df[df["is_emergency"] == True]
    elif "Risk Priority Tag" in df.columns:
        disasters = df[df["Risk Priority Tag"].str.contains("CRITICAL", case=False, na=False)]
    else:
        disasters = pd.DataFrame()

    if disasters.empty:
        print("✅ Alert Dispatcher: All industrial facilities within safe baseline parameters. No alarms dispatched.")
        return 0

    print(f"\n🚨 [CRITICAL ALERT DISPATCHER] Intercepted {len(disasters)} uncontained structural disasters!\n")

    for idx, row in disasters.iterrows():
        lat = row.get("latitude") or row.get("Lat")
        lon = row.get("longitude") or row.get("Lon")
        frp = row.get("frp") or row.get("Radiative Power (FRP)")
        facility = row.get("facility_name") or "Industrial Zone"
        analysis = row.get("analysis") or row.get("System Analysis", "Uncontained Fire Outbreak")

        title_text = "🚨 SIH ALPHA-RED DISASTER ALERT"
        msg_text = f"CRITICAL FIRE at {facility} (Lat {lat}, Lon {lon}). Thermal Output: {frp} MW!"

        # Print formatted terminal card
        print("=" * 65)
        print(f"🔥 EMERGENCY CODE ALPHA-RED TRIGGERED")
        print(f"🏭 Target Asset: {facility}")
        print(f"📍 GPS Location: Latitude {lat}, Longitude {lon}")
        print(f"💥 Thermal Intensity: {frp} MW")
        print(f"📋 Protocol: Dispatching Hazmat Fleet & Local Fire Division")
        print("=" * 65)

        # On macOS, trigger native desktop notification and audio chime
        if platform.system() == "Darwin":
            try:
                applescript = (
                    f'display notification "{msg_text}" '
                    f'with title "{title_text}" '
                    f'sound name "Submarine"'
                )
                subprocess.run(["osascript", "-e", applescript], check=False)
            except Exception as e:
                print(f"⚠️ Desktop notification fallback: {e}")

        # Audible terminal bell
        print("\a", end="", flush=True)

    return len(disasters)


if __name__ == "__main__":
    count = dispatch_emergency_alerts()
    print(f"Done. Dispatched {count} emergency notifications.")
