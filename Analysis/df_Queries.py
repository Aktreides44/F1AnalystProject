import pandas as pd
from db_conector import get_db_connection

def get_laps(session_id):
    query = """
    SELECT d.abbreviation, l.lap_number, l.lap_time, l.pit, l.track_status
    FROM laps l
    JOIN drivers d ON l.driver_id = d.driver_id
    WHERE l.session_id = %s
    ORDER BY d.abbreviation, l.lap_number
    """
    conn = get_db_connection()
    df = pd.read_sql(query, conn, params=(session_id,))
    conn.close()
    return df

def get_sectors(session_id):
    query = """
    SELECT d.abbreviation,
           l.sector1_time,
           l.sector2_time,
           l.sector3_time
    FROM laps l
    JOIN drivers d ON l.driver_id = d.driver_id
    WHERE l.session_id = %s AND l.pit = 0
    """
    conn = get_db_connection()
    df = pd.read_sql(query, conn, params=(session_id,))
    conn.close()
    return df

def get_telemetry(session_id):
    query = """
    SELECT d.abbreviation,
           t.speed, t.throttle, t.brake, t.nGear, t.rpm, l.lap_time
    FROM telemetry t
    JOIN laps l
      ON t.session_id = l.session_id
     AND t.driver_id = l.driver_id
     AND t.lap_number = l.lap_number
    JOIN drivers d ON d.driver_id = l.driver_id
    WHERE t.session_id = %s AND l.pit = 0
    """
    conn = get_db_connection()
    df = pd.read_sql(query, conn, params=(session_id,))
    conn.close()
    return df
