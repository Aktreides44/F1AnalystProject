import pandas as pd
import matplotlib.pyplot as plt
from db_conector import get_db_connection

# ===============================
# Configuration
# ===============================
SESSION_ID = 1
DRIVER_IDS = {"LEC": 1, "SAI": 4, "HAM": 5, "NOR": 3, "PIA": 2}

# Tire colors
TIRE_COLORS = {
    "SOFT": "#FF6666",  # red
    "MEDIUM": "#FFCC66",  # yellow
    "HARD": "#FFFFFF"  # white
}

# ===============================
# Load laps
# ===============================
conn = get_db_connection()

query = """
        SELECT d.abbreviation AS driver, \
               l.lap_number, \
               l.lap_time, \
               l.pit, \
               l.tyre_compound
        FROM laps l
                 JOIN drivers d ON l.driver_id = d.driver_id
        WHERE l.session_id = %s
        ORDER BY d.abbreviation, l.lap_number \
        """

df = pd.read_sql(query, conn, params=(SESSION_ID,))
conn.close()

df = df.dropna(subset=["lap_time"])
df["tyre_compound"] = df["tyre_compound"].str.strip().str.upper()  # normalize tire names


# ===============================
# Helper to format lap time in min:sec:ms
# ===============================
def format_lap_time(seconds):
    minutes = int(seconds // 60)
    sec = seconds % 60
    return f"{minutes}:{sec:06.3f}"  # 1:20.345


# ===============================
# Plot per driver
# ===============================
for driver, driver_id in DRIVER_IDS.items():
    d = df[df["driver"] == driver].copy()

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor('black')  # figure background
    ax.set_facecolor('black')  # axes background

    # Plot each tire type
    for tyre, color in TIRE_COLORS.items():
        tyre_laps = d[d["tyre_compound"] == tyre]
        if not tyre_laps.empty:
            ax.plot(
                tyre_laps["lap_number"],
                tyre_laps["lap_time"],
                marker='o',
                linestyle='-',
                color=color,
                label=tyre
            )

    # Vertical lines for pit laps
    pit_laps = d[d["pit"] == 1]
    for lap in pit_laps["lap_number"]:
        ax.axvline(lap, color="grey", linestyle="--", alpha=0.5)

    # Axes & labels
    ax.set_xlabel("Lap Number", color="white")
    ax.set_ylabel("Lap Time (min:sec.ms)", color="white")
    ax.set_title(f"{driver} – Lap Time Progression\n2024 Italian GP", color="white")

    # Set tick labels to white
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    # Convert y-axis to min:sec.ms format
    yticks = ax.get_yticks()
    ax.set_yticklabels([format_lap_time(y) for y in yticks], color='white')

    # Optional: grid in white
    ax.grid(alpha=0.3, color="white")

    ax.legend(facecolor='black', edgecolor='white', labelcolor='white')  # legend matches black bg
    plt.tight_layout()
    plt.show()
