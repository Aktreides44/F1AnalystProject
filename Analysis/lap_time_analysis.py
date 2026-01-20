import pandas as pd
import matplotlib.pyplot as plt
from db_conector import get_db_connection

SESSION_ID = 1  # Monza session

# ===============================
# Database query
# ===============================
query = """
SELECT
    d.abbreviation AS driver,
    l.lap_number,
    l.lap_time,
    l.pit,
    l.track_status
FROM laps l
JOIN drivers d ON l.driver_id = d.driver_id
WHERE l.session_id = %s
ORDER BY d.abbreviation, l.lap_number
"""

conn = get_db_connection()
df = pd.read_sql(query, conn, params=(SESSION_ID,))
conn.close()

# Cleaning

df = df.dropna(subset=["lap_time"])

# Identify pit-out laps (lap after pit-in)
df["pit_out"] = df.groupby("driver")["pit"].shift(1) == 1

# Remove pit-in AND pit-out from analysis
clean_df = df[(df["pit"] == 0) & (~df["pit_out"])]

# Lap-to-lap delta (only meaningful on clean data)
clean_df["lap_delta"] = clean_df.groupby("driver")["lap_time"].diff()


# Plotting

plt.figure(figsize=(11, 6))

y_min = clean_df["lap_time"].min() - 1.5  # space for pit dots

for driver in clean_df["driver"].unique():
    d = clean_df[clean_df["driver"] == driver]

    # Main lap time line
    plt.plot(
        d["lap_number"],
        d["lap_time"],
        label=driver,
        linewidth=1.8
    )

    # --- pit stop markers (fun but tasteful) ---
    pit_laps = df[(df["driver"] == driver) & (df["pit"] == 1)]

    plt.scatter(
        pit_laps["lap_number"],
        [y_min] * len(pit_laps),
        s=40,
        marker="o",
        zorder=5
    )

plt.xlabel("Lap Number")
plt.ylabel("Lap Time (seconds)")
plt.title("Lap Time Progression – 2024 Italian Grand Prix\n(Pit-in & Pit-out laps removed)")
plt.legend(title="Driver")
plt.grid(alpha=0.3)
plt.ylim(bottom=y_min)
plt.tight_layout()
plt.show()


print("Lap Time Progression Analysis\n")

for driver in clean_df["driver"].unique():
    d = clean_df[clean_df["driver"] == driver]

    avg_delta = d["lap_delta"].mean()
    trend = "improving" if avg_delta < 0 else "degrading"

    print(
        f"{driver}: Average lap-to-lap change = "
        f"{avg_delta:.3f} s → Pace is {trend}"
    )
