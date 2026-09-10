"""
🧹 SIH26162: Data Cleaning & Preprocessing Utilities
Filters satellite observation noise, deduplicates overlapping orbital passes,
and provides spatial buffering utilities.
"""

import math
import pandas as pd
import numpy as np


def clean_and_filter_firms(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1: Removes low-confidence satellite noise from MODIS/VIIRS detections.
    Retains high/nominal confidence flags and filters sensor anomalies.
    """
    if df.empty or "confidence" not in df.columns:
        return df

    # Keep VIIRS nominal/high flags
    viirs_mask = df["confidence"].astype(str).str.lower().isin(["n", "h", "nominal", "high"])

    # Keep MODIS percentages >= 70% if numeric
    numeric_conf = pd.to_numeric(df["confidence"], errors="coerce")
    modis_mask = numeric_conf >= 70.0

    filtered = df[viirs_mask | modis_mask].copy()
    return filtered if not filtered.empty else df.copy()


def deduplicate_hotspots(df: pd.DataFrame, dist_km: float = 1.0, hours_window: float = 3.0) -> pd.DataFrame:
    """
    Step 2: Merges satellite double-counts (VIIRS + MODIS sensors) within a space-time window.
    """
    if df.empty or "latitude" not in df.columns or "longitude" not in df.columns:
        return df

    date_col = df.get("acq_date", "2026-09-08").astype(str)
    time_col = df.get("acq_time", "0000").astype(str).str.zfill(4)
    
    df = df.copy()
    df["acq_datetime"] = pd.to_datetime(date_col + " " + time_col, format="%Y-%m-%d %H%M", errors="coerce")
    df = df.sort_values(by="acq_datetime").reset_index(drop=True)

    keep_indices = []
    dropped = set()
    coords = df[["latitude", "longitude"]].values

    for i in range(len(df)):
        if i in dropped:
            continue
        keep_indices.append(i)

        # Approximate distance in kilometers
        lat_dist = np.abs(coords[:, 0] - coords[i, 0]) * 111.0
        lon_dist = np.abs(coords[:, 1] - coords[i, 1]) * 111.0 * np.cos(np.radians(coords[i, 0]))
        approx_dist = np.sqrt(lat_dist**2 + lon_dist**2)

        # Time difference in hours
        if "acq_datetime" in df.columns and pd.notna(df.loc[i, "acq_datetime"]):
            time_dist = np.abs((df["acq_datetime"] - df.loc[i, "acq_datetime"]).dt.total_seconds()) / 3600.0
        else:
            time_dist = np.zeros(len(df))

        # Flag matches within space-time proximity
        duplicates = np.where((approx_dist <= dist_km) & (time_dist <= hours_window))[0]
        for idx in duplicates:
            if idx != i:
                dropped.add(idx)

    return df.iloc[keep_indices].copy()


def calculate_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between coordinates in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    return R * (2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)))


if __name__ == "__main__":
    test_df = pd.DataFrame([
        {"latitude": 22.3, "longitude": 73.1, "confidence": "high", "acq_date": "2026-09-08", "acq_time": "1200"},
        {"latitude": 22.301, "longitude": 73.101, "confidence": "high", "acq_date": "2026-09-08", "acq_time": "1210"},
        {"latitude": 24.5, "longitude": 75.5, "confidence": "low", "acq_date": "2026-09-08", "acq_time": "1400"}
    ])
    cleaned = clean_and_filter_firms(test_df)
    deduped = deduplicate_hotspots(cleaned)
    print(f"Original: {len(test_df)} -> Cleaned: {len(cleaned)} -> Deduplicated: {len(deduped)}")
