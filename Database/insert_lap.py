import fastf1
import pandas as pd
import os
from db_conector import get_db_connection, get_cursor


# to clean the Nan values put by panda and convert it to None
def clean(value):
    """Convert NaN to None so MySQL accepts it as NULL."""
    if pd.isna(value):
        return None
    return value



session_id = 1  # use session_id =1
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
session.load()

# ---------- database ----------
conn = get_db_connection()
cursor = get_cursor(conn)

insert_query = """
               INSERT INTO laps (session_id, \
                                 driver_id, \
                                 lap_number, \
                                 lap_time, \
                                 sector1_time, \
                                 sector2_time, \
                                 sector3_time, \
                                 pit, \
                                 tyre_compound, \
                                 stint_number, \
                                 track_status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
               """

try:
    for abbreviation, driver_id in driver_ids.items():
        laps = session.laps.pick_drivers([abbreviation])

        for _, lap in laps.iterrows():
            pit_flag = 1 if pd.notna(lap['PitInTime']) else 0

            cursor.execute(insert_query, (
                session_id,
                driver_id,
                int(lap['LapNumber']),
                clean(lap['LapTime'].total_seconds() if lap['LapTime'] else None),
                clean(lap['Sector1Time'].total_seconds() if lap['Sector1Time'] else None),
                clean(lap['Sector2Time'].total_seconds() if lap['Sector2Time'] else None),
                clean(lap['Sector3Time'].total_seconds() if lap['Sector3Time'] else None),
                pit_flag,
                clean(lap['Compound']),
                clean(lap['Stint']),
                clean(lap['TrackStatus'])
            ))

    conn.commit()
    print("Laps inserted successfully.")

except Exception as e:
    print(f" Error inserting laps: {e}")

finally:
    cursor.close()
    conn.close()
