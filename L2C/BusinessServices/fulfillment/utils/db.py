import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path to repository/
DB_PATH = os.path.join(BASE_DIR, '../data/order_fulfillment.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS fulfillment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                fulfillment_date TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
