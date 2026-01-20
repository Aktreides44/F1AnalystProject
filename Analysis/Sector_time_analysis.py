import pandas as pd
import matplotlib.pyplot as plt
from db_conector import get_db_connection

SESSION_ID = 1  # Monza race

# --- query ---
query = """
SELECT
    d.abbreviation AS driver,
    l.sector1_time,
    l.sector2_time,
    l.sector3_time
FROM laps l
JOIN drivers d ON l.driver_id = d.driver_id
WHERE l.session_id = %s
  AND l.pit = 0
"""

conn = get_db_connection()
df = pd.read_sql(query, conn, params=(SESSION_ID,))
conn.close()

# --- cleaning ---
df = df.dropna()

# --- compute average per driver ---
sector_avg = df.groupby("driver")[["sector1_time", "sector2_time", "sector3_time"]].mean().reset_index()

# --- compute gap to fastest driver per sector (ms) ---
sector_gap = sector_avg.copy()
for s in ["sector1_time", "sector2_time", "sector3_time"]:
    sector_gap[s] = (sector_gap[s] - sector_gap[s].min())   # seconds → milliseconds

# --- plot ---
sector_gap.set_index("driver")[["sector1_time", "sector2_time", "sector3_time"]].plot(
    kind="bar",
    figsize=(12, 6),
    width=0.8
)

plt.ylabel("Gap to Fastest Driver (ms)")
plt.title("Sector Time Gaps – 2024 Italian GP")
plt.xticks(rotation=0)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.show()

# --- print dominant sector ---
sector_spread = {
    "Sector 1": sector_gap["sector1_time"].max(),
    "Sector 2": sector_gap["sector2_time"].max(),
    "Sector 3": sector_gap["sector3_time"].max(),
}
dominant_sector = max(sector_spread, key=sector_spread.get)



print("Sector Time Contribution Analysis\n")
for sector, spread in sector_spread.items():
    print(f"{sector}: max gap = {spread:.3f} s")
print(f"\n➡ Sector with largest performance gap: {dominant_sector}")
