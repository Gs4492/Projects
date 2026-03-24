import sqlite3

DB_NAME = "players.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # allows dict-like access
    return conn