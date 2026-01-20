import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from db_conector import get_db_connection

SESSION_ID = 1

# ===============================
# Load combined lap + sector data
# ===============================
lap_query = """
SELECT
    d.abbreviation AS driver,
    l.lap_number,
    l.lap_time,
    l.sector1_time,
    l.sector2_time,
    l.sector3_time
FROM laps l
JOIN drivers d ON l.driver_id = d.driver_id
WHERE l.session_id = %s
  AND l.pit = 0
  AND l.lap_time IS NOT NULL
"""

conn = get_db_connection()
laps_df = pd.read_sql(lap_query, conn, params=(SESSION_ID,))
conn.close()

# ===============================
# Overall performance metrics
# ===============================
summary = laps_df.groupby("driver").agg(
    avg_lap_time=("lap_time", "mean"),
    std_lap_time=("lap_time", "std"),
    avg_s1=("sector1_time", "mean"),
    avg_s2=("sector2_time", "mean"),
    avg_s3=("sector3_time", "mean"),
).reset_index()

summary["total_sector_time"] = (
    summary["avg_s1"] + summary["avg_s2"] + summary["avg_s3"]
)

summary = summary.sort_values("avg_lap_time")

print("\nOverall Driver Performance Summary\n")
print(summary[[
    "driver",
    "avg_lap_time",
    "std_lap_time",
    "total_sector_time"
]])

# ===============================
# 1️⃣ Lap time trend (pace evolution)
# ===============================
plt.figure(figsize=(10, 5))

for driver in laps_df["driver"].unique():
    d = laps_df[laps_df["driver"] == driver]
    plt.plot(d["lap_number"], d["lap_time"], label=driver, linewidth=1.5)

plt.xlabel("Lap Number")
plt.ylabel("Lap Time (s)")
plt.title("Lap Time Trend – Race Pace Evolution")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# ===============================
# 2️⃣ Sector contribution comparison
# ===============================
sector_df = summary.set_index("driver")[["avg_s1", "avg_s2", "avg_s3"]]

sector_df.plot(
    kind="bar",
    stacked=True,
    figsize=(10, 6)
)

plt.ylabel("Average Sector Time (s)")
plt.title("Sector Time Contribution by Driver")
plt.xticks(rotation=0)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# ===============================
# 3️⃣ Telemetry correlation heatmap
# ===============================
telemetry_query = """
SELECT
    d.abbreviation AS driver,
    t.speed,
    t.throttle,
    t.brake,
    t.gear,
    l.lap_time
FROM telemetry t
JOIN laps l
  ON t.session_id = l.session_id
 AND t.driver_id = l.driver_id
 AND t.lap_number = l.lap_number
JOIN drivers d ON d.driver_id = t.driver_id
WHERE t.session_id = %s
  AND l.pit = 0
  AND l.lap_time IS NOT NULL
"""

conn = get_db_connection()
tele_df = pd.read_sql(telemetry_query, conn, params=(SESSION_ID,))
conn.close()

tele_df = tele_df.dropna()

corr = tele_df[["speed", "throttle", "brake", "gear", "lap_time"]].corr(method="pearson")

plt.figure(figsize=(7, 5))
sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("Telemetry ↔ Lap Time Correlation (Pearson)")
plt.tight_layout()
plt.show()

# ===============================
# Interpretation summary
# ===============================
best_driver = summary.iloc[0]

print("\nFinal Interpretation\n")
print(
    f"Fastest overall driver: {best_driver['driver']}\n"
    f"Average lap time: {best_driver['avg_lap_time']:.3f} s\n"
    f"Consistency (std dev): {best_driver['std_lap_time']:.3f} s\n"
)

print(
    "Sector analysis shows where lap time is gained, while telemetry correlations\n"
    "indicate that speed and throttle usage are the strongest linear contributors\n"
    "to lap performance, particularly in a low-interruption race such as Monza."
)
