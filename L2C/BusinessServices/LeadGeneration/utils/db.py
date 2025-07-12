import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path to repository/
DB_PATH = os.path.join(BASE_DIR, '../data/lead_generation.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            source TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
