import mysql.connector
from seed import connect_to_prodev

def stream_user_ages():
    connection = connect_to_prodev()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT age FROM user_data")
            for row in cursor:
                yield row['age']
            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            print(f"Error streaming ages: {err}")

def calculate_average_age():
    total_age = 0
    count = 0
    for age in stream_user_ages():
        total_age += age
        count += 1
    average_age = total_age / count if count > 0 else 0
    print(f"Average age of users: {average_age:.2f}")

if __name__ == "__main__":
    calculate_average_age()
