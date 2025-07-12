import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path to repository/
DB_PATH = os.path.join(BASE_DIR, '../data/order_management.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """This function will initialize the database and create necessary tables."""
    conn = get_db_connection()  # Get the DB connection
    cursor = conn.cursor()  # Create a cursor object

    # Create the orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            customer_name TEXT,
            order_date TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Order Management Database initialized.")
