import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path to repository/
DB_PATH = os.path.join(BASE_DIR, '../data/invoicing.db')


# Database connection function
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS invoice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            amount REAL,
            status TEXT,
            issue_date TEXT
        )
    ''')
    conn.commit()
    conn.close()
