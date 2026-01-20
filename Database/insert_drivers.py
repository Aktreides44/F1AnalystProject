from db_conector import get_db_connection, get_cursor

# List of drivers to insert
drivers = [
    {"driver_number": 16, "abbreviation": "LEC", "full_name": "Charles Leclerc"},
    {"driver_number": 81, "abbreviation": "PIA", "full_name": "Oscar Piastri"},
    {"driver_number": 4,  "abbreviation": "NOR", "full_name": "Lando Norris"},
    {"driver_number": 55, "abbreviation": "SAI", "full_name": "Carlos Sainz"},
    {"driver_number": 44, "abbreviation": "HAM", "full_name": "Lewis Hamilton"}
]

conn = get_db_connection()
cursor = get_cursor(conn)

driver_ids = {}

try:
    insert_query = """
    INSERT INTO drivers (driver_number, abbreviation, full_name)
    VALUES (%s, %s, %s)
    """
    for driver in drivers:
        cursor.execute(insert_query, (driver["driver_number"], driver["abbreviation"], driver["full_name"]))
        conn.commit()
        driver_ids[driver["abbreviation"]] = cursor.lastrowid
        print(f"Inserted {driver['full_name']} with driver_id = {cursor.lastrowid}")

except Exception as e:
    print(f"Error inserting drivers: {e}")

finally:
    cursor.close()
    conn.close()

print("\nAll driver IDs:", driver_ids)
