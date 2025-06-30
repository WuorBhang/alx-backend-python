import mysql.connector
from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    connection = connect_to_prodev()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_data")
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                yield rows
            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            print(f"Error streaming batches: {err}")

def batch_processing(batch_size):
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)
