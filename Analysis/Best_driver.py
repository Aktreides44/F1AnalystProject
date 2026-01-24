import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from db_conector import get_db_connection

# ===============================
# Configuration
# ===============================
SESSION_ID = 1  # Race session ID
DRIVERS = {"LEC": "Charles Leclerc", "PIA": "Oscar Piastri"}

DRIVER_COLORS = {
    "Charles Leclerc": "#FF0000",  # red
    "Oscar Piastri": "#FF8800"     # orange
}

TYRE_STYLES = {
    "HARD": "-",    # solid
    "MEDIUM": "--", # dashed
    "SOFT": ":"     # optional
}

# ===============================
# Load laps
# ===============================
conn = get_db_connection()
query = """
SELECT d.full_name AS driver,
       l.lap_number,
       l.lap_time,
       l.pit,
       l.tyre_compound,
       l.stint_number
FROM laps l
JOIN drivers d ON l.driver_id = d.driver_id
WHERE l.session_id = %s
AND (d.full_name = %s OR d.full_name = %s)
ORDER BY l.lap_number, d.full_name
"""
df = pd.read_sql(query, conn, params=(SESSION_ID, DRIVERS["LEC"], DRIVERS["PIA"]))
conn.close()

df = df.dropna(subset=["lap_time"])
df["tyre_compound"] = df["tyre_compound"].str.strip().str.upper()

# ===============================
# Helper to format lap time
# ===============================
def format_lap_time(seconds):
    minutes = int(seconds // 60)
    sec = seconds % 60
    return f"{minutes}:{sec:06.3f}"

# ===============================
# Remove pit-out laps for line plot
# ===============================
df_line = df[df.groupby(['driver', 'stint_number'])['lap_number'].transform('min') != df['lap_number']]

# ===============================
# Line plot: lap times with tyre & pit info
# ===============================
plt.figure(figsize=(14, 6))

for driver_name in DRIVERS.values():
    driver_df = df_line[df_line["driver"] == driver_name]

    for tyre, style in TYRE_STYLES.items():
        tyre_laps = driver_df[driver_df["tyre_compound"] == tyre]
        if not tyre_laps.empty:
            plt.plot(
                tyre_laps["lap_number"],
                tyre_laps["lap_time"],
                linestyle=style,
                color=DRIVER_COLORS[driver_name],
                marker='o',
                markersize=4,
                label=f"{driver_name} – {tyre}"
            )

    # pit stops as small dots
    pits = driver_df[driver_df["pit"] == 1]
    plt.scatter(
        pits["lap_number"],
        pits["lap_time"],
        s=40,  # smaller dots
        facecolor='white',
        edgecolor=DRIVER_COLORS[driver_name],
        linewidth=1.5,
        zorder=5
    )

plt.xlabel("Lap Number", color='black')
plt.ylabel("Lap Time (min:sec.ms)", color='black')
plt.title("2024 Italian GP – Leclerc vs Piastri Strategy Battle", color='black')

# y-axis formatting using FuncFormatter
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: format_lap_time(y)))

plt.grid(alpha=0.3)
plt.legend(bbox_to_anchor=(1.05,1), loc='upper left')
plt.tight_layout()
plt.show()

# ===============================
# Cumulative race time per driver
# ===============================
df_cumm = df.copy()

# Remove pit-out laps if desired
df_cumm = df_cumm[df_cumm.groupby(['driver', 'stint_number'])['lap_number'].transform('min') != df_cumm['lap_number']]

# Compute cumulative time
df_cumm['cum_time'] = df_cumm.groupby('driver')['lap_time'].cumsum()

# ===============================
# Plot cumulative race time
# ===============================
plt.figure(figsize=(14, 6))

for driver_name in DRIVERS.values():
    driver_df = df_cumm[df_cumm['driver'] == driver_name]
    plt.plot(
        driver_df['lap_number'],
        driver_df['cum_time'],
        color=DRIVER_COLORS[driver_name],
        linestyle='-',
        marker='o',
        markersize=4,
        label=driver_name
    )

plt.xlabel("Lap Number")
plt.ylabel("Cumulative Race Time (s)")
plt.title("2024 Italian GP – Cumulative Race Time: Leclerc vs Piastri")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

