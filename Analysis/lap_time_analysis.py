import pandas as pd
import matplotlib.pyplot as plt
from db_conector import get_db_connection


SESSION_ID = 1  # Monza session

# ---------- database query ----------
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

# cleaning
df = df.dropna(subset=["lap_time"])


df["lap_delta"] = df.groupby("driver")["lap_time"].diff()

# Plotting line graph
plt.figure(figsize=(10, 6))

for driver in df["driver"].unique():
    d = df[(df["driver"] == driver)&(df["pit"] == 0)]

    plt.plot(
        d["lap_number"],
        d["lap_time"],
        label=driver,
        linewidth=1.8
    )

    # Highlight pit laps
    pit_laps = d[d["pit"] == 1]
    plt.scatter(
        pit_laps["lap_number"],
        pit_laps["lap_time"],
        color="red",
        zorder=5
    )

plt.xlabel("Lap Number")
plt.ylabel("Lap Time (seconds)")
plt.title("Lap Time Progression – 2024 Italian Grand Prix")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# ---------- interpretation ----------
print("Lap Time Progression Analysis\n")

for driver in df["driver"].unique():
    d = df[(df["driver"] == driver) & (df["pit"] == 0)]

    avg_delta = d["lap_delta"].mean()
    trend = "improving" if avg_delta < 0 else "degrading"

    print(
        f"{driver}: Average lap-to-lap change = "
        f"{avg_delta:.3f} s → Pace is {trend}"
    )
