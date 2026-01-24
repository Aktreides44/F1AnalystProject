import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from db_conector import get_db_connection

# ===============================
# Configuration
# ===============================
SESSION_ID = 1  # Italian GP Race

# Define driver colors
DRIVER_COLORS = {
    "LEC": "red",
    "SAI": "red",
    "HAM": "green",
    "NOR": "orange",
    "PIA": "orange"
}

# ===============================
# Load lap times (exclude pit laps)
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
# Remove outliers based on IQR per driver
# ===============================
cleaned = []
for driver in df['driver'].unique():
    laps = df[df['driver'] == driver]['lap_time']
    q1 = laps.quantile(0.25)
    q3 = laps.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    driver_clean = df[(df['driver'] == driver) & (df['lap_time'] >= lower) & (df['lap_time'] <= upper)]
    cleaned.append(driver_clean)

df_clean = pd.concat(cleaned)

# ===============================
# Compute consistency stats
# ===============================
stats = []
for driver in df_clean['driver'].unique():
    laps = df_clean[df_clean['driver'] == driver]['lap_time']
    std_dev = laps.std()
    q1 = laps.quantile(0.25)
    q3 = laps.quantile(0.75)
    iqr = q3 - q1
    stats.append({
        "Driver": driver,
        "Std Dev (s)": std_dev,
        "IQR (s)": iqr
    })

consistency_df = pd.DataFrame(stats).sort_values("Std Dev (s)")
print("\nLap Time Consistency Metrics\n")
print(consistency_df)

# ===============================
# Violin + Swarm Plot
# ===============================
plt.figure(figsize=(10, 6))

sns.violinplot(
    x='driver',
    y='lap_time',
    data=df_clean,
    palette=DRIVER_COLORS,
    inner='quartile',
    cut=0  # avoids showing extended tails beyond data
)

sns.swarmplot(
    x='driver',
    y='lap_time',
    data=df_clean,
    color='k',      # black dots
    size=3,         # small points
    alpha=0.6
)

plt.title("Lap Time Distribution – 2024 Italian Grand Prix (Outliers Removed)")
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
