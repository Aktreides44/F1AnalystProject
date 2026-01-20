import mysql.connector
from mysql.connector import Error


def get_db_connection():
    """
    Connection to the MySQL database.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="f1_user",
            password="StrongPassword123!",
            database="f1_analysis"
        )

        if connection.is_connected():
            return connection

    except Error as e:
        print(f"Database connection error: {e}")
        return None


def get_cursor(connection):
    """
    Return a cursor
    """
    return connection.cursor(buffered=True)
