import pandas as pd

# Define real coordinate locations in India for testing
# 1st point: Near an oil refinery in Gujarat (Should flag as industrial)
# 2nd point: In a random empty forest area (Should not flag as industrial)
mock_data = {
    'latitude': [22.3072, 24.5000],
    'longitude': [73.1812, 75.5000],
    'acq_date': ['2026-09-07', '2026-09-07'],
    'acq_time': ['1200', '1430'],
    'frp': [120.5, 45.2]  # Fire Radiative Power (Heat strength)
}

df = pd.DataFrame(mock_data)
df.to_csv("live_hotspots.csv", index=False)
print("✅ Setup complete! Local 'live_hotspots.csv' filled with 2 test points.")

