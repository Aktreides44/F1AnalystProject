from db_conector import get_db_connection, get_cursor

conn = get_db_connection()
if conn:
    cursor = get_cursor(conn)
    cursor.execute("SHOW TABLES;")
    print(cursor.fetchall())
    conn.close()
