import mysql.connector
from seed import connect_to_prodev

def stream_users():
    connection = connect_to_prodev()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_data")
            for row in cursor:
                yield row
            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            print(f"Error streaming data: {err}")
