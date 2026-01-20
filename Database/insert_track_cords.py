import fastf1
import pandas as pd
from db_conector import get_db_connection, get_cursor
import os

# ===============================
# Configuration
# ===============================
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

YEAR = 2024
GP_NAME = "Italian Grand Prix"
SESSION_TYPE = "R"
TRACK_ID = 1  # Identifier for Monza in your track_coords table

# ===============================
# Load session
# ===============================
session = fastf1.get_session(YEAR, GP_NAME, SESSION_TYPE)
session.load()  # loads laps

# ===============================
# Extract track coordinates
# ===============================
# Take telemetry from first driver as reference
first_driver = session.drivers[0]
telemetry = session.laps.pick_driver(first_driver).get_telemetry()

# Build DataFrame of distance + X/Y coordinates
track_df = telemetry[['Distance', 'X', 'Y']].drop_duplicates().reset_index(drop=True)
track_df['track_id'] = TRACK_ID

# ===============================
# Insert into MySQL
# ===============================
conn = get_db_connection()
cursor = get_cursor(conn)

insert_query = """
INSERT IGNORE INTO track_coords (track_id, distance, x, y)
VALUES (%s, %s, %s, %s)
"""

try:
    for _, row in track_df.iterrows():
        cursor.execute(insert_query, (row['track_id'], row['Distance'], row['X'], row['Y']))
    conn.commit()
    print(f"Track coordinates for '{GP_NAME}' inserted successfully ({len(track_df)} points).")
except Exception as e:
    print(f"Error inserting track coordinates: {e}")
finally:
    cursor.close()
    conn.close()
