import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path to repository/
DB_PATH = os.path.join(BASE_DIR, '../data/dispute_resolution.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS dispute (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dispute_number TEXT NOT NULL,
            order_number TEXT NOT NULL,
            description TEXT,
            resolution_status TEXT
        )
    ''')
    conn.commit()
    conn.close()
