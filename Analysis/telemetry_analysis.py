import pandas as pd
import matplotlib.pyplot as plt
from db_conector import get_db_connection

# ===============================
# Configuration
# ===============================
SESSION_ID = 1        # Italian GP Race
DRIVER_ID = 1         # Leclerc
EARLY_LAP_NUMBER = 5  # Pick one early lap
TRACK_ID = 1          # Your track ID
SHIFT_BACK = 320      # meters to shift telemetry backward along the track

# ===============================
# Load telemetry and track coordinates
# ===============================
conn = get_db_connection()

# Telemetry for one lap
query_tel = """
SELECT distance, speed, throttle, brake, gear
FROM telemetry
WHERE session_id = %s
  AND driver_id = %s
  AND lap_number = %s
ORDER BY distance
"""
telemetry = pd.read_sql(query_tel, conn, params=(SESSION_ID, DRIVER_ID, EARLY_LAP_NUMBER))

# Track coordinates
query_track = """
SELECT distance, x, y
FROM track_coords
WHERE track_id = %s
ORDER BY distance
"""
track = pd.read_sql(query_track, conn, params=(TRACK_ID,))
conn.close()

# ===============================
# Map telemetry to track coordinates
# ===============================
def map_to_track(distances, track_df, shift=0):
    x_mapped = []
    y_mapped = []
    for d in distances:
        d_shifted = max(d - shift, 0)  # avoid negative distances
        idx = (track_df['distance'] - d_shifted).abs().idxmin()
        x_mapped.append(track_df.loc[idx, 'x'])
        y_mapped.append(track_df.loc[idx, 'y'])
    return x_mapped, y_mapped

telemetry['x'], telemetry['y'] = map_to_track(telemetry['distance'], track, shift=SHIFT_BACK)

# ===============================
# Plot function for telemetry variable
# ===============================
def plot_telemetry(var, cmap, label):
    plt.figure(figsize=(10, 8))
    sc = plt.scatter(telemetry['x'], telemetry['y'], c=telemetry[var], cmap=cmap, s=15)
    plt.colorbar(sc, label=label)
    plt.title(f"Leclerc – Lap {EARLY_LAP_NUMBER} {label} Map\n2024 Italian GP")
    plt.axis('equal')
    plt.xlabel("Track X")
    plt.ylabel("Track Y")
    plt.tight_layout()
    plt.show()

# ===============================
# Plot all telemetry variables
# ===============================
plot_telemetry('speed', 'viridis', 'Speed (km/h)')
plot_telemetry('throttle', 'plasma', 'Throttle (%)')
plot_telemetry('brake', 'inferno', 'Brake (%)')
plot_telemetry('gear', 'cool', 'Gear')
