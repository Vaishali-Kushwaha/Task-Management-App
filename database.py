import mysql.connector
from mysql.connector import Error
import os

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": "task_management_new"
}


def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            return connection

    except Error as e:
        print("Database connection failed:", e)

    return None


if __name__ == "__main__":
    connection = get_connection()

    if connection:
        print("Database connected successfully!")
        connection.close()
    else:
        print("Database connection failed.")