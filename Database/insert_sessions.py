import fastf1
import os

from db_conector import *
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

year = 2024
gp_name= "Italian Grand Prix"
session_type = "R"

session = fastf1.get_session(year, gp_name, session_type)
session.load()

#Converting date into a string format
session_date = session.date.strftime("%Y-%m-%d") if session.date else None

conn = get_db_connection()
cursor = get_cursor(conn)

try:
    insert_query = """
    INSERT INTO sessions (year, grand_prix, session_type, date)
    VALUES ( %s, %s, %s, %s)
    """
    cursor.execute(insert_query, ( year, gp_name, session_type, session_date))
    conn.commit()
    session_id = cursor.lastrowid
    print(f"Session '{session_id}' inserted successfully.")
except Exception as e:
    print(f"Error inserting session: {e}")
finally:
    cursor.close()
    conn.close()
