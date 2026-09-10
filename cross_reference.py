"""
📐 SIH26162 - Stage 3: Geospatial Proximity & Collision Cross-Referencing
Applies the Haversine spherical distance formula to match satellite thermal
hotspots with industrial facility coordinates within safety buffer perimeters.
"""

import json
import math
import os
import pandas as pd


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two points on the Earth's surface in kilometers.
    Formula:
      a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
      c = 2 * atan2(√a, √(1−a))
      d = R * c (where R = 6371 km)
    """
    R = 6371.0  # Mean radius of the Earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def cross_reference_hotspots(
    hotspots_path: str = "live_hotspots.csv",
    zones_path: str = "industrial_zones.json",
    default_buffer_km: float = 4.0
) -> pd.DataFrame:
    """
    Cross-references satellite hotspots with industrial facilities.
    Identifies if a fire is inside an industrial hazard zone and computes distance.
    """
    if not os.path.exists(hotspots_path):
        raise FileNotFoundError(f"Missing '{hotspots_path}'. Run Stage 1 (fetch_firms.py) first.")
        
    if not os.path.exists(zones_path):
        raise FileNotFoundError(f"Missing '{zones_path}'. Run Stage 2 (fetch_osm.py) first.")

    hotspots_df = pd.read_csv(hotspots_path)
    with open(zones_path, "r") as f:
        zones_data = json.load(f)

    facilities = zones_data.get("elements", [])
    print(f"🔄 Cross-referencing {len(hotspots_df)} hotspots against {len(facilities)} industrial facilities...")

    results = []

    for _, row in hotspots_df.iterrows():
        f_lat = float(row["latitude"])
        f_lon = float(row["longitude"])
        frp = float(row.get("frp", 0.0))
        acq_date = str(row.get("acq_date", "2026-09-08"))
        acq_time = str(row.get("acq_time", "0000"))
        confidence = str(row.get("confidence", "nominal"))

        # Find closest industrial facility
        min_dist = float("inf")
        closest_facility = None

        for fac in facilities:
            e_lat = fac.get("lat")
            e_lon = fac.get("lon")
            if e_lat is None or e_lon is None:
                continue

            dist = haversine_distance_km(f_lat, f_lon, float(e_lat), float(e_lon))
            if dist < min_dist:
                min_dist = dist
                closest_facility = fac

        safe_radius = closest_facility.get("safe_radius_km", default_buffer_km) if closest_facility else default_buffer_km
        in_industrial_zone = (min_dist <= safe_radius)

        facility_name = closest_facility.get("name", "Unknown Facility") if (closest_facility and in_industrial_zone) else "None / Non-Industrial Land"
        facility_id = closest_facility.get("id", "N/A") if (closest_facility and in_industrial_zone) else "N/A"
        has_flare_stacks = closest_facility.get("has_flare_stacks", False) if (closest_facility and in_industrial_zone) else False
        expected_range = closest_facility.get("expected_baseline_frp_mw", [0.0, 50.0]) if (closest_facility and in_industrial_zone) else [0.0, 0.0]

        results.append({
            "latitude": round(f_lat, 5),
            "longitude": round(f_lon, 5),
            "frp": round(frp, 1),
            "confidence": confidence,
            "acq_date": acq_date,
            "acq_time": acq_time,
            "in_industrial_zone": in_industrial_zone,
            "facility_id": facility_id,
            "facility_name": facility_name,
            "distance_km": round(min_dist, 2) if min_dist != float("inf") else 999.0,
            "safe_radius_km": safe_radius,
            "has_flare_stacks": has_flare_stacks,
            "expected_baseline_min_mw": expected_range[0],
            "expected_baseline_max_mw": expected_range[1]
        })

    result_df = pd.DataFrame(results)
    return result_df


if __name__ == "__main__":
    df = cross_reference_hotspots()
    df.to_csv("cross_referenced_hotspots.csv", index=False)
    print(f"✅ Proximity analysis complete. Stored {len(df)} records in 'cross_referenced_hotspots.csv'.")
