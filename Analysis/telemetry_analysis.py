import pandas as pd
import matplotlib.pyplot as plt
from db_conector import get_db_connection

# ===============================
# Configuration
# ===============================
SESSION_ID = 1        # Italian GP Race
DRIVER_ID = 2         # Leclerc
EARLY_LAPS = 15
MIN_SPEED = 50        # remove pit-lane noise
BIN_SIZE = 50         # meters (for speed profile)

# ===============================
# Load data from database
# ===============================
query = """
SELECT
    t.speed,
    t.throttle,
    t.brake,
    t.gear,
    t.distance,
    l.lap_time,
    l.lap_number
FROM telemetry t
JOIN laps l
  ON t.session_id = l.session_id
 AND t.driver_id = l.driver_id
 AND t.lap_number = l.lap_number
WHERE l.session_id = %s
  AND l.driver_id = %s
  AND l.pit = 0
  AND l.lap_time IS NOT NULL
"""

conn = get_db_connection()
df = pd.read_sql(query, conn, params=(SESSION_ID, DRIVER_ID))
conn.close()


# Cleaning

df = df.dropna()
df = df[df["speed"] > MIN_SPEED]

# ===============================
# Split early / late race
# ===============================
early_df = df[df["lap_number"] <= EARLY_LAPS]
late_df  = df[df["lap_number"] > EARLY_LAPS]

# ===============================
# Pearson Correlation Analysis
# ===============================
variables = ["speed", "throttle", "brake", "gear"]

early_corr = {}
late_corr = {}

for var in variables:
    early_corr[var] = early_df[var].corr(early_df["lap_time"], method="pearson")
    late_corr[var]  = late_df[var].corr(late_df["lap_time"], method="pearson")

corr_df = pd.DataFrame({
    "Early Race": early_corr,
    "Late Race": late_corr
})

print("\nTelemetry ↔ Lap Time (Pearson Correlation)\n")
print(corr_df)

# Correlation Bar Plot
corr_df.plot(
    kind="bar",
    figsize=(10, 6),
    width=0.7
)

plt.axhline(0)
plt.ylabel("Pearson Correlation with Lap Time")
plt.title("Telemetry Influence on Lap Time\nEarly vs Late Race")
plt.xticks(rotation=0)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()


# Speed vs Distance Profile

early_df["dist_bin"] = (early_df["distance"] // BIN_SIZE) * BIN_SIZE
late_df["dist_bin"]  = (late_df["distance"] // BIN_SIZE) * BIN_SIZE

early_speed = early_df.groupby("dist_bin")["speed"].mean()
late_speed  = late_df.groupby("dist_bin")["speed"].mean()

plt.figure(figsize=(10, 5))
plt.plot(early_speed.index, early_speed.values, label="Early Race", linewidth=2)
plt.plot(late_speed.index, late_speed.values, label="Late Race", linewidth=2)

plt.xlabel("Distance (m)")
plt.ylabel("Speed (km/h)")
plt.title("Average Speed Profile\nEarly vs Late Race")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

#brake vs distance
# Speed vs Distance Profile

early_df["dist_bin"] = (early_df["distance"] // BIN_SIZE) * BIN_SIZE
late_df["dist_bin"]  = (late_df["distance"] // BIN_SIZE) * BIN_SIZE

early_brake = early_df.groupby("dist_bin")["brake"].mean()
late_brake  = late_df.groupby("dist_bin")["brake"].mean()

plt.figure(figsize=(10, 5))
plt.plot(early_brake.index, early_brake.values, label="Early Race", linewidth=2)
plt.plot(late_brake.index, late_brake.values, label="Late Race", linewidth=2)

plt.xlabel("Distance (m)")
plt.ylabel("Brake Force %")
plt.title("Average Brake Use Profile\nEarly vs Late Race")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

#Gear Usage
# Speed vs Distance Profile

early_df["dist_bin"] = (early_df["distance"] // BIN_SIZE) * BIN_SIZE
late_df["dist_bin"]  = (late_df["distance"] // BIN_SIZE) * BIN_SIZE

early_gear = early_df.groupby("dist_bin")["gear"].mean()
late_gear  = late_df.groupby("dist_bin")["gear"].mean()

plt.figure(figsize=(10, 5))
plt.plot(early_gear.index, early_gear.values, label="Early Race", linewidth=2)
plt.plot(late_gear.index, late_gear.values, label="Late Race", linewidth=2)

plt.xlabel("Distance (m)")
plt.ylabel("Gear")
plt.title("Gear  Profile\nEarly vs Late Race")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# Interpretation

print("\nInterpretation Summary\n")

for var in variables:
    e = corr_df.loc[var, "Early Race"]
    l = corr_df.loc[var, "Late Race"]

    trend = "stronger" if abs(l) > abs(e) else "weaker"

    print(
        f"{var.capitalize():>8}: correlation becomes {trend} "
        f"({e:.3f} → {l:.3f})"
    )
