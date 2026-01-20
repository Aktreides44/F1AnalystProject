import fastf1
import pandas as pd
import os
from db_conector import get_db_connection, get_cursor


def clean(value):
    if pd.isna(value):
        return None
    return value

# ---------- configuration ----------
session_id = 1  # from sessions table
driver_ids = {
    "LEC": 1,
    "PIA": 2,
    "NOR": 3,
    "SAI": 4,
    "HAM": 5
}

year = 2024
gp_name = "Italian Grand Prix"
session_type = "R"

# ---------- load session ----------
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(year, gp_name, session_type)
session.load(telemetry=True)

# ---------- database ----------
conn = get_db_connection()
cursor = get_cursor(conn)

insert_query = """
INSERT INTO telemetry (
    session_id,
    driver_id,
    lap_number,
    sample_index,
    time,
    distance,
    speed,
    throttle,
    brake,
    gear,
    drs,
    rpm
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

try:
    for abbr, driver_id in driver_ids.items():
        laps = session.laps.pick_drivers(abbr)

        for _, lap in laps.iterrows():
            if lap['LapTime'] is None:
                continue  # skip incomplete laps

            tel = lap.get_telemetry()
            rows = []

            for idx, row in tel.iterrows():
                rows.append((
                    session_id,
                    driver_id,
                    int(lap['LapNumber']),
                    int(idx),
                    clean(row['Time'].total_seconds() if row['Time'] is not None else None),
                    clean(row['Distance']),
                    clean(row['Speed']),
                    clean(row['Throttle']),
                    clean(row['Brake']),
                    clean(row['nGear']),
                    clean(row['DRS']),
                    clean(row['RPM'])
                ))

            if rows:
                cursor.executemany(insert_query, rows)

        conn.commit()
        print(f"Telemetry inserted for {abbr}")

except Exception as e:
    print(f"Error inserting telemetry: {e}")

finally:
    cursor.close()
    conn.close()
