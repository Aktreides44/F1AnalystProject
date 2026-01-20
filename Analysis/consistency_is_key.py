import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
from db_conector import get_db_connection

# ===============================
# Configuration
# ===============================
SESSION_ID = 1  # Italian GP Race

# ===============================
# Query lap times
# ===============================
query = """
SELECT
    d.abbreviation AS driver,
    l.lap_time
FROM laps l
JOIN drivers d ON l.driver_id = d.driver_id
WHERE l.session_id = %s
  AND l.pit = 0
  AND l.lap_time IS NOT NULL
"""

conn = get_db_connection()
df = pd.read_sql(query, conn, params=(SESSION_ID,))
conn.close()

# ===============================
# Consistency statistics
# ===============================
stats = []

for driver in df["driver"].unique():
    laps = df[df["driver"] == driver]["lap_time"]

    std_dev = laps.std()
    q1 = laps.quantile(0.25)
    q3 = laps.quantile(0.75)
    iqr = q3 - q1

    stats.append({
        "Driver": driver,
        "Std Dev (s)": std_dev,
        "IQR (s)": iqr
    })

consistency_df = pd.DataFrame(stats)
consistency_df = consistency_df.sort_values("Std Dev (s)")

print("\nLap Time Consistency Metrics\n")
print(consistency_df)

# ===============================
# Visualization: Boxplot
# ===============================
plt.figure(figsize=(10, 6))

df.boxplot(
    column="lap_time",
    by="driver",
    grid=False
)

plt.suptitle("")
plt.title("Lap Time Consistency – 2024 Italian Grand Prix")
plt.xlabel("Driver")
plt.ylabel("Lap Time (seconds)")
plt.tight_layout()
plt.show()

# ===============================
# Interpretation
# ===============================
most_consistent = consistency_df.iloc[0]

print("\nInterpretation Summary\n")
print(
    f"Most consistent driver: {most_consistent['Driver']}\n"
    f"Standard deviation: {most_consistent['Std Dev (s)']:.3f} s\n"
    f"IQR: {most_consistent['IQR (s)']:.3f} s"
)
