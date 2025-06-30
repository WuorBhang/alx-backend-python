import mysql.connector
from seed import connect_to_prodev

def streamusersinbatches(batchsize):
    """Generator function to fetch rows from user_data table in batches using yield."""
    connection = connect_to_prodev()
    try:
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_data")
            while True:
                rows = cursor.fetchmany(batchsize)
                if not rows:
                    break
                yield rows
            cursor.close()
            connection.close()
        else:
            print("Failed to connect to database")
    except mysql.connector.Error as err:
        print(f"Error streaming batches: {err}")

def batch_processing(batch_size):
    """Process batches from streamusersinbatches and filter users over age 25."""
    for batch in streamusersinbatches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)
